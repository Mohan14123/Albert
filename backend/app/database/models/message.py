from sqlalchemy import Column, Enum, ForeignKey, Integer, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.base import BaseModel

class Message(BaseModel):
    __tablename__ = "messages"

    chat_id = Column(UUID(as_uuid=True), ForeignKey("chats.id", ondelete="CASCADE"), nullable=False)
    role = Column(Enum("user", "assistant", "system", name="message_role_enum"), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(Enum("pending", "completed", "failed", name="message_status_enum"), default="completed", nullable=False)
    token_count = Column(Integer, nullable=True)

    chat = relationship("Chat", back_populates="messages")

    __table_args__ = (
        Index("ix_messages_chat_id_created_at", "chat_id", "created_at"),
    )
