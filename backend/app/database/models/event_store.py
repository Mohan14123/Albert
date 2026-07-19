from sqlalchemy import JSON, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID

from app.database.base import BaseModel


class EventStore(BaseModel):
    __tablename__ = "event_store"

    event_name = Column(String(255), nullable=False, index=True)
    routing_key = Column(String(255), nullable=True)
    payload = Column(JSON, default=dict)
    aggregate_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)
