from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CreateChatRequest(BaseModel):
    title: str


class RenameChatRequest(BaseModel):
    title: str


class ChatResponse(BaseModel):
    id: UUID
    title: str
    archived: bool
    created_at: datetime
    updated_at: datetime


class ChatListResponse(BaseModel):
    items: list[ChatResponse]
    total: int
    page: int
    limit: int
