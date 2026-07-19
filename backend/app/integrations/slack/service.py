from typing import Any

from app.integrations.base import BaseIntegration
from app.integrations.registry import register_provider


@register_provider("slack")
class SlackIntegration(BaseIntegration):
    async def connect(self, user_id: str) -> str:
        raise NotImplementedError("Slack integration is stubbed")

    async def exchange_code(self, code: str) -> dict[str, Any]:
        raise NotImplementedError("Slack integration is stubbed")

    async def disconnect(self, user_id: str) -> bool:
        raise NotImplementedError()

    async def refresh_token(self, refresh_token: str) -> dict[str, Any]:
        raise NotImplementedError()

    async def sync(self, user_id: str) -> None:
        raise NotImplementedError()

    async def webhook(self, payload: dict[str, Any]) -> None:
        raise NotImplementedError()

    async def health_check(self) -> bool:
        raise NotImplementedError()
