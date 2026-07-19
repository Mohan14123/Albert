"""Ports that adapters from other AI modules implement for orchestration."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Mapping, Sequence

from .models import AssistantResponse, ChatRequest


class IntentPlanner(ABC):
    """Determines the deterministic execution plan for a user request."""

    @abstractmethod
    async def create_plan(self, request: ChatRequest) -> Any:
        """Return a plan object for ``request`` without executing tools."""


class MemoryRetriever(ABC):
    """Retrieves relevant context through a storage-agnostic adapter."""

    @abstractmethod
    async def retrieve(self, request: ChatRequest, plan: Any) -> Sequence[Any]:
        """Return memory records relevant to the request and plan."""


class ToolExecutor(ABC):
    """Executes only the tool calls authorized by a planner-produced plan."""

    @abstractmethod
    async def execute(self, request: ChatRequest, plan: Any) -> Sequence[Any]:
        """Execute authorized tool calls and return normalized results."""


class ContextAssembler(ABC):
    """Builds provider-ready context from normalized pipeline artifacts."""

    @abstractmethod
    async def build(
        self,
        request: ChatRequest,
        plan: Any,
        memories: Sequence[Any],
        tool_results: Sequence[Any],
    ) -> Any:
        """Return the context object consumed by an LLM gateway."""


class LanguageModelGateway(ABC):
    """Generates language model output through a provider-neutral boundary."""

    @abstractmethod
    async def generate(self, context: Any) -> Any:
        """Generate a complete provider-neutral model result."""

    @abstractmethod
    def stream(self, context: Any) -> AsyncIterator[Any]:
        """Yield provider-neutral model events for a streaming response."""


class ResponseFormatter(ABC):
    """Converts provider-neutral model output into API-facing response values."""

    @abstractmethod
    async def format(self, model_result: Any, plan: Any) -> AssistantResponse:
        """Return a validated assistant response for a completed generation."""

    @abstractmethod
    async def format_stream_event(self, event: Any) -> Mapping[str, Any] | None:
        """Convert one model event to a transport-neutral stream payload."""


class MemoryWriter(ABC):
    """Persists approved memory candidates through an external adapter."""

    @abstractmethod
    async def save(
        self, request: ChatRequest, response: AssistantResponse, plan: Any
    ) -> None:
        """Save durable memory after a successful response, if applicable."""
