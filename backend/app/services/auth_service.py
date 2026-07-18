"""Business operations for password authentication and session rotation."""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

from app.config.settings import settings
from app.core.exceptions import AuthenticationError, ValidationError
from app.core.security import create_access_token, get_password_hash, verify_password
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.repositories.user_settings_repository import UserSettingsRepository
from app.services import EventDispatcher


class AuthService:
    def __init__(
        self,
        users: UserRepository,
        refresh_tokens: RefreshTokenRepository,
        user_settings: UserSettingsRepository,
        events: EventDispatcher,
    ) -> None:
        self._users = users
        self._refresh_tokens = refresh_tokens
        self._user_settings = user_settings
        self._events = events

    async def register(self, email: str, password: str, full_name: str) -> UUID:
        if await self._users.get_by_email(email) is not None:
            raise ValidationError("An account already exists for this email")
        self._validate_password(password)
        user = await self._users.create(
            {
                "email": email,
                "password_hash": get_password_hash(password),
                "full_name": full_name,
            }
        )
        await self._user_settings.create(user.id, {})
        await self._events.publish(
            "user.created", {"user_id": str(user.id), "email": user.email}
        )
        return user.id

    async def login(self, email: str, password: str) -> dict[str, object]:
        user = await self._users.get_by_email(email)
        if (
            user is None
            or not user.is_active
            or not verify_password(password, user.password_hash)
        ):
            raise AuthenticationError("Invalid email or password")
        return await self._issue_tokens(user.id)

    async def refresh(self, refresh_token: str) -> dict[str, object]:
        token = await self._refresh_tokens.get_by_hash(
            self._hash_refresh_token(refresh_token)
        )
        if token is None or token.revoked or token.expires_at <= datetime.now(UTC):
            raise AuthenticationError("Refresh token is invalid or expired")
        await self._refresh_tokens.revoke(token.id)
        result = await self._issue_tokens(token.user_id)
        await self._events.publish("auth.refreshed", {"user_id": str(token.user_id)})
        return result

    async def logout(self, refresh_token: str) -> None:
        token = await self._refresh_tokens.get_by_hash(
            self._hash_refresh_token(refresh_token)
        )
        if token is not None:
            await self._refresh_tokens.revoke(token.id)
            await self._events.publish("auth.logout", {"user_id": str(token.user_id)})

    async def logout_all(self, user_id: UUID) -> int:
        return await self._refresh_tokens.revoke_all_for_user(user_id)

    async def _issue_tokens(self, user_id: UUID) -> dict[str, object]:
        raw_refresh = secrets.token_urlsafe(64)
        await self._refresh_tokens.create(
            user_id,
            self._hash_refresh_token(raw_refresh),
            datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days),
        )
        await self._events.publish("auth.login", {"user_id": str(user_id)})
        return {
            "access_token": create_access_token(str(user_id)),
            "refresh_token": raw_refresh,
            "expires_in": settings.access_token_expire_minutes * 60,
        }

    @staticmethod
    def _hash_refresh_token(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    @staticmethod
    def _validate_password(password: str) -> None:
        if len(password) < 12 or not all(
            (
                any(c.isupper() for c in password),
                any(c.islower() for c in password),
                any(c.isdigit() for c in password),
                any(not c.isalnum() for c in password),
            )
        ):
            raise ValidationError(
                "Password needs 12+ characters with upper, lower, number, and symbol"
            )
