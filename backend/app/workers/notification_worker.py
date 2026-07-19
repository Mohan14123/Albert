"""Notification Worker — consumes user/integration events for notification delivery."""

import asyncio
import logging

from app.config.settings import settings
from app.events.consumer import BaseConsumer
from app.events.schemas import DomainEvent

logger = logging.getLogger(__name__)

QUEUE_NAME = "notification.worker.queue"
ROUTING_KEY = "#"  # wildcard — receives all events routed to notification exchange
EXCHANGE = "domain.exchange"


class NotificationWorker(BaseConsumer):
    """
    Consumes user.created and integration.connected events.
    Placeholder for email/push notification delivery.
    """

    async def on_message(self, event: DomainEvent) -> None:
        logger.info(
            "NotificationWorker received event=%s payload=%s",
            event.event_name,
            event.payload,
        )

        if event.event_name == "user.created":
            await self._handle_user_created(event)
        elif event.event_name == "integration.connected":
            await self._handle_integration_connected(event)
        else:
            logger.debug("NotificationWorker ignoring event=%s", event.event_name)

    async def _handle_user_created(self, event: DomainEvent) -> None:
        """Send welcome notification to newly registered user."""
        user_id = event.payload.get("user_id")
        email = event.payload.get("email")
        logger.info(
            "NotificationWorker: sending welcome notification to user_id=%s email=%s",
            user_id,
            email,
        )
        if settings.smtp_host and settings.smtp_username and settings.smtp_password:
            from email.message import EmailMessage

            import aiosmtplib

            msg = EmailMessage()
            msg["From"] = settings.smtp_from or "noreply@albert.ai"
            msg["To"] = email
            msg["Subject"] = "Welcome to Albert AI"
            msg.set_content(
                f"Hi {email},\n\nWelcome to Albert AI! We're glad to have you."
            )

            try:
                await aiosmtplib.send(
                    msg,
                    hostname=settings.smtp_host,
                    port=settings.smtp_port,
                    username=settings.smtp_username,
                    password=settings.smtp_password.get_secret_value(),
                    use_tls=(settings.smtp_port == 465),
                    start_tls=(settings.smtp_port == 587),
                )
                logger.info("Welcome email sent to %s", email)
            except Exception as e:
                logger.error("Failed to send welcome email to %s: %s", email, e)
        else:
            logger.info("SMTP settings not configured, skipping email delivery.")

    async def _handle_integration_connected(self, event: DomainEvent) -> None:
        """Notify user that their integration was connected successfully."""
        user_id = event.payload.get("user_id")
        provider = event.payload.get("provider")
        logger.info(
            "NotificationWorker: integration connected provider=%s user_id=%s",
            provider,
            user_id,
        )
        # We can implement similarly if we wanted an email. For now, just logging.


async def run_notification_worker() -> None:
    worker = NotificationWorker(
        queue_name=QUEUE_NAME,
        exchange_name=EXCHANGE,
        routing_key=ROUTING_KEY,
    )
    await worker.start()


if __name__ == "__main__":
    asyncio.run(run_notification_worker())
