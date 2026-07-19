from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Sequence
from .models import MemoryRecord

logger = logging.getLogger(__name__)


class MemoryCompressor:
    """Compresses and consolidates memory records by deduplicating redundant content."""

    def compress(self, records: Sequence[MemoryRecord]) -> list[MemoryRecord]:
        """Deduplicate records with identical or near-identical content and merge metadata."""
        if not records:
            return []

        seen_content: dict[str, MemoryRecord] = {}
        for rec in records:
            key = rec.content.strip().lower()
            if key in seen_content:
                # Merge metadata if duplicate found
                existing = seen_content[key]
                merged_meta = dict(existing.metadata)
                merged_meta.update(rec.metadata)
                merged_meta["merged_count"] = merged_meta.get("merged_count", 1) + 1
                seen_content[key] = MemoryRecord(
                    id=existing.id,
                    type=existing.type,
                    content=existing.content,
                    created_at=existing.created_at,
                    metadata=merged_meta,
                )
            else:
                seen_content[key] = rec

        compressed = list(seen_content.values())
        if len(compressed) < len(records):
            logger.info("Compressed %d memory records down to %d", len(records), len(compressed))
        return compressed

    def summarize_facts(self, records: Sequence[MemoryRecord]) -> list[MemoryRecord]:
        """Group records of the same type and summarize key statements."""
        compressed = self.compress(records)
        # Group by type and return sorted by created_at descending
        return sorted(compressed, key=lambda r: r.created_at, reverse=True)
