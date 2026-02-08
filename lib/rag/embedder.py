#!/usr/bin/env python3
"""
Local Embedder for RAG-based Document Extraction

Uses sentence-transformers with all-MiniLM-L6-v2 (22MB, fast) for local vectorization.
"""

import os
import sys
import warnings
import logging
from typing import List, Optional
import numpy as np

# Suppress HuggingFace and transformers warnings
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
warnings.filterwarnings("ignore", category=FutureWarning)
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)


class LocalEmbedder:
    """Wrapper for sentence-transformers embeddings."""

    DEFAULT_MODEL = "all-MiniLM-L6-v2"

    def __init__(self, model_name: str = None):
        """
        Initialize the local embedder.

        Args:
            model_name: The sentence-transformers model to use.
                       Defaults to all-MiniLM-L6-v2 (22MB, fast, good quality).
        """
        self.model_name = model_name or self.DEFAULT_MODEL
        self._model = None

    @staticmethod
    def is_available() -> bool:
        """Check if sentence-transformers is available."""
        try:
            import sentence_transformers
            return True
        except ImportError:
            return False

    def _ensure_model(self):
        """Lazy-load the model on first use (suppressing noisy output)."""
        if self._model is None:
            # Suppress stderr during model loading (progress bars, warnings)
            import io
            old_stderr = sys.stderr
            sys.stderr = io.StringIO()
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
            finally:
                sys.stderr = old_stderr

    def embed(self, text: str) -> np.ndarray:
        """
        Embed a single text string.

        Args:
            text: The text to embed.

        Returns:
            Embedding vector as numpy array.
        """
        self._ensure_model()
        return self._model.encode(text, convert_to_numpy=True)

    def embed_batch(self, texts: List[str], batch_size: int = 32, show_progress: bool = False) -> np.ndarray:
        """
        Embed multiple texts efficiently in batches.

        Args:
            texts: List of texts to embed.
            batch_size: Number of texts per batch.
            show_progress: Whether to show progress bar.

        Returns:
            Array of embedding vectors (n_texts x embedding_dim).
        """
        self._ensure_model()
        return self._model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True
        )

    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector.
            embedding2: Second embedding vector.

        Returns:
            Cosine similarity score (0-1).
        """
        # Normalize vectors
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(np.dot(embedding1, embedding2) / (norm1 * norm2))

    def similarities(self, query_embedding: np.ndarray, corpus_embeddings: np.ndarray) -> np.ndarray:
        """
        Calculate cosine similarities between a query and corpus of embeddings.

        Args:
            query_embedding: Single query embedding vector.
            corpus_embeddings: Array of corpus embeddings (n_docs x embedding_dim).

        Returns:
            Array of similarity scores.
        """
        # Normalize query
        query_norm = query_embedding / np.linalg.norm(query_embedding)

        # Normalize corpus (row-wise)
        corpus_norms = np.linalg.norm(corpus_embeddings, axis=1, keepdims=True)
        corpus_norms = np.where(corpus_norms == 0, 1, corpus_norms)  # Avoid div by zero
        corpus_normalized = corpus_embeddings / corpus_norms

        # Compute similarities
        return np.dot(corpus_normalized, query_norm)

    @property
    def embedding_dimension(self) -> int:
        """Get the embedding dimension for the current model."""
        self._ensure_model()
        return self._model.get_sentence_embedding_dimension()


def main():
    """Test the embedder."""
    if not LocalEmbedder.is_available():
        print("sentence-transformers not installed!")
        print("Install with: pip install sentence-transformers")
        return

    embedder = LocalEmbedder()
    print(f"Model: {embedder.model_name}")

    # Test single embedding
    text = "The old wizard lives in a tower by the sea."
    embedding = embedder.embed(text)
    print(f"Embedding shape: {embedding.shape}")
    print(f"Embedding dimension: {embedder.embedding_dimension}")

    # Test batch embedding
    texts = [
        "A knight in shining armor enters the tavern.",
        "The dark dungeon holds many treasures.",
        "Cast fireball at the goblin horde.",
    ]
    embeddings = embedder.embed_batch(texts)
    print(f"Batch embeddings shape: {embeddings.shape}")

    # Test similarity
    query = embedder.embed("A warrior walks into an inn.")
    sims = embedder.similarities(query, embeddings)
    print(f"Similarities to 'A warrior walks into an inn': {sims}")


if __name__ == "__main__":
    main()
