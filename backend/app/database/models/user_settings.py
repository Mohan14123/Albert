from sqlalchemy import Boolean, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.base import BaseModel

class UserSettings(BaseModel):
    __tablename__ = "user_settings"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    theme = Column(String(50), default="system", nullable=True)
    language = Column(String(20), default="en", nullable=True)
    notifications = Column(Boolean, default=True, nullable=False)

    user = relationship("User", back_populates="settings")
