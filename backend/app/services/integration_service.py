"""Business operations for OAuth-backed integrations."""

from uuid import UUID

from app.core.exceptions import NotFoundError, ProviderError
from app.repositories.integration_repository import IntegrationRepository
from app.repositories.oauth_token_repository import OAuthTokenRepository
from app.services import EventDispatcher


class IntegrationService:
    """Coordinates integration persistence; provider mechanics arrive in Phase 8."""

    def __init__(
        self,
        integrations: IntegrationRepository,
        tokens: OAuthTokenRepository,
        events: EventDispatcher,
    ) -> None:
        self._integrations = integrations
        self._tokens = tokens
        self._events = events

    async def get_integrations(self, user_id: UUID):
        return await self._integrations.get_by_user(user_id)

    async def connect(self, user_id: UUID, provider: str) -> str:
        raise ProviderError(
            "OAuth provider configuration is supplied by the Phase 8 integration module"
        )

    async def handle_callback(self, provider: str, code: str, state: str):
        raise ProviderError(
            "OAuth provider callbacks are supplied by the Phase 8 integration module"
        )

    async def disconnect(self, user_id: UUID, provider: str) -> None:
        integration = await self._get_owned_integration(user_id, provider)
        token = await self._tokens.get_by_integration(integration.id)
        if token is not None:
            await self._tokens.delete(token.id)
        await self._integrations.update_status(integration.id, "disconnected")
        await self._events.publish(
            "integration.disconnected",
            {"integration_id": str(integration.id), "user_id": str(user_id)},
        )

    async def trigger_sync(self, user_id: UUID, provider: str) -> None:
        integration = await self._get_owned_integration(user_id, provider)
        await self._events.publish(
            "integration.synced",
            {"integration_id": str(integration.id), "user_id": str(user_id)},
        )

    async def get_status(self, user_id: UUID, provider: str):
        return await self._get_owned_integration(user_id, provider)

    async def _get_owned_integration(self, user_id: UUID, provider: str):
        integration = await self._integrations.get_by_user_and_provider(
            user_id, provider
        )
        if integration is None:
            raise NotFoundError("Integration not found")
        return integration
