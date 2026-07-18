from pydantic import BaseModel
from typing import Optional

class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    assistant_name: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None

class ProfileResponse(BaseModel):
    full_name: str
    assistant_name: str
    language: str
    timezone: str

class SettingsUpdateRequest(BaseModel):
    theme: Optional[str] = None
    language: Optional[str] = None
    notifications: Optional[bool] = None

class SettingsResponse(BaseModel):
    theme: str
    language: str
    notifications: bool
