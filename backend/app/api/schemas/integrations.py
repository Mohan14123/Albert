from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ConnectResponse(BaseModel):
    auth_url: str


class IntegrationResponse(BaseModel):
    id: UUID
    provider: str
    status: str
    connected_at: datetime
    last_sync: datetime | None = None


class IntegrationStatusResponse(BaseModel):
    status: str
    last_sync: datetime | None = None
