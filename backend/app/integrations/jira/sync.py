"""Jira syncing logic."""

import logging
from uuid import UUID

from app.core.security import decrypt_token
from app.database.session import AsyncSessionLocal
from app.repositories.integration_repository import IntegrationRepository
from app.repositories.oauth_token_repository import OAuthTokenRepository

logger = logging.getLogger(__name__)


class JiraSync:
    @staticmethod
    async def sync_issues(user_id: str) -> None:
        """Fetch Jira issues and perform background sync."""
        async with AsyncSessionLocal() as session:
            integrations = IntegrationRepository(session)
            tokens = OAuthTokenRepository(session)

            integration = await integrations.get_by_user_and_provider(
                UUID(user_id), "jira"
            )
            if not integration:
                logger.warning(
                    f"JiraSync: No jira integration found for user {user_id}"
                )
                return

            token_record = await tokens.get_by_integration(integration.id)
            if not token_record or not token_record.access_token:
                logger.warning(f"JiraSync: No token found for user {user_id}")
                return

            access_token = decrypt_token(token_record.access_token)

            import httpx

            async with httpx.AsyncClient(timeout=10.0) as client:
                # Jira API is complicated as it needs a cloudId first
                cloud_resp = await client.get(
                    "https://api.atlassian.com/oauth/token/accessible-resources",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/json",
                    },
                )

                if cloud_resp.status_code == 200:
                    resources = cloud_resp.json()
                    if not resources:
                        logger.warning(
                            f"JiraSync: No accessible resources for user {user_id}"
                        )
                        return
                    cloud_id = resources[0].get("id")

                    search_resp = await client.get(
                        f"https://api.atlassian.com/ex/jira/{cloud_id}/rest/api/3/search",
                        headers={
                            "Authorization": f"Bearer {access_token}",
                            "Accept": "application/json",
                        },
                        params={"jql": "assignee = currentUser()"},
                    )

                    if search_resp.status_code == 200:
                        data = search_resp.json()
                        issues = data.get("issues", [])
                        logger.info(
                            f"JiraSync: Successfully synced {len(issues)} issues for user {user_id}"
                        )
                    else:
                        logger.error(
                            f"JiraSync: Failed to fetch issues for user {user_id}, status={search_resp.status_code}"
                        )
                else:
                    logger.error(
                        f"JiraSync: Failed to fetch cloudId for user {user_id}, status={cloud_resp.status_code}"
                    )
