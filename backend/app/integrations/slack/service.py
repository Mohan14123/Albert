from typing import Any

from app.integrations.base import BaseIntegration
from app.integrations.registry import register_provider
from app.integrations.slack.oauth import SlackOAuth
from app.integrations.slack.sync import SlackSync


@register_provider("slack")
class SlackIntegration(BaseIntegration):
    async def connect(self, user_id: str) -> str:
        """Return OAuth authorization URL for Slack."""
        return SlackOAuth.get_auth_url(user_id)

    async def exchange_code(self, code: str) -> dict[str, Any]:
        """Exchange authorization code for Slack tokens."""
        return await SlackOAuth.exchange_code(code)

    async def disconnect(self, user_id: str) -> bool:
        """Token revocation is handled by IntegrationService."""
        return True

    async def refresh_token(self, refresh_token: str) -> dict[str, Any]:
        """Slack tokens do not typically refresh in v2, but if they do, implement here."""
        return {}

    async def sync(self, user_id: str) -> None:
        """Run a background Slack sync."""
        await SlackSync.sync_messages(user_id)

    async def webhook(self, payload: dict[str, Any]) -> None:
        """Handle Slack push notification payload."""
        pass

    async def health_check(self) -> bool:
        """Check that Slack API is reachable."""
        import httpx

        try:
            async with httpx.AsyncClient(timeout=5) as client:
                r = await client.get("https://slack.com/api/api.test")
            return r.status_code == 200
        except Exception:
            return False
