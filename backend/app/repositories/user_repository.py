"""Persistence operations for users."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.user import User


class UserRepository:
    """Provides async, model-focused user data access."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, user_data: dict[str, object]) -> User:
        user = User(**user_data)
        self._session.add(user)
        await self._session.flush()
        return user

    async def get_by_id(self, user_id: UUID) -> User | None:
        statement = select(User).where(User.id == user_id, User.deleted_at.is_(None))
        return await self._session.scalar(statement)

    async def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email, User.deleted_at.is_(None))
        return await self._session.scalar(statement)

    async def update(self, user_id: UUID, data: dict[str, object]) -> User | None:
        user = await self.get_by_id(user_id)
        if user is None:
            return None
        for field, value in data.items():
            setattr(user, field, value)
        await self._session.flush()
        return user

    async def soft_delete(self, user_id: UUID) -> User | None:
        user = await self.get_by_id(user_id)
        if user is None:
            return None
        user.deleted_at = datetime.now(UTC)
        await self._session.flush()
        return user
