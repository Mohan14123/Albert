"""User profile and settings endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.users import (
    ProfileResponse,
    ProfileUpdateRequest,
    SettingsResponse,
    SettingsUpdateRequest,
)
from app.core.dependencies import get_current_user, get_db
from app.core.responses import success_response
from app.database.models.user import User
from app.events.publisher import EventPublisher
from app.repositories.user_repository import UserRepository
from app.repositories.user_settings_repository import UserSettingsRepository
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


def _get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(
        users=UserRepository(db),
        settings=UserSettingsRepository(db),
        events=EventPublisher(),
    )


@router.get("/me", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(_get_user_service),
) -> dict:
    """Return current user's profile."""
    user = await service.get_profile(current_user.id)
    return {
        "full_name": user.full_name,
        "assistant_name": user.assistant_name,
        "language": user.language or "en",
        "timezone": user.timezone or "UTC",
    }


@router.patch("/me", response_model=ProfileResponse)
async def update_profile(
    body: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(_get_user_service),
) -> dict:
    """Update the current user's profile."""
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    user = await service.update_profile(current_user.id, data)
    return {
        "full_name": user.full_name,
        "assistant_name": user.assistant_name,
        "language": user.language or "en",
        "timezone": user.timezone or "UTC",
    }


@router.get("/settings", response_model=SettingsResponse)
async def get_settings(
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(_get_user_service),
) -> dict:
    """Return current user's settings."""
    settings = await service.get_settings(current_user.id)
    return {
        "theme": settings.theme or "dark",
        "language": settings.language or "en",
        "notifications": settings.notifications,
    }


@router.patch("/settings", response_model=SettingsResponse)
async def update_settings(
    body: SettingsUpdateRequest,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(_get_user_service),
) -> dict:
    """Update current user's settings."""
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    settings = await service.update_settings(current_user.id, data)
    return {
        "theme": settings.theme or "dark",
        "language": settings.language or "en",
        "notifications": settings.notifications,
    }
