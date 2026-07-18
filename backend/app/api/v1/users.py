from fastapi import APIRouter
from typing import Any
from app.api.schemas.users import ProfileUpdateRequest, SettingsUpdateRequest, ProfileResponse, SettingsResponse

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=ProfileResponse)
async def get_profile() -> Any:
    return {"full_name": "Test User", "assistant_name": "Albert", "language": "en", "timezone": "UTC"}

@router.patch("/me", response_model=ProfileResponse)
async def update_profile(request: ProfileUpdateRequest) -> Any:
    return {"full_name": "Test User", "assistant_name": "Albert", "language": "en", "timezone": "UTC"}

@router.get("/settings", response_model=SettingsResponse)
async def get_settings() -> Any:
    return {"theme": "dark", "language": "en", "notifications": True}

@router.patch("/settings", response_model=SettingsResponse)
async def update_settings(request: SettingsUpdateRequest) -> Any:
    return {"theme": "dark", "language": "en", "notifications": True}
