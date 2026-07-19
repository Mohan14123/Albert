"""Integration endpoints — connect, callback, disconnect, sync, status."""

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.integrations import (
    ConnectResponse,
    IntegrationStatusResponse,
)
from app.core.dependencies import get_current_user, get_db
from app.core.responses import success_response
from app.database.models.user import User
from app.events.publisher import EventPublisher
from app.repositories.integration_repository import IntegrationRepository
from app.repositories.oauth_token_repository import OAuthTokenRepository
from app.services.integration_service import IntegrationService

router = APIRouter(prefix="/integrations", tags=["integrations"])


def _get_integration_service(db: AsyncSession = Depends(get_db)) -> IntegrationService:
    return IntegrationService(
        integrations=IntegrationRepository(db),
        tokens=OAuthTokenRepository(db),
        events=EventPublisher(),
    )


@router.get("")
async def list_integrations(
    current_user: User = Depends(get_current_user),
    service: IntegrationService = Depends(_get_integration_service),
) -> dict:
    """List all integrations for the current user."""
    items = await service.get_integrations(current_user.id)
    return success_response(
        [
            {
                "id": str(i.id),
                "provider": i.provider,
                "status": i.status,
                "connected_at": i.connected_at.isoformat() if i.connected_at else None,
                "last_sync": i.last_sync.isoformat() if i.last_sync else None,
            }
            for i in items
        ]
    )


@router.post("/{provider}/connect", response_model=ConnectResponse)
async def connect_integration(
    provider: str,
    current_user: User = Depends(get_current_user),
    service: IntegrationService = Depends(_get_integration_service),
) -> dict:
    """Generate OAuth redirect URL for the given provider."""
    auth_url = await service.connect(current_user.id, provider)
    return {"auth_url": auth_url}


@router.get("/{provider}/callback")
async def integration_callback(
    provider: str,
    code: str,
    state: str,
    service: IntegrationService = Depends(_get_integration_service),
):
    """
    Public OAuth redirect handler — exchanges auth code, stores tokens,
    then redirects the user back to the frontend dashboard.
    """
    from app.config.settings import settings

    await service.handle_callback(provider, code, state)
    # Redirect to frontend after successful OAuth
    frontend_url = (
        settings.cors_origins[0] if settings.cors_origins else "http://localhost:3000"
    )
    return RedirectResponse(url=f"{frontend_url}/integrations?connected={provider}")


@router.delete("/{provider}", status_code=204)
async def disconnect_integration(
    provider: str,
    current_user: User = Depends(get_current_user),
    service: IntegrationService = Depends(_get_integration_service),
) -> None:
    """Disconnect (revoke tokens + mark disconnected) an integration."""
    await service.disconnect(current_user.id, provider)


@router.post("/{provider}/sync", status_code=202)
async def sync_integration(
    provider: str,
    current_user: User = Depends(get_current_user),
    service: IntegrationService = Depends(_get_integration_service),
) -> dict:
    """Trigger a background sync for the given provider."""
    await service.trigger_sync(current_user.id, provider)
    return success_response({"message": f"Sync triggered for {provider}"})


@router.get("/{provider}/status", response_model=IntegrationStatusResponse)
async def integration_status(
    provider: str,
    current_user: User = Depends(get_current_user),
    service: IntegrationService = Depends(_get_integration_service),
) -> dict:
    """Return connection status for the given provider."""
    integration = await service.get_status(current_user.id, provider)
    return {
        "status": integration.status,
        "last_sync": integration.last_sync,
    }
