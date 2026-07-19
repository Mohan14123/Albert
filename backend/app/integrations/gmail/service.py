"""Gmail integration — implements BaseIntegration for Google Gmail."""

from typing import Any

from app.integrations.base import BaseIntegration
from app.integrations.gmail.oauth import GmailOAuth
from app.integrations.gmail.sync import GmailSync
from app.integrations.gmail.webhook import GmailWebhook
from app.integrations.registry import register_provider


@register_provider("gmail")
class GmailIntegration(BaseIntegration):
    async def connect(self, user_id: str) -> str:
        """Return OAuth authorization URL for Gmail."""
        return GmailOAuth.get_auth_url(user_id)

    async def exchange_code(self, code: str) -> dict[str, Any]:
        """Exchange authorization code for Gmail tokens."""
        return await GmailOAuth.exchange_code(code)

    async def disconnect(self, user_id: str) -> bool:
        """Token revocation is handled by IntegrationService; returns True."""
        return True

    async def refresh_token(self, refresh_token: str) -> dict[str, Any]:
        """Refresh the Gmail access token."""
        from app.config.settings import settings
        from app.integrations.gmail.oauth import GOOGLE_TOKEN_URL
        from app.integrations.oauth import OAuthHelper

        secret = settings.google_client_secret
        return await OAuthHelper.refresh_token(
            token_url=GOOGLE_TOKEN_URL,
            client_id=settings.google_client_id,
            client_secret=secret.get_secret_value() if secret else "",
            refresh_token=refresh_token,
        )

    async def sync(self, user_id: str) -> None:
        """Run a background Gmail email sync."""
        await GmailSync.sync_emails(user_id)

    async def webhook(self, payload: dict[str, Any]) -> None:
        """Handle Gmail push notification payload."""
        await GmailWebhook.handle(payload)

    async def health_check(self) -> bool:
        """Check that Google's token endpoint is reachable."""
        import httpx

        try:
            async with httpx.AsyncClient(timeout=5) as client:
                r = await client.get(
                    "https://accounts.google.com/.well-known/openid-configuration"
                )
            return r.status_code == 200
        except Exception:
            return False
