from sqlalchemy import JSON, Column, String
from sqlalchemy.dialects.postgresql import UUID

from app.database.base import BaseModel


class AuditLog(BaseModel):
    __tablename__ = "audit_logs"

    user_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    action = Column(String(255), nullable=False, index=True)
    resource_type = Column(String(100), nullable=True)
    resource_id = Column(String(255), nullable=True)
    ip_address = Column(String(50), nullable=True)
    audit_metadata = Column("metadata", JSON, default=dict)
