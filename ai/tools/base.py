from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Tool(ABC):
    """Abstract Base Class representing a plug-and-play tool."""

    @property
    @abstractmethod
    def name(self) -> str:
        """The dot-separated unique identifier for the tool (e.g., 'calendar.get_events')."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """A description of what the tool does, consumed by the LLM Planner."""
        pass

    @property
    @abstractmethod
    def parameters(self) -> dict[str, Any]:
        """JSON Schema dictionary describing the arguments expected by run()."""
        pass

    @abstractmethod
    async def run(self, **kwargs: Any) -> Any:
        """Asynchronously execute the tool's core logic with validated arguments."""
        pass
