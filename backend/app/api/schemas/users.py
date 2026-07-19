from pydantic import BaseModel


class ProfileUpdateRequest(BaseModel):
    full_name: str | None = None
    assistant_name: str | None = None
    language: str | None = None
    timezone: str | None = None


class ProfileResponse(BaseModel):
    full_name: str
    assistant_name: str
    language: str
    timezone: str


class SettingsUpdateRequest(BaseModel):
    theme: str | None = None
    language: str | None = None
    notifications: bool | None = None


class SettingsResponse(BaseModel):
    theme: str
    language: str
    notifications: bool
