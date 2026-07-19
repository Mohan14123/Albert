"""Gmail syncing logic."""

import logging
from uuid import UUID

from app.core.security import decrypt_token
from app.database.engine import async_session
from app.repositories.integration_repository import IntegrationRepository
from app.repositories.oauth_token_repository import OAuthTokenRepository

logger = logging.getLogger(__name__)


class GmailSync:
    @staticmethod
    async def sync_emails(user_id: str) -> None:
        """Fetch Gmail emails and perform background sync."""
        async with async_session() as session:
            integrations = IntegrationRepository(session)
            tokens = OAuthTokenRepository(session)

            integration = await integrations.get_by_user_and_provider(
                UUID(user_id), "gmail"
            )
            if not integration:
                logger.warning(
                    f"GmailSync: No gmail integration found for user {user_id}"
                )
                return

            token_record = await tokens.get_by_integration(integration.id)
            if not token_record or not token_record.access_token:
                logger.warning(f"GmailSync: No token found for user {user_id}")
                return

            access_token = decrypt_token(token_record.access_token)

            import httpx

            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    "https://gmail.googleapis.com/gmail/v1/users/me/messages",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/json",
                    },
                )

                if resp.status_code == 200:
                    data = resp.json()
                    messages = data.get("messages", [])
                    logger.info(
                        f"GmailSync: Successfully synced {len(messages)} emails for user {user_id}"
                    )
                else:
                    logger.error(
                        f"GmailSync: Failed to fetch emails for user {user_id}, status={resp.status_code}"
                    )
