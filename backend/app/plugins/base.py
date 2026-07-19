import abc
from typing import Any


class BasePlugin(abc.ABC):
    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Name of the plugin."""
        pass

    @property
    @abc.abstractmethod
    def version(self) -> str:
        """Version of the plugin."""
        pass

    @abc.abstractmethod
    async def initialize(self, config: dict[str, Any]) -> None:
        """Initialize plugin with config."""
        pass

    @abc.abstractmethod
    async def execute(self, action: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Execute a specific action exposed by the plugin."""
        pass
