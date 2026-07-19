"""Sync Worker — consumes IntegrationSynced events and runs provider sync."""

import asyncio
import logging

from app.events.consumer import BaseConsumer
from app.events.schemas import DomainEvent
from app.integrations.manager import IntegrationManager

logger = logging.getLogger(__name__)

QUEUE_NAME = "integration.sync.queue"
ROUTING_KEY = "integration.synced"
EXCHANGE = "domain.exchange"

_manager = IntegrationManager()


class SyncWorker(BaseConsumer):
    """Consumes IntegrationSynced → delegates to provider.sync()."""

    async def on_message(self, event: DomainEvent) -> None:
        payload = event.payload
        integration_id = payload.get("integration_id")
        user_id = payload.get("user_id")
        provider = payload.get("provider")

        if not provider or not user_id:
            logger.warning("SyncWorker received event without provider/user_id: %s", payload)
            return

        logger.info(
            "SyncWorker syncing provider=%s user_id=%s integration_id=%s",
            provider,
            user_id,
            integration_id,
        )

        try:
            await _manager.trigger_sync(provider, user_id)
            logger.info("SyncWorker completed sync for provider=%s user_id=%s", provider, user_id)
        except NotImplementedError:
            logger.info("Sync not yet implemented for provider=%s — skipping", provider)
        except Exception as exc:
            logger.error("SyncWorker failed for provider=%s: %s", provider, exc)
            raise  # triggers retry/DLQ


async def run_sync_worker() -> None:
    worker = SyncWorker(
        queue_name=QUEUE_NAME,
        exchange_name=EXCHANGE,
        routing_key=ROUTING_KEY,
    )
    await worker.start()


if __name__ == "__main__":
    asyncio.run(run_sync_worker())
