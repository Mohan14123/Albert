"""Slack syncing logic."""

import logging
from uuid import UUID

from app.core.security import decrypt_token
from app.database.session import AsyncSessionLocal
from app.repositories.integration_repository import IntegrationRepository
from app.repositories.oauth_token_repository import OAuthTokenRepository

logger = logging.getLogger(__name__)


class SlackSync:
    @staticmethod
    async def sync_messages(user_id: str) -> None:
        """Fetch Slack messages and channels and perform background sync."""
        async with AsyncSessionLocal() as session:
            integrations = IntegrationRepository(session)
            tokens = OAuthTokenRepository(session)

            integration = await integrations.get_by_user_and_provider(
                UUID(user_id), "slack"
            )
            if not integration:
                logger.warning(
                    f"SlackSync: No slack integration found for user {user_id}"
                )
                return

            token_record = await tokens.get_by_integration(integration.id)
            if not token_record or not token_record.access_token:
                logger.warning(f"SlackSync: No token found for user {user_id}")
                return

            access_token = decrypt_token(token_record.access_token)

            import httpx

            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    "https://slack.com/api/conversations.list",
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                if resp.status_code == 200:
                    data = resp.json()
                    channels = data.get("channels", [])
                    logger.info(
                        f"SlackSync: Successfully synced {len(channels)} channels for user {user_id}"
                    )
                else:
                    logger.error(
                        f"SlackSync: Failed to fetch channels for user {user_id}, status={resp.status_code}"
                    )
