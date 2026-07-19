"""Abstract base class for all OAuth integration providers."""

import abc
from typing import Any


class BaseIntegration(abc.ABC):
    @abc.abstractmethod
    async def connect(self, user_id: str) -> str:
        """Returns the OAuth redirect URL for this provider."""

    @abc.abstractmethod
    async def exchange_code(self, code: str) -> dict[str, Any]:
        """Exchange an auth code for access/refresh tokens. Returns token dict."""

    @abc.abstractmethod
    async def disconnect(self, user_id: str) -> bool:
        """Revoke provider-side tokens and return True on success."""

    @abc.abstractmethod
    async def refresh_token(self, refresh_token: str) -> dict[str, Any]:
        """Use a refresh token to obtain a new access token."""

    @abc.abstractmethod
    async def sync(self, user_id: str) -> None:
        """Run a background sync for the given user."""

    @abc.abstractmethod
    async def webhook(self, payload: dict[str, Any]) -> None:
        """Handle an inbound webhook payload from the provider."""

    @abc.abstractmethod
    async def health_check(self) -> bool:
        """Return True if the provider API is reachable."""
