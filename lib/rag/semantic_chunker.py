#!/usr/bin/env python3
"""
Semantic Chunker for RAG-based Extraction

Pre-computes query embeddings and scores chunks against categories
via cosine similarity with threshold-based assignment.
"""

from typing import Dict, List, Tuple, Optional
import numpy as np

from lib.rag.embedder import LocalEmbedder
from lib.rag.extraction_queries import EXTRACTION_QUERIES, get_all_types


class SemanticChunker:
    """Categorize text chunks using semantic similarity."""

    DEFAULT_THRESHOLD = 0.35  # Minimum similarity to assign a category

    def __init__(
        self,
        embedder: Optional[LocalEmbedder] = None,
        threshold: float = None
    ):
        """
        Initialize the semantic chunker.

        Args:
            embedder: LocalEmbedder instance. Creates one if not provided.
            threshold: Minimum similarity score to assign a category.
        """
        self.embedder = embedder or LocalEmbedder()
        self.threshold = threshold or self.DEFAULT_THRESHOLD
        self._query_embeddings: Dict[str, np.ndarray] = {}
        self._category_embeddings: Dict[str, np.ndarray] = {}
        self._initialized = False

    def _ensure_initialized(self):
        """Lazy-initialize query embeddings on first use."""
        if self._initialized:
            return

        print("Initializing semantic chunker (computing query embeddings)...")

        # Embed all queries for each category
        for content_type, queries in EXTRACTION_QUERIES.items():
            # Embed each individual query
            embeddings = self.embedder.embed_batch(queries)
            self._query_embeddings[content_type] = embeddings

            # Also compute a centroid (average) embedding for the category
            self._category_embeddings[content_type] = embeddings.mean(axis=0)

        self._initialized = True
        print(f"  Initialized {len(self._query_embeddings)} categories")

    def score_chunk(self, chunk_text: str) -> Dict[str, float]:
        """
        Score a chunk against all content type categories.

        Args:
            chunk_text: The text to score.

        Returns:
            Dict mapping content type to similarity score.
        """
        self._ensure_initialized()

        # Embed the chunk
        chunk_embedding = self.embedder.embed(chunk_text)

        scores = {}
        for content_type, category_embedding in self._category_embeddings.items():
            # Compute similarity to category centroid
            similarity = self.embedder.similarity(chunk_embedding, category_embedding)
            scores[content_type] = float(similarity)

        return scores

    def score_chunk_detailed(self, chunk_text: str) -> Dict[str, Dict]:
        """
        Score a chunk with detailed per-query similarities.

        Args:
            chunk_text: The text to score.

        Returns:
            Dict with 'scores' (category -> score) and 'details' (category -> query scores)
        """
        self._ensure_initialized()

        chunk_embedding = self.embedder.embed(chunk_text)

        scores = {}
        details = {}

        for content_type, query_embeddings in self._query_embeddings.items():
            # Compute similarity to each query in the category
            sims = self.embedder.similarities(chunk_embedding, query_embeddings)

            # Use max similarity as the category score
            max_sim = float(sims.max())
            avg_sim = float(sims.mean())

            scores[content_type] = max_sim
            details[content_type] = {
                "max_similarity": max_sim,
                "avg_similarity": avg_sim,
                "query_similarities": sims.tolist()
            }

        return {"scores": scores, "details": details}

    def categorize_chunk(
        self,
        chunk_text: str,
        allow_multiple: bool = False
    ) -> List[Tuple[str, float]]:
        """
        Categorize a chunk into content types.

        Args:
            chunk_text: The text to categorize.
            allow_multiple: If True, return all categories above threshold.
                           If False, return only the best match.

        Returns:
            List of (category, score) tuples, sorted by score descending.
        """
        scores = self.score_chunk(chunk_text)

        if allow_multiple:
            # Return all categories above threshold
            matches = [
                (cat, score) for cat, score in scores.items()
                if score >= self.threshold
            ]
        else:
            # Return only the best match if above threshold
            best_cat = max(scores, key=scores.get)
            if scores[best_cat] >= self.threshold:
                matches = [(best_cat, scores[best_cat])]
            else:
                matches = [("general", scores[best_cat])]

        # Sort by score descending
        return sorted(matches, key=lambda x: x[1], reverse=True)

    def categorize_chunks(
        self,
        chunks: List[str],
        show_progress: bool = False
    ) -> Dict[str, List[Dict]]:
        """
        Categorize multiple chunks into content type buckets.

        Args:
            chunks: List of text chunks to categorize.
            show_progress: Whether to show progress.

        Returns:
            Dict mapping category to list of chunk dicts with:
            - 'index': Original index in input list
            - 'text': The chunk text
            - 'confidence': Category similarity score
            - 'all_scores': Scores for all categories
        """
        self._ensure_initialized()

        # Embed all chunks in batch
        if show_progress:
            print(f"Embedding {len(chunks)} chunks...")
        chunk_embeddings = self.embedder.embed_batch(chunks, show_progress=show_progress)

        # Initialize result buckets
        categorized = {cat: [] for cat in get_all_types()}
        categorized["general"] = []

        # Score and categorize each chunk
        for idx, (chunk_text, chunk_emb) in enumerate(zip(chunks, chunk_embeddings)):
            # Score against all categories
            scores = {}
            for content_type, category_embedding in self._category_embeddings.items():
                similarity = self.embedder.similarity(chunk_emb, category_embedding)
                scores[content_type] = float(similarity)

            # Find best category
            best_cat = max(scores, key=scores.get)
            confidence = scores[best_cat]

            # Assign to category or general
            if confidence >= self.threshold:
                category = best_cat
            else:
                category = "general"

            categorized[category].append({
                "index": idx,
                "text": chunk_text,
                "confidence": confidence,
                "all_scores": scores
            })

        return categorized

    def get_stats(self) -> Dict:
        """Get chunker statistics."""
        self._ensure_initialized()

        return {
            "threshold": self.threshold,
            "categories": list(self._category_embeddings.keys()),
            "queries_per_category": {
                cat: len(embeddings)
                for cat, embeddings in self._query_embeddings.items()
            },
            "embedding_dimension": self.embedder.embedding_dimension
        }


def main():
    """Test the semantic chunker."""
    from lib.rag.embedder import LocalEmbedder

    if not LocalEmbedder.is_available():
        print("sentence-transformers not installed!")
        return

    chunker = SemanticChunker()

    # Test chunks
    test_chunks = [
        "The old wizard Gandalf has white robes and a long staff. He speaks in riddles and offers guidance to travelers.",
        "The dungeon entrance is a dark cave mouth in the mountainside. Stairs descend into the depths below.",
        "A +2 longsword of flame dealing an extra 1d6 fire damage on hit. Requires attunement by a good-aligned creature.",
        "The villagers speak of a dragon terrorizing the countryside. Whoever slays it will receive 5000 gold pieces.",
        "The weather is pleasant today with a light breeze from the west.",
    ]

    print("Testing Semantic Chunker")
    print("=" * 50)

    for i, chunk in enumerate(test_chunks):
        print(f"\nChunk {i + 1}: {chunk[:60]}...")
        categories = chunker.categorize_chunk(chunk)
        for cat, score in categories:
            print(f"  -> {cat}: {score:.3f}")

    print("\n" + "=" * 50)
    print("\nBatch categorization:")
    categorized = chunker.categorize_chunks(test_chunks, show_progress=True)

    for cat, items in categorized.items():
        if items:
            print(f"\n{cat.upper()} ({len(items)} chunks):")
            for item in items:
                print(f"  - Chunk {item['index']}: {item['confidence']:.3f}")


if __name__ == "__main__":
    main()
