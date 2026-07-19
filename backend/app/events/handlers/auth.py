"""Auth event handlers."""

import logging

from app.events.consumer import BaseConsumer
from app.events.schemas import DomainEvent

logger = logging.getLogger(__name__)


class AuthConsumer(BaseConsumer):
    def __init__(self) -> None:
        super().__init__(queue_name="auth.audit.queue", routing_key="auth.#")

    async def on_message(self, event: DomainEvent) -> None:
        logger.info(
            "Audit log: Auth event %s received: %s", event.event_name, event.event_id
        )
        from app.database.engine import async_session
        from app.repositories.event_store_repository import EventStoreRepository

        async with async_session() as session:
            repo = EventStoreRepository(session)
            await repo.create(
                event_name=event.event_name,
                routing_key=self.routing_key,
                payload=event.payload,
            )
            from uuid import UUID

            from app.services.audit_service import AuditService

            user_id_raw = event.payload.get("user_id")
            if user_id_raw:
                user_id = (
                    UUID(user_id_raw) if isinstance(user_id_raw, str) else user_id_raw
                )
                await AuditService.log_action(
                    action=event.event_name,
                    user_id=user_id,
                    metadata=event.payload,
                )
