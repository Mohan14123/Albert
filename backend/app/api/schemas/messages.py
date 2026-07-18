from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class SendMessageRequest(BaseModel):
    content: str

class MessageResponse(BaseModel):
    id: UUID
    chat_id: UUID
    role: str
    content: str
    status: str
    token_count: Optional[int] = None
    created_at: datetime

class MessageListResponse(BaseModel):
    items: List[MessageResponse]
    total: int
    page: int
    limit: int
