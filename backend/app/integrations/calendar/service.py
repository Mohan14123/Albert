"""Google Calendar integration — implements BaseIntegration."""

from typing import Any

from app.integrations.base import BaseIntegration
from app.integrations.calendar.oauth import CalendarOAuth
from app.integrations.calendar.sync import CalendarSync
from app.integrations.registry import register_provider


@register_provider("calendar")
class CalendarIntegration(BaseIntegration):
    async def connect(self, user_id: str) -> str:
        """Return OAuth authorization URL for Google Calendar."""
        return CalendarOAuth.get_auth_url(user_id)

    async def exchange_code(self, code: str) -> dict[str, Any]:
        """Exchange authorization code for Calendar tokens."""
        return await CalendarOAuth.exchange_code(code)

    async def disconnect(self, user_id: str) -> bool:
        """Token revocation handled by IntegrationService."""
        return True

    async def refresh_token(self, refresh_token: str) -> dict[str, Any]:
        """Refresh Google Calendar access token."""
        from app.config.settings import settings
        from app.integrations.calendar.oauth import GOOGLE_TOKEN_URL
        from app.integrations.oauth import OAuthHelper

        secret = settings.google_client_secret
        return await OAuthHelper.refresh_token(
            token_url=GOOGLE_TOKEN_URL,
            client_id=settings.google_client_id,
            client_secret=secret.get_secret_value() if secret else "",
            refresh_token=refresh_token,
        )

    async def sync(self, user_id: str) -> None:
        """Run background calendar sync."""
        await CalendarSync.sync_events(user_id)

    async def webhook(self, payload: dict[str, Any]) -> None:
        """Handle Calendar push notification payload."""
        pass  # Calendar uses polling-based sync; webhook is a no-op

    async def health_check(self) -> bool:
        """Check Google Calendar API reachability."""
        import httpx

        try:
            async with httpx.AsyncClient(timeout=5) as client:
                r = await client.get(
                    "https://accounts.google.com/.well-known/openid-configuration"
                )
            return r.status_code == 200
        except Exception:
            return False
