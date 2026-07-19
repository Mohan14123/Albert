"""Internal AI endpoints — only accessible with a valid API key header."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.core.responses import success_response
from app.events.publisher import EventPublisher
from app.repositories.chat_repository import ChatRepository
from app.repositories.message_repository import MessageRepository
from app.services.message_service import MessageService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["internal"])


class AICallbackRequest(BaseModel):
    """Payload that the AI service sends after generating a response."""

    chat_id: UUID
    content: str
    token_count: int | None = None
    correlation_id: str | None = None


class AIRequestPayload(BaseModel):
    """Outbound request the backend makes to the AI service."""

    chat_id: UUID
    message_id: UUID
    user_id: UUID
    content: str


def _verify_internal_key(x_internal_api_key: str = Header(...)) -> None:
    """Validate that the caller presents the correct internal API key."""
    from app.config.settings import settings

    expected = settings.ai_api_key
    if expected is None or x_internal_api_key != expected.get_secret_value():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid internal API key"
        )


def _get_message_service(db: AsyncSession = Depends(get_db)) -> MessageService:
    return MessageService(
        chats=ChatRepository(db),
        messages=MessageRepository(db),
        events=EventPublisher(),
    )


@router.post("/respond")
async def ai_respond(
    body: AIRequestPayload,
    _key: None = Depends(_verify_internal_key),
) -> dict:
    """
    Backend → AI service request endpoint.
    Used by the AI team to pull messages they should process.
    """
    return success_response(
        {
            "chat_id": str(body.chat_id),
            "message_id": str(body.message_id),
            "content": body.content,
        }
    )


@router.post("/callback")
async def ai_callback(
    body: AICallbackRequest,
    _key: None = Depends(_verify_internal_key),
    service: MessageService = Depends(_get_message_service),
) -> dict:
    """
    AI service → Backend callback.
    Called by the AI worker after generating a response. Stores the assistant
    message and publishes MessageStored event via Redis pub/sub for SSE clients.
    """
    message = await service.store_ai_response(
        body.chat_id, body.content, body.token_count
    )

    # Publish to Redis channel so SSE stream endpoint can forward to the client
    try:
        import json

        import redis.asyncio as aioredis

        from app.config.settings import settings

        r = aioredis.from_url(settings.redis_url, decode_responses=True)
        channel = f"chat:{body.chat_id}:stream"
        payload = json.dumps(
            {
                "message_id": str(message.id),
                "content": body.content,
                "role": "assistant",
                "token_count": body.token_count,
                "done": True,
            }
        )
        await r.publish(channel, payload)
        await r.aclose()
    except Exception as exc:
        logger.warning("Failed to publish AI response to Redis: %s", exc)

    return success_response({"message_id": str(message.id), "status": "stored"})
