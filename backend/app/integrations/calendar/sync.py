"""Google Calendar syncing logic."""

import logging
from uuid import UUID

from app.core.security import decrypt_token
from app.database.engine import async_session
from app.repositories.integration_repository import IntegrationRepository
from app.repositories.oauth_token_repository import OAuthTokenRepository

logger = logging.getLogger(__name__)


class CalendarSync:
    @staticmethod
    async def sync_events(user_id: str) -> None:
        """Fetch Calendar events and perform background sync."""
        async with async_session() as session:
            integrations = IntegrationRepository(session)
            tokens = OAuthTokenRepository(session)

            integration = await integrations.get_by_user_and_provider(
                UUID(user_id), "google_calendar"
            )
            if not integration:
                logger.warning(
                    f"CalendarSync: No calendar integration found for user {user_id}"
                )
                return

            token_record = await tokens.get_by_integration(integration.id)
            if not token_record or not token_record.access_token:
                logger.warning(f"CalendarSync: No token found for user {user_id}")
                return

            access_token = decrypt_token(token_record.access_token)

            import httpx

            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    "https://www.googleapis.com/calendar/v3/calendars/primary/events",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/json",
                    },
                )

                if resp.status_code == 200:
                    data = resp.json()
                    events = data.get("items", [])
                    logger.info(
                        f"CalendarSync: Successfully synced {len(events)} events for user {user_id}"
                    )
                else:
                    logger.error(
                        f"CalendarSync: Failed to fetch events for user {user_id}, status={resp.status_code}"
                    )
