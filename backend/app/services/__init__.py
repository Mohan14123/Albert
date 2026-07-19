"""Business services and their event-dispatching contract."""

from collections.abc import Mapping
from typing import Protocol
from uuid import UUID


class EventDispatcher(Protocol):
    """Stable service-facing event interface implemented by the Phase 6 bus."""

    async def publish(
        self,
        routing_key: str,
        payload: Mapping[str, object],
        *,
        correlation_id: UUID | None = None,
    ) -> None: ...


class NullEventDispatcher:
    """No-op dispatcher used in tests — silently discards all events."""

    async def publish(
        self,
        routing_key: str,
        payload: Mapping[str, object],
        *,
        correlation_id: UUID | None = None,
    ) -> None:
        pass  # intentional no-op


__all__ = ["EventDispatcher", "NullEventDispatcher"]
