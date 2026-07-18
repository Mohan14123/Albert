from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.base import BaseModel

class Integration(BaseModel):
    __tablename__ = "integrations"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    provider = Column(String(50), nullable=False)
    status = Column(Enum("connected", "expired", "disconnected", name="integration_status_enum"), nullable=False)
    connected_at = Column(DateTime(timezone=True), nullable=False)
    last_sync = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="integrations")
    oauth_tokens = relationship("OAuthToken", back_populates="integration", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_integrations_user_id_provider", "user_id", "provider", unique=True),
    )
