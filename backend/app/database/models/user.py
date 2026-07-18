from sqlalchemy import Boolean, Column, String, Text
from sqlalchemy.orm import relationship
from app.database.base import BaseModel

class User(BaseModel):
    __tablename__ = "users"

    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    full_name = Column(String(100), nullable=False)
    assistant_name = Column(String(50), default="Albert", nullable=False)
    timezone = Column(String(50), nullable=True)
    language = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    chats = relationship("Chat", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    settings = relationship("UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    integrations = relationship("Integration", back_populates="user", cascade="all, delete-orphan")
