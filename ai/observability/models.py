from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class AIMetricEvent:
    """A diagnostic telemetry event recorded during pipeline execution."""
    event_id: str
    event_type: str  # request, tool_call, gateway_call, planner_call, error
    conversation_id: str
    duration_ms: float
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=_utc_now)


@dataclass(frozen=True)
class LatencyRecord:
    """Recorded duration for a specific execution step."""
    step_name: str
    duration_ms: float


@dataclass(frozen=True)
class TokenUsageRecord:
    """Token metrics for model generation."""
    provider: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
