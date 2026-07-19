from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.core.dependencies import get_db
from app.core.responses import success_response
from app.events.publisher import EventPublisher
from app.integrations.oauth import OAuthHelper
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.session_repository import SessionRepository
from app.repositories.user_repository import UserRepository
from app.repositories.user_settings_repository import UserSettingsRepository
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth/google", tags=["auth"])


def _get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(
        users=UserRepository(db),
        refresh_tokens=RefreshTokenRepository(db),
        user_settings=UserSettingsRepository(db),
        sessions=SessionRepository(db),
        events=EventPublisher(),
    )


@router.get("")
async def google_login_redirect():
    """Redirect to Google OAuth consent screen."""
    if not settings.google_client_id:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")

    auth_url = OAuthHelper.build_redirect_url(
        base_url="https://accounts.google.com/o/oauth2/v2/auth",
        client_id=settings.google_client_id,
        scopes=["openid", "email", "profile"],
        redirect_uri=settings.google_redirect_uri,
        state="google_login",  # In prod, generate a secure random state and store in redis
    )
    return RedirectResponse(auth_url)


@router.get("/callback")
async def google_login_callback(
    code: str,
    state: str = None,
    auth_service: AuthService = Depends(_get_auth_service),
):
    """Handle Google OAuth callback, exchange code for tokens, and log in."""
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")

    try:
        tokens = await OAuthHelper.exchange_code(
            token_url="https://oauth2.googleapis.com/token",
            client_id=settings.google_client_id,
            client_secret=settings.google_client_secret.get_secret_value(),
            code=code,
            redirect_uri=settings.google_redirect_uri,
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to exchange code: {str(e)}"
        )

    id_token = tokens.get("id_token")
    if not id_token:
        raise HTTPException(status_code=400, detail="No id_token received from Google")

    # In a real app, verify the JWT signature using Google's public keys.
    # We will let the auth_service handle the payload extraction.
    result = await auth_service.google_login(id_token)
    return success_response(result)
