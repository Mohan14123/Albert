"""IntegrationManager — delegates to provider registry, handles token refresh/encryption."""

import logging
from typing import Any

from app.integrations.base import BaseIntegration
from app.integrations.registry import get_provider

logger = logging.getLogger(__name__)


class IntegrationManager:
    """Top-level coordinator that resolves provider names to provider instances."""

    def get_provider_instance(self, provider: str) -> BaseIntegration:
        """Return a live provider instance; raises ValueError for unknown providers."""
        # Ensure all providers are imported so the registry is populated
        _import_providers()
        return get_provider(provider)

    async def get_connect_url(self, provider: str, user_id: str) -> str:
        instance = self.get_provider_instance(provider)
        return await instance.connect(user_id)

    async def exchange_code(self, provider: str, code: str) -> dict[str, Any]:
        instance = self.get_provider_instance(provider)
        return await instance.exchange_code(code)

    async def disconnect(self, provider: str, user_id: str) -> bool:
        instance = self.get_provider_instance(provider)
        return await instance.disconnect(user_id)

    async def trigger_sync(self, provider: str, user_id: str) -> None:
        instance = self.get_provider_instance(provider)
        await instance.sync(user_id)

    async def handle_webhook(self, provider: str, payload: dict[str, Any]) -> None:
        instance = self.get_provider_instance(provider)
        await instance.webhook(payload)


def _import_providers() -> None:
    """Lazy import all providers to populate the registry."""
    import importlib

    for mod in (
        "app.integrations.gmail.service",
        "app.integrations.calendar.service",
        "app.integrations.slack.service",
        "app.integrations.github.service",
        "app.integrations.jira.service",
        "app.integrations.news.service",
    ):
        try:
            importlib.import_module(mod)
        except Exception as exc:
            logger.debug("Could not import provider module %s: %s", mod, exc)
