from __future__ import annotations

import logging
from typing import Sequence
from .models import RAGConfig, SearchResult
from .chunker import TextChunker
from .vector_store import InMemoryVectorStore

logger = logging.getLogger(__name__)


class RAGService:
    """High-level service coordinating document ingestion, chunk retrieval, and context injection."""

    def __init__(
        self,
        vector_store: InMemoryVectorStore | None = None,
        config: RAGConfig | None = None,
    ) -> None:
        self._config = config or RAGConfig()
        self._vector_store = vector_store or InMemoryVectorStore()
        self._chunker = TextChunker(
            chunk_size=self._config.chunk_size,
            chunk_overlap=self._config.chunk_overlap,
        )

    async def ingest_document(self, document_id: str, content: str) -> int:
        """Chunk raw document content and index into vector store. Return count of created chunks."""
        chunks = self._chunker.chunk_text(content, document_id=document_id)
        await self._vector_store.add_chunks(chunks)
        return len(chunks)

    async def retrieve_relevant_context(self, query: str) -> list[SearchResult]:
        """Search vector store for relevant document chunks matching query."""
        return await self._vector_store.search(
            query=query,
            top_k=self._config.top_k,
            threshold=self._config.similarity_threshold,
        )

    def format_context_injection(self, results: Sequence[SearchResult]) -> str:
        """Format retrieved search results for injection into model prompt."""
        if not results:
            return ""

        output = ["\n--- Retrieved Knowledge Documents (RAG) ---"]
        for res in results:
            output.append(f"Document [{res.chunk.document_id}]:")
            output.append(f"{res.chunk.content}")
            output.append("---")
        return "\n".join(output)
