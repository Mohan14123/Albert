"""Jira OAuth specifics."""

from typing import Any

from app.config.settings import settings

JIRA_AUTH_URL = "https://auth.atlassian.com/authorize"
JIRA_TOKEN_URL = "https://auth.atlassian.com/oauth/token"

JIRA_SCOPES = ["read:jira-work", "read:jira-user", "offline_access"]


class JiraOAuth:
    @staticmethod
    def get_auth_url(user_id: str) -> str:
        from urllib.parse import urlencode

        params = {
            "audience": "api.atlassian.com",
            "client_id": settings.jira_client_id,
            "scope": " ".join(JIRA_SCOPES),
            "redirect_uri": settings.jira_redirect_uri,
            "state": user_id,
            "response_type": "code",
            "prompt": "consent",
        }
        return f"{JIRA_AUTH_URL}?{urlencode(params)}"

    @staticmethod
    async def exchange_code(code: str) -> dict[str, Any]:
        import httpx

        from app.core.exceptions import ProviderError

        secret = settings.jira_client_secret
        client_secret = secret.get_secret_value() if secret else ""

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                JIRA_TOKEN_URL,
                json={
                    "grant_type": "authorization_code",
                    "client_id": settings.jira_client_id,
                    "client_secret": client_secret,
                    "code": code,
                    "redirect_uri": settings.jira_redirect_uri,
                },
            )
            if resp.status_code != 200:
                raise ProviderError(f"Jira returned {resp.status_code}: {resp.text}")

            data = resp.json()
            return {
                "access_token": data.get("access_token"),
                "refresh_token": data.get("refresh_token", ""),
                "expires_in": int(data.get("expires_in", 3600)),
            }
