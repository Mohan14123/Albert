"""Chat event handlers."""

import json
import logging
from uuid import UUID

import redis.asyncio as aioredis

from app.config.settings import settings
from app.database.engine import async_session
from app.events.consumer import BaseConsumer
from app.events.publisher import EventPublisher
from app.events.routing import AI_RESPONSE_GENERATED
from app.events.schemas import DomainEvent
from app.repositories.chat_repository import ChatRepository
from app.repositories.message_repository import MessageRepository
from app.services.message_service import MessageService

logger = logging.getLogger(__name__)


class ChatConsumer(BaseConsumer):
    def __init__(self) -> None:
        super().__init__(queue_name="chat.ai.queue", routing_key=AI_RESPONSE_GENERATED)

    async def on_message(self, event: DomainEvent) -> None:
        logger.info("Handling AI response generated event: %s", event.event_id)

        payload = event.payload
        chat_id = UUID(payload["chat_id"])
        content = payload["content"]
        token_count = payload.get("token_count")

        # 1. Store response in DB
        async with async_session() as session:
            service = MessageService(
                chats=ChatRepository(session),
                messages=MessageRepository(session),
                events=EventPublisher(),
            )

            message = await service.store_ai_response(
                chat_id=chat_id,
                content=content,
                token_count=token_count,
            )
            await session.commit()

        # 2. Publish to Redis stream for SSE endpoint
        try:
            r = aioredis.from_url(settings.redis_url, decode_responses=True)
            channel = f"chat:{chat_id}:stream"
            redis_payload = json.dumps(
                {
                    "message_id": str(message.id),
                    "content": content,
                    "role": "assistant",
                    "token_count": token_count,
                    "done": True,
                }
            )
            await r.publish(channel, redis_payload)
            await r.aclose()
        except Exception as exc:
            logger.warning("Failed to publish AI response to Redis: %s", exc)
