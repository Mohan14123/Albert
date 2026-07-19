"""Gmail OAuth specifics — scopes, endpoints, and URL builder."""

from app.config.settings import settings

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"

GMAIL_SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/gmail.readonly",
]


class GmailOAuth:
    @staticmethod
    def get_auth_url(user_id: str) -> str:
        """Build the Google OAuth authorization URL with Gmail scopes."""
        from app.integrations.oauth import OAuthHelper
        return OAuthHelper.build_redirect_url(
            base_url=GOOGLE_AUTH_URL,
            client_id=settings.google_client_id,
            scopes=GMAIL_SCOPES,
            redirect_uri=settings.google_redirect_uri,
            state=user_id,  # state carries user_id back in callback
        )

    @staticmethod
    async def exchange_code(code: str) -> dict:
        """Exchange Gmail authorization code for tokens."""
        from app.integrations.oauth import OAuthHelper
        secret = settings.google_client_secret
        return await OAuthHelper.exchange_code(
            token_url=GOOGLE_TOKEN_URL,
            client_id=settings.google_client_id,
            client_secret=secret.get_secret_value() if secret else "",
            code=code,
            redirect_uri=settings.google_redirect_uri,
        )
