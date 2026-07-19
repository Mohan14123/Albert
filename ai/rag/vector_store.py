from __future__ import annotations

import logging
from typing import Sequence
from .models import DocumentChunk, SearchResult
from .embeddings import EmbeddingClient, MockEmbeddingClient, cosine_similarity

logger = logging.getLogger(__name__)


class InMemoryVectorStore:
    """In-memory vector store indexing chunks and executing similarity search."""

    def __init__(self, embedding_client: EmbeddingClient | None = None) -> None:
        self._embedding_client = embedding_client or MockEmbeddingClient()
        self._chunks: dict[str, DocumentChunk] = {}
        self._vectors: dict[str, list[float]] = {}

    async def add_chunks(self, chunks: Sequence[DocumentChunk]) -> None:
        """Index document chunks with calculated embeddings."""
        if not chunks:
            return
        texts = [c.content for c in chunks]
        embeddings = await self._embedding_client.embed_batch(texts)

        for chunk, emb in zip(chunks, embeddings):
            self._chunks[chunk.chunk_id] = chunk
            self._vectors[chunk.chunk_id] = emb

        logger.info("Indexed %d document chunks in vector store", len(chunks))

    async def search(self, query: str, top_k: int = 3, threshold: float = 0.0) -> list[SearchResult]:
        """Perform similarity search for query and return ranked top-K results."""
        if not self._chunks:
            return []

        query_vec = await self._embedding_client.embed_text(query)
        scored: list[SearchResult] = []

        for chunk_id, chunk in self._chunks.items():
            emb = self._vectors[chunk_id]
            score = cosine_similarity(query_vec, emb)
            if score >= threshold:
                scored.append(SearchResult(chunk=chunk, score=score))

        scored.sort(key=lambda r: r.score, reverse=True)
        return scored[:top_k]

    def clear(self) -> None:
        """Remove all indexed chunks."""
        self._chunks.clear()
        self._vectors.clear()
