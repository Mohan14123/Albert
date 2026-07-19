"""GitHub OAuth specifics."""

from typing import Any

from app.config.settings import settings

GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"

GITHUB_SCOPES = [
    "repo",
    "user",
    "read:org",
]


class GitHubOAuth:
    @staticmethod
    def get_auth_url(user_id: str) -> str:
        from app.integrations.oauth import OAuthHelper

        return OAuthHelper.build_redirect_url(
            base_url=GITHUB_AUTH_URL,
            client_id=settings.github_client_id,
            scopes=GITHUB_SCOPES,
            redirect_uri=settings.github_redirect_uri,
            state=user_id,
        )

    @staticmethod
    async def exchange_code(code: str) -> dict[str, Any]:
        import httpx

        from app.core.exceptions import ProviderError

        secret = settings.github_client_secret
        client_secret = secret.get_secret_value() if secret else ""

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                GITHUB_TOKEN_URL,
                data={
                    "client_id": settings.github_client_id,
                    "client_secret": client_secret,
                    "code": code,
                    "redirect_uri": settings.github_redirect_uri,
                },
                headers={"Accept": "application/json"},
            )
            if resp.status_code != 200:
                raise ProviderError(f"GitHub returned {resp.status_code}")

            data = resp.json()
            if "error" in data:
                raise ProviderError(f"GitHub token error: {data['error']}")

            return {
                "access_token": data.get("access_token"),
                "refresh_token": data.get("refresh_token", ""),
                "expires_in": (
                    int(data.get("expires_in", 3600))
                    if data.get("expires_in")
                    else 31536000
                ),
            }
