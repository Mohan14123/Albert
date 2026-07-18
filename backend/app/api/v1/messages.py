from fastapi import APIRouter
from typing import Any
from app.api.schemas.messages import SendMessageRequest, MessageListResponse

router = APIRouter(prefix="/chats/{chat_id}/messages", tags=["messages"])

@router.post("")
async def send_message(chat_id: str, request: SendMessageRequest) -> Any:
    return {"success": True}

@router.get("", response_model=MessageListResponse)
async def list_messages(chat_id: str, page: int = 1, limit: int = 20) -> Any:
    return {"items": [], "total": 0, "page": page, "limit": limit}

@router.get("/stream")
async def stream_messages(chat_id: str) -> Any:
    return {"success": True}
