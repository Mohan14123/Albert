from typing import Any

from app.integrations.base import BaseIntegration
from app.integrations.github.oauth import GitHubOAuth
from app.integrations.github.sync import GitHubSync
from app.integrations.registry import register_provider


@register_provider("github")
class GitHubIntegration(BaseIntegration):
    async def connect(self, user_id: str) -> str:
        """Return OAuth authorization URL for GitHub."""
        return GitHubOAuth.get_auth_url(user_id)

    async def exchange_code(self, code: str) -> dict[str, Any]:
        """Exchange authorization code for GitHub tokens."""
        return await GitHubOAuth.exchange_code(code)

    async def disconnect(self, user_id: str) -> bool:
        """Token revocation is handled by IntegrationService."""
        return True

    async def refresh_token(self, refresh_token: str) -> dict[str, Any]:
        """GitHub handles token refresh; stubbed for now."""
        return {}

    async def sync(self, user_id: str) -> None:
        """Run a background GitHub sync."""
        await GitHubSync.sync_issues(user_id)

    async def webhook(self, payload: dict[str, Any]) -> None:
        """Handle GitHub webhook payload."""
        pass

    async def health_check(self) -> bool:
        """Check that GitHub API is reachable."""
        import httpx

        try:
            async with httpx.AsyncClient(timeout=5) as client:
                r = await client.get("https://api.github.com/")
            return r.status_code == 200
        except Exception:
            return False
