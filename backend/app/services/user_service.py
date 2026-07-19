"""Business operations for user profiles and preferences."""

from uuid import UUID

from app.core.exceptions import NotFoundError
from app.repositories.user_repository import UserRepository
from app.repositories.user_settings_repository import UserSettingsRepository
from app.services import EventDispatcher


class UserService:
    """Coordinates profile and settings repositories without HTTP concerns."""

    def __init__(
        self,
        users: UserRepository,
        settings: UserSettingsRepository,
        events: EventDispatcher,
    ) -> None:
        self._users = users
        self._settings = settings
        self._events = events

    async def get_profile(self, user_id: UUID):
        user = await self._users.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found")
        return user

    async def update_profile(self, user_id: UUID, data: dict[str, object]):
        user = await self._users.update(user_id, data)
        if user is None:
            raise NotFoundError("User not found")
        await self._events.publish("user.updated", {"user_id": str(user.id)})
        return user

    async def get_settings(self, user_id: UUID):
        settings = await self._settings.get_by_user(user_id)
        if settings is None:
            raise NotFoundError("User settings not found")
        return settings

    async def update_settings(self, user_id: UUID, data: dict[str, object]):
        settings = await self._settings.update(user_id, data)
        if settings is None:
            raise NotFoundError("User settings not found")
        return settings
