"""Persistence operations for encrypted OAuth tokens."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.oauth_token import OAuthToken


class OAuthTokenRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self, integration_id: UUID, encrypted_access: str, encrypted_refresh: str | None, expires_at: datetime | None
    ) -> OAuthToken:
        token = OAuthToken(
            integration_id=integration_id, access_token=encrypted_access,
            refresh_token=encrypted_refresh, expires_at=expires_at,
        )
        self._session.add(token)
        await self._session.flush()
        return token

    async def get_by_integration(self, integration_id: UUID) -> OAuthToken | None:
        return await self._session.scalar(
            select(OAuthToken).where(OAuthToken.integration_id == integration_id)
        )

    async def update(self, token_id: UUID, data: dict[str, object]) -> OAuthToken | None:
        token = await self._session.get(OAuthToken, token_id)
        if token is None:
            return None
        for field, value in data.items():
            setattr(token, field, value)
        await self._session.flush()
        return token

    async def delete(self, token_id: UUID) -> bool:
        token = await self._session.get(OAuthToken, token_id)
        if token is None:
            return False
        await self._session.delete(token)
        await self._session.flush()
        return True
