from sqlalchemy import JSON, Column, String

from app.database.base import BaseModel


class PluginRegistry(BaseModel):
    __tablename__ = "plugin_registry"

    name = Column(String(100), unique=True, index=True, nullable=False)
    version = Column(String(50), nullable=False)
    description = Column(String(500), nullable=True)
    status = Column(String(50), default="inactive", nullable=False)
    capabilities = Column(JSON, default=dict)
    config = Column(JSON, default=dict)
