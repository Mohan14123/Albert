from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class ConnectResponse(BaseModel):
    auth_url: str

class IntegrationResponse(BaseModel):
    id: UUID
    provider: str
    status: str
    connected_at: datetime
    last_sync: Optional[datetime] = None

class IntegrationStatusResponse(BaseModel):
    status: str
    last_sync: Optional[datetime] = None
