import logging
from collections.abc import Sequence
from uuid import UUID

from app.database.models.memory import Memory
from app.repositories.memory_repository import MemoryRepository
from app.services import EventDispatcher

logger = logging.getLogger(__name__)


class MemoryService:
    def __init__(self, memories: MemoryRepository, events: EventDispatcher) -> None:
        self._memories = memories
        self._events = events

    async def store_memory(
        self, user_id: UUID, content: str, category: str | None = None
    ) -> Memory:
        memory = await self._memories.create(user_id, content, category)
        await self._events.publish(
            "memory.stored",
            {
                "user_id": str(user_id),
                "memory_id": str(memory.id),
                "category": category,
            },
        )
        return memory

    async def get_all_for_user(self, user_id: UUID) -> Sequence[Memory]:
        return await self._memories.get_all_for_user(user_id)

    async def search_memories(self, user_id: UUID, query: str) -> Sequence[Memory]:
        # For now, we fetch all and do simple string matching.
        # In a real app, use pgvector, Qdrant, or basic SQL ILIKE.
        all_memories = await self._memories.get_all_for_user(user_id)
        query = query.lower()
        return [m for m in all_memories if query in m.content.lower()]

    async def compress_memories(self, user_id: UUID) -> None:
        # Stub for background memory compression task
        logger.info(f"Compressing memories for user {user_id}")

    async def cleanup_expired(self) -> None:
        # Stub for expired memory cleanup
        logger.info("Cleaning up expired memories")
