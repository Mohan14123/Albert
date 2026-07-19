import asyncio
import logging
from datetime import UTC, datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.events.publisher import EventPublisher

logger = logging.getLogger(__name__)


async def trigger_periodic_sync():
    """Publish a system-wide sync event."""
    logger.info("Scheduler: Triggering periodic sync event...")
    publisher = EventPublisher()
    await publisher.connect()

    # In a real app we might fetch all active integrations from DB and send individual events.
    # For now we just emit a generic sync event.
    await publisher.publish(
        routing_key="system.periodic_sync",
        payload={"timestamp": datetime.now(UTC).isoformat()},
    )
    await publisher.close()


def run_scheduler() -> None:
    """Run the APScheduler to trigger recurring background jobs."""
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting background scheduler...")

    scheduler = AsyncIOScheduler()
    # Trigger a sync every 15 minutes (or 1 min for demo purposes)
    scheduler.add_job(trigger_periodic_sync, "interval", minutes=1)
    scheduler.start()

    # Keep the main thread alive
    import contextlib

    with contextlib.suppress(KeyboardInterrupt, SystemExit):
        asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    run_scheduler()
