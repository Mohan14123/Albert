"""Chat event handlers."""

import logging

from app.events.consumer import BaseConsumer
from app.events.routing import AI_RESPONSE_GENERATED
from app.events.schemas import DomainEvent

logger = logging.getLogger(__name__)


class ChatConsumer(BaseConsumer):
    def __init__(self) -> None:
        super().__init__(queue_name="chat.ai.queue", routing_key=AI_RESPONSE_GENERATED)

    async def on_message(self, event: DomainEvent) -> None:
        logger.info("Handling AI response generated event: %s", event.event_id)
        # TODO: Call message_service.store_ai_response()
        pass
