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
        pass
