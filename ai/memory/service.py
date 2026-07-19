from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Sequence
from ..orchestrator.contracts import MemoryRetriever, MemoryWriter
from ..orchestrator.models import ChatRequest, AssistantResponse
from .models import MemoryRecord


class InMemoryMemoryAdapter(MemoryRetriever, MemoryWriter):
    """An in-memory stub implementation of MemoryRetriever and MemoryWriter.

    This serves as a developer contract adapter to test the pipeline
    without setting up external databases or search indices.
    """

    def __init__(self) -> None:
        """Initialize the storage adapter with some baseline mock data."""
        self._logger = logging.getLogger(__name__)
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

    async def retrieve(self, request: ChatRequest, plan: Any) -> Sequence[MemoryRecord]:
        """Retrieve memory records relevant to the current query."""
        # Simple match: if any word of user query is in the memory content, return it.
        # This keeps the mock query logic dynamic and easy to test.
        query_words = set(request.message.lower().split())
        matched = []
        for rec in self._records:
            rec_words = set(rec.content.lower().split())
            if query_words.intersection(rec_words) or len(query_words) < 3:
                matched.append(rec)
        return matched

    async def save(
        self, request: ChatRequest, response: AssistantResponse, plan: Any
    ) -> None:
        """Parse response and user message to extract and persist new memory nodes."""
        msg_lower = request.message.lower()
        if "remember that" in msg_lower:
            # Use the lowered index to find the split point in the original message
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
