"""Business operations for OAuth-backed integrations."""

from datetime import UTC, datetime
from uuid import UUID

from app.core.exceptions import NotFoundError, ProviderError, ValidationError
from app.core.security import encrypt_token
from app.integrations.manager import IntegrationManager
from app.repositories.integration_repository import IntegrationRepository
from app.repositories.oauth_token_repository import OAuthTokenRepository
from app.services import EventDispatcher

_manager = IntegrationManager()


class IntegrationService:
    """Coordinates integration persistence and delegates OAuth mechanics to providers."""

    def __init__(
        self,
        integrations: IntegrationRepository,
        tokens: OAuthTokenRepository,
        events: EventDispatcher,
    ) -> None:
        self._integrations = integrations
        self._tokens = tokens
        self._events = events

    async def get_integrations(self, user_id: UUID) -> list:
        return await self._integrations.get_by_user(user_id)

    async def connect(self, user_id: UUID, provider: str) -> str:
        """Generate an OAuth redirect URL for the given provider."""
        try:
            provider_instance = _manager.get_provider_instance(provider)
        except ValueError:
            raise ValidationError(f"Provider '{provider}' is not supported")
        return await provider_instance.connect(str(user_id))

    async def handle_callback(self, provider: str, code: str, state: str) -> None:
        """
        Exchange auth code → encrypt tokens → persist integration → publish event.
        The `state` value carries the user_id set during the connect step.
        """
        # state = user_id (set in connect URL generation)
        try:
            user_id = UUID(state)
        except ValueError:
            raise ValidationError("Invalid state parameter in OAuth callback")

        try:
            provider_instance = _manager.get_provider_instance(provider)
        except ValueError:
            raise ValidationError(f"Provider '{provider}' is not supported")

        # Exchange authorization code for tokens
        token_data = await provider_instance.exchange_code(code)
        access_token: str = token_data.get("access_token", "")
        refresh_token: str = token_data.get("refresh_token", "")
        expires_in: int = token_data.get("expires_in", 3600)

        if not access_token:
            raise ProviderError(f"No access token returned by {provider}")

        # Upsert integration record
        existing = await self._integrations.get_by_user_and_provider(user_id, provider)
        if existing is None:
            integration = await self._integrations.create(user_id, provider)
        else:
            integration = existing
        await self._integrations.update_status(integration.id, "connected")

        # Encrypt and persist OAuth tokens
        from datetime import timedelta

        existing_token = await self._tokens.get_by_integration(integration.id)
        token_expires = datetime.now(UTC) + timedelta(seconds=expires_in)
        if existing_token is None:
            await self._tokens.create(
                integration.id,
                encrypt_token(access_token),
                encrypt_token(refresh_token) if refresh_token else "",
                token_expires,
            )
        else:
            await self._tokens.update(
                existing_token.id,
                {
                    "access_token": encrypt_token(access_token),
                    "refresh_token": (
                        encrypt_token(refresh_token)
                        if refresh_token
                        else existing_token.refresh_token
                    ),
                    "expires_at": token_expires,
                },
            )

        await self._events.publish(
            "integration.connected",
            {
                "integration_id": str(integration.id),
                "user_id": str(user_id),
                "provider": provider,
            },
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
            raise NotFoundError(f"No '{provider}' integration found for this account")
        return integration
