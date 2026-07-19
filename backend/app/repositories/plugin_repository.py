from collections.abc import Sequence
from typing import Any
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.plugin_registry import PluginRegistry


class PluginRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        name: str,
        version: str,
        description: str | None = None,
        capabilities: dict[str, Any] | None = None,
    ) -> PluginRegistry:
        plugin = PluginRegistry(
            name=name,
            version=version,
            description=description,
            capabilities=capabilities or {},
        )
        self._session.add(plugin)
        await self._session.commit()
        await self._session.refresh(plugin)
        return plugin

    async def get_by_name(self, name: str) -> PluginRegistry | None:
        stmt = select(PluginRegistry).where(PluginRegistry.name == name)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self) -> Sequence[PluginRegistry]:
        stmt = select(PluginRegistry)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def update_status(self, plugin_id: UUID, status: str) -> None:
        stmt = (
            update(PluginRegistry)
            .where(PluginRegistry.id == plugin_id)
            .values(status=status)
        )
        await self._session.execute(stmt)
        await self._session.commit()
