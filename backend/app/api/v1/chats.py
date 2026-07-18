from fastapi import APIRouter
from typing import Any
from app.api.schemas.chats import CreateChatRequest, RenameChatRequest, ChatResponse, ChatListResponse
from uuid import uuid4
from datetime import datetime, UTC

router = APIRouter(prefix="/chats", tags=["chats"])

@router.post("", response_model=ChatResponse)
async def create_chat(request: CreateChatRequest) -> Any:
    return {"id": uuid4(), "title": request.title, "archived": False, "created_at": datetime.now(UTC), "updated_at": datetime.now(UTC)}

@router.get("", response_model=ChatListResponse)
async def list_chats(page: int = 1, limit: int = 20) -> Any:
    return {"items": [], "total": 0, "page": page, "limit": limit}

@router.get("/{chat_id}", response_model=ChatResponse)
async def get_chat(chat_id: str) -> Any:
    return {"id": uuid4(), "title": "Test Chat", "archived": False, "created_at": datetime.now(UTC), "updated_at": datetime.now(UTC)}

@router.patch("/{chat_id}", response_model=ChatResponse)
async def rename_chat(chat_id: str, request: RenameChatRequest) -> Any:
    return {"id": uuid4(), "title": request.title, "archived": False, "created_at": datetime.now(UTC), "updated_at": datetime.now(UTC)}

@router.delete("/{chat_id}")
async def delete_chat(chat_id: str) -> Any:
    return {"success": True}
