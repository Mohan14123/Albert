"""Gmail webhook handler."""

import logging
from typing import Any

from app.events.publisher import EventPublisher

logger = logging.getLogger(__name__)


class GmailWebhook:
    @staticmethod
    async def handle(payload: dict[str, Any]) -> None:
        """Handle incoming Pub/Sub notifications from Gmail."""
        logger.info("Gmail webhook received payload: %s", payload)

        # In a real app, verify the webhook signature and extract the user/historyId
        # For now we emit an event
        publisher = EventPublisher()
        await publisher.connect()
        await publisher.publish(
            routing_key="integration.synced",
            payload={"provider": "gmail", "status": "sync_triggered", "data": payload},
        )
        await publisher.close()
