"""Auth endpoints — register, login, token rotation, session management."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.core.dependencies import get_current_user, get_db
from app.core.responses import success_response
from app.database.models.user import User
from app.events.publisher import EventPublisher
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.session_repository import SessionRepository
from app.repositories.user_repository import UserRepository
from app.repositories.user_settings_repository import UserSettingsRepository
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def _get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    """Build AuthService with its dependencies."""
    return AuthService(
        users=UserRepository(db),
        refresh_tokens=RefreshTokenRepository(db),
        user_settings=UserSettingsRepository(db),
        sessions=SessionRepository(db),
        events=EventPublisher(),
    )


@router.post("/register", status_code=201)
async def register(
    body: RegisterRequest,
    service: AuthService = Depends(_get_auth_service),
) -> dict:
    """Create a new user account."""
    user_id = await service.register(body.email, body.password, body.full_name)
    return success_response({"user_id": str(user_id)})


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    service: AuthService = Depends(_get_auth_service),
) -> dict:
    """Authenticate and receive JWT + refresh token."""
    tokens = await service.login(body.email, body.password)
    return tokens


class GoogleLoginRequest(BaseModel):
    id_token: str


@router.post("/google-login", response_model=TokenResponse)
async def google_login(
    body: GoogleLoginRequest,
    service: AuthService = Depends(_get_auth_service),
) -> dict:
    """Authenticate via Google ID token."""
    tokens = await service.google_login(body.id_token)
    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    body: RefreshRequest,
    service: AuthService = Depends(_get_auth_service),
) -> dict:
    """Rotate tokens using a valid refresh token."""
    tokens = await service.refresh(body.refresh_token)
    return tokens


@router.post("/logout")
async def logout(
    body: RefreshRequest,
    service: AuthService = Depends(_get_auth_service),
    _current_user: User = Depends(get_current_user),
) -> dict:
    """Revoke the supplied refresh token."""
    await service.logout(body.refresh_token)
    return success_response({"message": "Logged out successfully"})


@router.post("/logout-all")
async def logout_all(
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(_get_auth_service),
) -> dict:
    """Revoke all refresh tokens for the authenticated user."""
    count = await service.logout_all(current_user.id)
    return success_response({"revoked_sessions": count})


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)) -> User:
    """Return the current authenticated user."""
    return current_user
