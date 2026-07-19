from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.memory import Memory


class MemoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self, user_id: UUID, content: str, category: str | None = None
    ) -> Memory:
        memory = Memory(user_id=user_id, content=content, category=category)
        self._session.add(memory)
        await self._session.flush()
        await self._session.refresh(memory)
        return memory

    async def get_by_id(self, memory_id: UUID) -> Memory | None:
        return await self._session.get(Memory, memory_id)

    async def get_all_for_user(self, user_id: UUID) -> Sequence[Memory]:
        stmt = (
            select(Memory)
            .where(Memory.user_id == user_id)
            .order_by(Memory.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()
