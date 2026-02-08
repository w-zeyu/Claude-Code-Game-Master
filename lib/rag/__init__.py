"""
RAG-based Document Extraction Module

This module provides semantic/embedding-based extraction using local vectorization.
It's designed to be siloed and modular - can be excluded without affecting core functionality.

Install dependencies: pip install -e ".[rag]" or uv pip install -e ".[rag]"
"""

# Check for RAG dependencies availability
RAG_AVAILABLE = False
_MISSING_DEPS = []

try:
    import sentence_transformers
except ImportError:
    _MISSING_DEPS.append("sentence-transformers")

try:
    import chromadb
except ImportError:
    _MISSING_DEPS.append("chromadb")

# Only mark available if all deps present
RAG_AVAILABLE = len(_MISSING_DEPS) == 0


def check_rag_available() -> bool:
    """Check if RAG dependencies are installed."""
    return RAG_AVAILABLE


def get_missing_deps() -> list:
    """Get list of missing dependencies."""
    return _MISSING_DEPS.copy()


def require_rag():
    """Raise an error if RAG deps are not available."""
    if not RAG_AVAILABLE:
        missing = ", ".join(_MISSING_DEPS)
        raise ImportError(
            f"RAG dependencies not installed: {missing}\n"
            f"Install with: pip install -e '.[rag]' or uv pip install -e '.[rag]'"
        )


# Conditional exports - only import classes if deps available
if RAG_AVAILABLE:
    from lib.rag.embedder import LocalEmbedder
    from lib.rag.vector_store import CampaignVectorStore
    from lib.rag.semantic_chunker import SemanticChunker
    from lib.rag.rag_extractor import RAGExtractor
    from lib.rag.extraction_queries import EXTRACTION_QUERIES, get_queries_for_type
    from lib.rag.quote_extractor import QuoteExtractor

    __all__ = [
        'RAG_AVAILABLE',
        'check_rag_available',
        'get_missing_deps',
        'require_rag',
        'LocalEmbedder',
        'CampaignVectorStore',
        'SemanticChunker',
        'RAGExtractor',
        'EXTRACTION_QUERIES',
        'get_queries_for_type',
        'QuoteExtractor',
    ]
else:
    __all__ = [
        'RAG_AVAILABLE',
        'check_rag_available',
        'get_missing_deps',
        'require_rag',
    ]
