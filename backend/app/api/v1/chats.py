"""Chat CRUD endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.chats import (
    ChatListResponse,
    ChatResponse,
    CreateChatRequest,
    RenameChatRequest,
)
from app.core.dependencies import get_current_user, get_db
from app.core.responses import success_response
from app.database.models.user import User
from app.events.publisher import EventPublisher
from app.repositories.chat_repository import ChatRepository
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chats", tags=["chats"])


def _get_chat_service(db: AsyncSession = Depends(get_db)) -> ChatService:
    return ChatService(chats=ChatRepository(db), events=EventPublisher())


@router.post("", status_code=201, response_model=ChatResponse)
async def create_chat(
    body: CreateChatRequest,
    current_user: User = Depends(get_current_user),
    service: ChatService = Depends(_get_chat_service),
) -> dict:
    """Create a new chat session."""
    chat = await service.create_chat(current_user.id, body.title)
    return {
        "id": chat.id,
        "title": chat.title,
        "archived": chat.archived,
        "created_at": chat.created_at,
        "updated_at": chat.updated_at,
    }


@router.get("", response_model=ChatListResponse)
async def list_chats(
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    service: ChatService = Depends(_get_chat_service),
) -> dict:
    """List all chats for the current user (paginated)."""
    items, total = await service.get_chats(current_user.id, page, limit)
    return {
        "items": [
            {
                "id": c.id,
                "title": c.title,
                "archived": c.archived,
                "created_at": c.created_at,
                "updated_at": c.updated_at,
            }
            for c in items
        ],
        "total": total,
        "page": page,
        "limit": limit,
    }


@router.get("/{chat_id}", response_model=ChatResponse)
async def get_chat(
    chat_id: UUID,
    current_user: User = Depends(get_current_user),
    service: ChatService = Depends(_get_chat_service),
) -> dict:
    """Return a single chat by ID."""
    chat = await service.get_chat(current_user.id, chat_id)
    return {
        "id": chat.id,
        "title": chat.title,
        "archived": chat.archived,
        "created_at": chat.created_at,
        "updated_at": chat.updated_at,
    }


@router.patch("/{chat_id}", response_model=ChatResponse)
async def rename_chat(
    chat_id: UUID,
    body: RenameChatRequest,
    current_user: User = Depends(get_current_user),
    service: ChatService = Depends(_get_chat_service),
) -> dict:
    """Rename an existing chat."""
    chat = await service.rename_chat(current_user.id, chat_id, body.title)
    return {
        "id": chat.id,
        "title": chat.title,
        "archived": chat.archived,
        "created_at": chat.created_at,
        "updated_at": chat.updated_at,
    }


@router.delete("/{chat_id}", status_code=204)
async def delete_chat(
    chat_id: UUID,
    current_user: User = Depends(get_current_user),
    service: ChatService = Depends(_get_chat_service),
) -> None:
    """Soft-delete a chat session."""
    await service.delete_chat(current_user.id, chat_id)
