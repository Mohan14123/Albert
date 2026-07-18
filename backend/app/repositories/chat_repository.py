"""Persistence operations for chats."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.chat import Chat


class ChatRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, user_id: UUID, title: str) -> Chat:
        chat = Chat(user_id=user_id, title=title)
        self._session.add(chat)
        await self._session.flush()
        return chat

    async def get_by_id(self, chat_id: UUID) -> Chat | None:
        return await self._session.scalar(
            select(Chat).where(Chat.id == chat_id, Chat.deleted_at.is_(None))
        )

    async def get_by_user(
        self, user_id: UUID, page: int, limit: int
    ) -> tuple[list[Chat], int]:
        filters = (Chat.user_id == user_id, Chat.deleted_at.is_(None))
        total = await self._session.scalar(
            select(func.count()).select_from(Chat).where(*filters)
        )
        items = (
            await self._session.scalars(
                select(Chat)
                .where(*filters)
                .order_by(Chat.updated_at.desc())
                .offset((page - 1) * limit)
                .limit(limit)
            )
        ).all()
        return list(items), total or 0

    async def update(self, chat_id: UUID, data: dict[str, object]) -> Chat | None:
        chat = await self.get_by_id(chat_id)
        if chat is None:
            return None
        for field, value in data.items():
            setattr(chat, field, value)
        await self._session.flush()
        return chat

    async def archive(self, chat_id: UUID) -> Chat | None:
        return await self.update(chat_id, {"archived": True})

    async def soft_delete(self, chat_id: UUID) -> Chat | None:
        chat = await self.get_by_id(chat_id)
        if chat is None:
            return None
        chat.deleted_at = datetime.now(UTC)
        await self._session.flush()
        return chat
