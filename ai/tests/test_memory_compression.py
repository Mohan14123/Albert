"""Tests for Memory Compression and Memory Ranking."""

import asyncio
import sys
import os
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from ai.memory.compressor import MemoryCompressor
from ai.memory.models import MemoryRecord
from ai.memory.service import InMemoryMemoryAdapter
from ai.orchestrator.models import ChatRequest


# -- Test 1: Deduplication via MemoryCompressor -----------------------------

def test_memory_deduplication():
    """Verify that duplicate content is compressed and metadata merged."""
    compressor = MemoryCompressor()

    now = datetime.now(timezone.utc)
    records = [
        MemoryRecord(id="1", type="fact", content="User likes Python", created_at=now, metadata={"source": "chat1"}),
        MemoryRecord(id="2", type="fact", content="User likes Python ", created_at=now, metadata={"source": "chat2"}),
        MemoryRecord(id="3", type="preference", content="User prefers dark theme", created_at=now),
    ]

    compressed = compressor.compress(records)
    assert len(compressed) == 2, f"Expected 2 unique records, got {len(compressed)}"

    python_rec = [r for r in compressed if "Python" in r.content][0]
    assert python_rec.metadata.get("merged_count") == 2, "Merged count should be 2"
    print("  PASSED: Memory deduplication and metadata merging")


# -- Test 2: Memory ranking by relevance and recency ------------------------

async def test_memory_scoring_and_ranking():
    """Verify that memories are scored and ranked properly."""
    adapter = InMemoryMemoryAdapter()

    # Add a fresh record
    now = datetime.now(timezone.utc)
    old_time = now - timedelta(days=10)

    adapter._records.append(
        MemoryRecord(id="old", type="fact", content="User lives in Paris", created_at=old_time)
    )
    adapter._records.append(
        MemoryRecord(id="new", type="fact", content="User currently lives in Munich", created_at=now)
    )

    request = ChatRequest(conversation_id="c1", user_id="u1", message="Where do I live?")
    retrieved = await adapter.retrieve(request, None)

    assert len(retrieved) > 0, "Should retrieve matching memories"
    # Munich record should rank higher than Paris because of recency
    munich_indices = [i for i, r in enumerate(retrieved) if "Munich" in r.content]
    paris_indices = [i for i, r in enumerate(retrieved) if "Paris" in r.content]

    if munich_indices and paris_indices:
        assert munich_indices[0] < paris_indices[0], "Munich record should rank higher due to recency"

    print("  PASSED: Memory scoring and ranking")


# -- Main -------------------------------------------------------------------

async def main():
    print("--- Memory Compression Tests ---")
    test_memory_deduplication()

    print("\n--- Memory Ranking Tests ---")
    await test_memory_scoring_and_ranking()

    print("\n All memory compression tests passed!")


if __name__ == "__main__":
    asyncio.run(main())
