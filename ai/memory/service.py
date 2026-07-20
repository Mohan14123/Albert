from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Sequence
from ..orchestrator.contracts import MemoryRetriever, MemoryWriter
from ..orchestrator.models import ChatRequest, AssistantResponse
from .models import MemoryRecord
from .compressor import MemoryCompressor

logger = logging.getLogger(__name__)


class InMemoryMemoryAdapter(MemoryRetriever, MemoryWriter):
    """An in-memory stub implementation of MemoryRetriever and MemoryWriter.

    Features:
    - Keyword relevance and recency scoring for memory ranking.
    - Automatic memory compression & deduplication before returning.
    """

    def __init__(self, compressor: MemoryCompressor | None = None) -> None:
        """Initialize the storage adapter with baseline mock data and compressor."""
        self._logger = logging.getLogger(__name__)
        self._compressor = compressor or MemoryCompressor()
        self._records: list[MemoryRecord] = [
            MemoryRecord(
                id=str(uuid.uuid4()),
                type="preference",
                content="User prefers concise answers",
                created_at=datetime.now(timezone.utc),
            ),
            MemoryRecord(
                id=str(uuid.uuid4()),
                type="fact",
                content="User lives in Munich, Germany",
                created_at=datetime.now(timezone.utc),
            ),
        ]

    @staticmethod
    def _extract_words(text: str) -> set[str]:
        """Extract alphanumeric words from text, lowercased and stripped of punctuation."""
        import re

        return set(re.findall(r"\w+", text.lower()))

    def _score_memory(self, record: MemoryRecord, query_words: set[str]) -> float:
        """Calculate a composite relevance + recency score for a memory record."""
        rec_words = self._extract_words(record.content)

        # Calculate stem match count (e.g. 'live' matching 'lives')
        match_count = 0
        for qw in query_words:
            if any(qw in rw or rw in qw for rw in rec_words):
                match_count += 1

        # Keyword relevance score (0.0 to 1.0)
        relevance_score = (match_count / len(query_words)) if query_words else 0.0

        # Recency score (newer records get slightly higher score)
        age_hours = (
            datetime.now(timezone.utc) - record.created_at
        ).total_seconds() / 3600.0
        recency_score = 1.0 / (1.0 + (age_hours / 24.0))

        # Weight: 80% relevance, 20% recency
        return (0.8 * relevance_score) + (0.2 * recency_score)

    async def retrieve(self, request: ChatRequest, plan: Any) -> Sequence[MemoryRecord]:
        """Retrieve and rank memory records relevant to the current query."""
        query_words = self._extract_words(request.message)

        # First compress records to eliminate duplicate info
        compressed_records = self._compressor.compress(self._records)

        # Score records
        scored: list[tuple[float, MemoryRecord]] = []
        for rec in compressed_records:
            score = self._score_memory(rec, query_words)
            rec_words = self._extract_words(rec.content)
            # Include records with match or return all records if score > 0 or query is generic
            has_match = any(
                qw in rw or rw in qw for qw in query_words for rw in rec_words
            )
            if has_match or len(query_words) < 3 or not query_words:
                scored.append((score, rec))

        # Sort descending by score
        scored.sort(key=lambda item: item[0], reverse=True)
        return [rec for _, rec in scored]

    async def save(
        self, request: ChatRequest, response: AssistantResponse, plan: Any
    ) -> None:
        """Parse response and user message to extract and persist new memory nodes."""
        msg_lower = request.message.lower()
        if "remember that" in msg_lower:
            idx = msg_lower.index("remember that") + len("remember that")
            content = request.message[idx:].strip()
            if content:
                new_record = MemoryRecord(
                    id=str(uuid.uuid4()),
                    type="fact",
                    content=content,
                    created_at=datetime.now(timezone.utc),
                )
                self._records.append(new_record)
                self._logger.info("Saved new memory record: %s", content[:50])
