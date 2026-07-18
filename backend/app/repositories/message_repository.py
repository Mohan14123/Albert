"""Persistence operations for chat messages."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.message import Message


class MessageRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, chat_id: UUID, role: str, content: str, status: str) -> Message:
        message = Message(chat_id=chat_id, role=role, content=content, status=status)
        self._session.add(message)
        await self._session.flush()
        return message

    async def get_by_chat(self, chat_id: UUID, page: int, limit: int) -> tuple[list[Message], int]:
        total = await self._session.scalar(
            select(func.count()).select_from(Message).where(Message.chat_id == chat_id)
        )
        items = (await self._session.scalars(
            select(Message).where(Message.chat_id == chat_id)
            .order_by(Message.created_at.asc()).offset((page - 1) * limit).limit(limit)
        )).all()
        return list(items), total or 0

    async def update_status(self, message_id: UUID, status: str) -> Message | None:
        message = await self._session.get(Message, message_id)
        if message is None:
            return None
        message.status = status
        await self._session.flush()
        return message
