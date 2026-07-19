"""Slack OAuth specifics."""

from typing import Any

from app.config.settings import settings

SLACK_AUTH_URL = "https://slack.com/oauth/v2/authorize"
SLACK_TOKEN_URL = "https://slack.com/api/oauth.v2.access"

SLACK_SCOPES = [
    "channels:history",
    "channels:read",
    "groups:history",
    "groups:read",
    "im:history",
    "im:read",
    "mpim:history",
    "mpim:read",
]


class SlackOAuth:
    @staticmethod
    def get_auth_url(user_id: str) -> str:
        from app.integrations.oauth import OAuthHelper

        return OAuthHelper.build_redirect_url(
            base_url=SLACK_AUTH_URL,
            client_id=settings.slack_client_id,
            scopes=SLACK_SCOPES,
            redirect_uri=settings.slack_redirect_uri,
            state=user_id,
        )

    @staticmethod
    async def exchange_code(code: str) -> dict[str, Any]:
        from app.integrations.oauth import OAuthHelper

        secret = settings.slack_client_secret
        return await OAuthHelper.exchange_code(
            token_url=SLACK_TOKEN_URL,
            client_id=settings.slack_client_id,
            client_secret=secret.get_secret_value() if secret else "",
            code=code,
            redirect_uri=settings.slack_redirect_uri,
        )
