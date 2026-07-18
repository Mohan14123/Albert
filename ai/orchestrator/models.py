"""Value objects exchanged by the orchestration layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class ChatMessage:
    """A normalized conversation message supplied by an integration adapter."""

    role: str
    content: str


@dataclass(frozen=True)
class ChatRequest:
    """An immutable request accepted by :class:`AIOrchestrator`.

    ``metadata`` is intentionally opaque to keep the AI package independent of
    HTTP frameworks, authentication systems, and database schemas.
    """

    conversation_id: str
    user_id: str
    message: str
    history: Sequence[ChatMessage] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AssistantResponse:
    """Final normalized assistant output returned to the calling backend."""

    content: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class OrchestrationTrace:
    """Non-sensitive diagnostic information emitted for an invocation.

    Backends may log, trace, or discard this value.  It contains identifiers
    and step names only, never raw prompts, messages, or model output.
    """

    conversation_id: str
    completed_steps: tuple[str, ...]
