"""AI Worker — consumes MessageReceived events and forwards to the AI service."""

import asyncio
import logging

import httpx

from app.config.settings import settings
from app.events.consumer import BaseConsumer
from app.events.schemas import DomainEvent

logger = logging.getLogger(__name__)

QUEUE_NAME = "chat.ai.queue"
ROUTING_KEY = "message.received"
EXCHANGE = "domain.exchange"


class AIWorker(BaseConsumer):
    """Consumes MessageReceived → calls AI service → publishes AIResponseGenerated."""

    async def on_message(self, event: DomainEvent) -> None:
        payload = event.payload
        message_id = payload.get("message_id")
        chat_id = payload.get("chat_id")
        user_id = payload.get("user_id")

        logger.info(
            "AIWorker processing message_id=%s chat_id=%s",
            message_id,
            chat_id,
        )

        try:
            async with httpx.AsyncClient(timeout=settings.ai_request_timeout) as client:
                headers = {}
                if settings.ai_api_key:
                    headers["X-Internal-Api-Key"] = (
                        settings.ai_api_key.get_secret_value()
                    )

                response = await client.post(
                    f"{settings.ai_service_url}/process",
                    json={
                        "message_id": message_id,
                        "chat_id": chat_id,
                        "user_id": user_id,
                        "correlation_id": str(event.correlation_id),
                    },
                    headers=headers,
                )
                response.raise_for_status()
                result = response.json()

            # Publish the AI response back as an event
            await self._publisher.publish(
                "message.generated",
                {
                    "message_id": message_id,
                    "chat_id": chat_id,
                    "content": result.get("content", ""),
                    "token_count": result.get("token_count"),
                },
                correlation_id=event.correlation_id,
            )
            logger.info(
                "AIWorker published message.generated for message_id=%s", message_id
            )

        except httpx.HTTPStatusError as exc:
            logger.error(
                "AI service returned error %s for message_id=%s: %s",
                exc.response.status_code,
                message_id,
                exc.response.text,
            )
            raise  # triggers retry/DLQ in BaseConsumer

        except httpx.RequestError as exc:
            logger.error(
                "AI service unreachable for message_id=%s: %s", message_id, exc
            )
            raise


async def run_ai_worker() -> None:
    """Entry-point coroutine — runs the AI worker indefinitely."""
    worker = AIWorker(
        queue_name=QUEUE_NAME,
        exchange_name=EXCHANGE,
        routing_key=ROUTING_KEY,
    )
    await worker.start()


if __name__ == "__main__":
    asyncio.run(run_ai_worker())
