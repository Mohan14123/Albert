"""Persistence operations for user integrations."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.integration import Integration


class IntegrationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, user_id: UUID, provider: str) -> Integration:
        integration = Integration(
            user_id=user_id, provider=provider, status="disconnected", connected_at=datetime.now(timezone.utc)
        )
        self._session.add(integration)
        await self._session.flush()
        return integration

    async def get_by_user(self, user_id: UUID) -> list[Integration]:
        return list((await self._session.scalars(
            select(Integration).where(Integration.user_id == user_id).order_by(Integration.provider)
        )).all())

    async def get_by_user_and_provider(self, user_id: UUID, provider: str) -> Integration | None:
        return await self._session.scalar(select(Integration).where(
            Integration.user_id == user_id, Integration.provider == provider
        ))

    async def update_status(self, integration_id: UUID, status: str) -> Integration | None:
        integration = await self._session.get(Integration, integration_id)
        if integration is None:
            return None
        integration.status = status
        await self._session.flush()
        return integration

    async def update_last_sync(self, integration_id: UUID) -> Integration | None:
        integration = await self._session.get(Integration, integration_id)
        if integration is None:
            return None
        integration.last_sync = datetime.now(timezone.utc)
        await self._session.flush()
        return integration

    async def delete(self, integration_id: UUID) -> bool:
        integration = await self._session.get(Integration, integration_id)
        if integration is None:
            return False
        await self._session.delete(integration)
        await self._session.flush()
        return True
