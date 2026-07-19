from typing import Any

from app.integrations.base import BaseIntegration
from app.integrations.jira.oauth import JiraOAuth
from app.integrations.jira.sync import JiraSync
from app.integrations.registry import register_provider


@register_provider("jira")
class JiraIntegration(BaseIntegration):
    async def connect(self, user_id: str) -> str:
        """Return OAuth authorization URL for Jira."""
        return JiraOAuth.get_auth_url(user_id)

    async def exchange_code(self, code: str) -> dict[str, Any]:
        """Exchange authorization code for Jira tokens."""
        return await JiraOAuth.exchange_code(code)

    async def disconnect(self, user_id: str) -> bool:
        """Token revocation is handled by IntegrationService."""
        return True

    async def refresh_token(self, refresh_token: str) -> dict[str, Any]:
        """Jira tokens refresh handled by standard OAuth."""
        import httpx

        from app.config.settings import settings
        from app.integrations.jira.oauth import JIRA_TOKEN_URL

        secret = settings.jira_client_secret
        client_secret = secret.get_secret_value() if secret else ""

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                JIRA_TOKEN_URL,
                json={
                    "grant_type": "refresh_token",
                    "client_id": settings.jira_client_id,
                    "client_secret": client_secret,
                    "refresh_token": refresh_token,
                },
            )
            data = resp.json()
            return {
                "access_token": data.get("access_token"),
                "refresh_token": data.get("refresh_token", ""),
                "expires_in": int(data.get("expires_in", 3600)),
            }

    async def sync(self, user_id: str) -> None:
        """Run a background Jira sync."""
        await JiraSync.sync_issues(user_id)

    async def webhook(self, payload: dict[str, Any]) -> None:
        """Handle Jira push notification payload."""
        pass

    async def health_check(self) -> bool:
        """Check that Jira API is reachable."""
        import httpx

        try:
            async with httpx.AsyncClient(timeout=5) as client:
                r = await client.get("https://api.atlassian.com/")
            return r.status_code == 200
        except Exception:
            return False
