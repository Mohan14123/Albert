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
        pass
