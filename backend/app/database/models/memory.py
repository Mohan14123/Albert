from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.base import BaseModel


class Memory(BaseModel):
    __tablename__ = "memories"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1536), nullable=True)
    category = Column(String(100), nullable=True)
    relevance_score = Column(Float, nullable=True, default=1.0)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", backref="memories")
