"""Integration event handlers."""
import logging
from app.events.consumer import BaseConsumer
from app.events.routing import INTEGRATION_CONNECTED
from app.events.schemas import DomainEvent
from app.events.exchanges import INTEGRATION_EXCHANGE

logger = logging.getLogger(__name__)

class IntegrationConsumer(BaseConsumer):
    def __init__(self) -> None:
        super().__init__(
            queue_name="integration.sync.queue",
            routing_key=INTEGRATION_CONNECTED,
            exchange_name=INTEGRATION_EXCHANGE
        )

    async def on_message(self, event: DomainEvent) -> None:
        logger.info("Handling integration connected event: %s", event.event_id)
        # TODO: Call integration_service.trigger_sync()
        pass
