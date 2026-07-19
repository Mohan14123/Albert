"""Notification event handlers."""

import logging

from app.events.consumer import BaseConsumer
from app.events.exchanges import NOTIFICATION_EXCHANGE
from app.events.schemas import DomainEvent

logger = logging.getLogger(__name__)


class NotificationConsumer(BaseConsumer):
    def __init__(self) -> None:
        super().__init__(
            queue_name="notification.delivery.queue",
            routing_key="#",
            exchange_name=NOTIFICATION_EXCHANGE,
        )

    async def on_message(self, event: DomainEvent) -> None:
        logger.info("Notification delivery placeholder for event: %s", event.event_name)
        from app.database.engine import async_session
        from app.repositories.event_store_repository import EventStoreRepository

        async with async_session() as session:
            repo = EventStoreRepository(session)
            await repo.create(
                event_name=event.event_name,
                routing_key=self.routing_key,
                payload=event.payload,
            )
