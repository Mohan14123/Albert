"""Calendar OAuth specifics — Google Calendar scopes and endpoints."""

from app.config.settings import settings

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"

CALENDAR_SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/calendar.readonly",
]


class CalendarOAuth:
    @staticmethod
    def get_auth_url(user_id: str) -> str:
        from app.integrations.oauth import OAuthHelper
        return OAuthHelper.build_redirect_url(
            base_url=GOOGLE_AUTH_URL,
            client_id=settings.google_client_id,
            scopes=CALENDAR_SCOPES,
            redirect_uri=settings.google_redirect_uri,
            state=user_id,
        )

    @staticmethod
    async def exchange_code(code: str) -> dict:
        from app.integrations.oauth import OAuthHelper
        secret = settings.google_client_secret
        return await OAuthHelper.exchange_code(
            token_url=GOOGLE_TOKEN_URL,
            client_id=settings.google_client_id,
            client_secret=secret.get_secret_value() if secret else "",
            code=code,
            redirect_uri=settings.google_redirect_uri,
        )
