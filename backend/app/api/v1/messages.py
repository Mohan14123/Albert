"""Message endpoints — send, list, and SSE stream for real-time AI responses."""

import json
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.messages import MessageListResponse, SendMessageRequest
from app.core.dependencies import get_current_user, get_db
from app.core.responses import success_response
from app.database.models.user import User
from app.events.publisher import EventPublisher
from app.repositories.chat_repository import ChatRepository
from app.repositories.message_repository import MessageRepository
from app.services.message_service import MessageService

router = APIRouter(prefix="/chats/{chat_id}/messages", tags=["messages"])


def _get_message_service(db: AsyncSession = Depends(get_db)) -> MessageService:
    return MessageService(
        chats=ChatRepository(db),
        messages=MessageRepository(db),
        events=EventPublisher(),
    )


@router.post("", status_code=201)
async def send_message(
    chat_id: UUID,
    body: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    service: MessageService = Depends(_get_message_service),
) -> dict:
    """Send a user message — stores it and publishes MessageReceived event."""
    message = await service.send_message(current_user.id, chat_id, body.content)
    return success_response(
        {
            "message_id": str(message.id),
            "status": message.status,
            "content": message.content,
        }
    )


@router.get("", response_model=MessageListResponse)
async def list_messages(
    chat_id: UUID,
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    service: MessageService = Depends(_get_message_service),
) -> dict:
    """Return paginated messages for a chat, ordered by created_at."""
    items, total = await service.get_messages(current_user.id, chat_id, page, limit)
    return {
        "items": [
            {
                "id": m.id,
                "chat_id": m.chat_id,
                "role": m.role,
                "content": m.content,
                "status": m.status,
                "token_count": m.token_count,
                "created_at": m.created_at,
            }
            for m in items
        ],
        "total": total,
        "page": page,
        "limit": limit,
    }


@router.get("/stream")
async def stream_messages(
    chat_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """
    SSE endpoint — the client subscribes here to receive AI response chunks
    as they arrive from the AI worker via a Redis pub/sub channel.
    """
    from app.config.settings import settings

    async def event_generator():
        try:
            import redis.asyncio as aioredis

            redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)
            channel = f"chat:{chat_id}:stream"
            pubsub = redis_client.pubsub()
            await pubsub.subscribe(channel)

            # Send an initial connection event
            yield f"event: connected\ndata: {json.dumps({'chat_id': str(chat_id)})}\n\n"

            # Listen for messages with a timeout
            timeout = 120  # 2 minutes max
            elapsed = 0
            while elapsed < timeout:
                message = await pubsub.get_message(
                    ignore_subscribe_messages=True, timeout=1.0
                )
                if message and message["type"] == "message":
                    data = message["data"]
                    yield f"data: {data}\n\n"
                    # Check for done signal
                    try:
                        parsed = json.loads(data)
                        if parsed.get("done"):
                            break
                    except json.JSONDecodeError:
                        pass
                else:
                    # Send heartbeat to keep connection alive
                    elapsed += 1
                    if elapsed % 15 == 0:
                        yield f"event: heartbeat\ndata: {json.dumps({'ts': elapsed})}\n\n"

            await pubsub.unsubscribe(channel)
            await redis_client.aclose()
        except Exception as exc:
            yield f"event: error\ndata: {json.dumps({'error': str(exc)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
