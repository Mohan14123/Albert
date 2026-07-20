from __future__ import annotations

import uuid
from .models import DocumentChunk


class TextChunker:
    """Utilities for splitting raw text documents into searchable chunks."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50) -> None:
        self.chunk_size = max(50, chunk_size)
        self.chunk_overlap = max(0, min(chunk_overlap, self.chunk_size - 10))

    def chunk_text(self, text: str, document_id: str = "doc") -> list[DocumentChunk]:
        """Split text into fixed character chunks with sliding overlap."""
        if not text.strip():
            return []

        chunks: list[DocumentChunk] = []
        start = 0
        text_len = len(text)
        idx = 0

        while start < text_len:
            end = min(start + self.chunk_size, text_len)
            chunk_content = text[start:end].strip()

            if chunk_content:
                chunks.append(
                    DocumentChunk(
                        chunk_id=f"{document_id}_chunk_{idx}_{uuid.uuid4().hex[:6]}",
                        document_id=document_id,
                        content=chunk_content,
                        index=idx,
                        metadata={"start_char": start, "end_char": end},
                    )
                )
                idx += 1

            if end == text_len:
                break
            start += self.chunk_size - self.chunk_overlap

        return chunks
