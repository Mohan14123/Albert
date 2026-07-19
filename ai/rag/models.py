from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class DocumentChunk:
    """A segment of text extracted from a larger document."""
    chunk_id: str
    document_id: str
    content: str
    index: int
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=_utc_now)


@dataclass(frozen=True)
class SearchResult:
    """A scored document chunk retrieved from vector search."""
    chunk: DocumentChunk
    score: float


@dataclass(frozen=True)
class RAGConfig:
    """Configuration options for RAG indexing and search."""
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k: int = 3
    similarity_threshold: float = 0.1
