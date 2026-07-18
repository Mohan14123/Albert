"""Persistence operations for per-user settings."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.user_settings import UserSettings


class UserSettingsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, user_id: UUID, defaults: dict[str, object]) -> UserSettings:
        settings = UserSettings(user_id=user_id, **defaults)
        self._session.add(settings)
        await self._session.flush()
        return settings

    async def get_by_user(self, user_id: UUID) -> UserSettings | None:
        return await self._session.scalar(select(UserSettings).where(UserSettings.user_id == user_id))

    async def update(self, user_id: UUID, data: dict[str, object]) -> UserSettings | None:
        settings = await self.get_by_user(user_id)
        if settings is None:
            return None
        for field, value in data.items():
            setattr(settings, field, value)
        await self._session.flush()
        return settings
