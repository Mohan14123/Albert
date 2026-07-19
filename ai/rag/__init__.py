"""RAG (Retrieval-Augmented Generation) package.

Provides document chunking, embedding generation, vector store search, and prompt injection.
"""

from .models import DocumentChunk, SearchResult, RAGConfig
from .chunker import TextChunker
from .embeddings import EmbeddingClient, MockEmbeddingClient, cosine_similarity
from .vector_store import InMemoryVectorStore
from .service import RAGService

__all__ = [
    "DocumentChunk",
    "SearchResult",
    "RAGConfig",
    "TextChunker",
    "EmbeddingClient",
    "MockEmbeddingClient",
    "cosine_similarity",
    "InMemoryVectorStore",
    "RAGService",
]
