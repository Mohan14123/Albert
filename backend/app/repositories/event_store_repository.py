from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.event_store import EventStore


class EventStoreRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        event_name: str,
        routing_key: str | None = None,
        payload: dict[str, Any] | None = None,
        aggregate_id: UUID | None = None,
    ) -> EventStore:
        event = EventStore(
            event_name=event_name,
            routing_key=routing_key,
            payload=payload or {},
            aggregate_id=aggregate_id,
        )
        self._session.add(event)
        await self._session.flush()
        await self._session.refresh(event)
        return event

    async def mark_processed(self, event_id: UUID) -> None:
        event = await self._session.get(EventStore, event_id)
        if event:
            event.processed_at = datetime.now(UTC)
            await self._session.flush()
