"""GitHub syncing logic."""

import logging
from uuid import UUID

from app.core.security import decrypt_token
from app.database.session import AsyncSessionLocal
from app.repositories.integration_repository import IntegrationRepository
from app.repositories.oauth_token_repository import OAuthTokenRepository

logger = logging.getLogger(__name__)


class GitHubSync:
    @staticmethod
    async def sync_issues(user_id: str) -> None:
        """Fetch GitHub issues and PRs and perform background sync."""
        async with AsyncSessionLocal() as session:
            integrations = IntegrationRepository(session)
            tokens = OAuthTokenRepository(session)

            integration = await integrations.get_by_user_and_provider(
                UUID(user_id), "github"
            )
            if not integration:
                logger.warning(
                    f"GitHubSync: No github integration found for user {user_id}"
                )
                return

            token_record = await tokens.get_by_integration(integration.id)
            if not token_record or not token_record.access_token:
                logger.warning(f"GitHubSync: No token found for user {user_id}")
                return

            access_token = decrypt_token(token_record.access_token)

            import httpx

            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    "https://api.github.com/issues",
                    headers={
                        "Authorization": f"token {access_token}",
                        "Accept": "application/vnd.github.v3+json",
                    },
                )

                if resp.status_code == 200:
                    issues = resp.json()
                    logger.info(
                        f"GitHubSync: Successfully synced {len(issues)} issues/PRs for user {user_id}"
                    )
                else:
                    logger.error(
                        f"GitHubSync: Failed to fetch issues for user {user_id}, status={resp.status_code}"
                    )
