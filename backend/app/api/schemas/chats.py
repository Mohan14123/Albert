from pydantic import BaseModel
from typing import List
from uuid import UUID
from datetime import datetime

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
    items: List[ChatResponse]
    total: int
    page: int
    limit: int
