from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

@dataclass(frozen=True)
class PlanStep:
    """A single tool execution step in the plan."""
    step_id: str
    tool_name: str
    args: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExecutionPlan:
    """The complete execution plan containing steps and metadata."""
    intent: str
    confidence: float
    steps: list[PlanStep] = field(default_factory=list)
