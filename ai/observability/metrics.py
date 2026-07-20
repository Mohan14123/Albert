from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any
from .models import AIMetricEvent, TokenUsageRecord

logger = logging.getLogger(__name__)


class MetricsCollector:
    """In-memory aggregator for tracking pipeline metrics, token consumption, and errors."""

    def __init__(self) -> None:
        self._events: list[AIMetricEvent] = []
        self._token_usage: list[TokenUsageRecord] = []
        self._step_latencies: dict[str, list[float]] = defaultdict(list)
        self._error_counts: dict[str, int] = defaultdict(int)

    def record_event(self, event: AIMetricEvent) -> None:
        """Record a pipeline telemetry event."""
        self._events.append(event)
        self._step_latencies[event.event_type].append(event.duration_ms)
        if "error" in event.metadata:
            err_name = str(event.metadata["error"])
            self._error_counts[err_name] += 1

    def record_tokens(
        self, provider: str, model: str, prompt_tokens: int, completion_tokens: int
    ) -> None:
        """Record token usage metrics from model generation."""
        record = TokenUsageRecord(
            provider=provider,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        )
        self._token_usage.append(record)

    def get_summary(self) -> dict[str, Any]:
        """Return an aggregated metrics summary dictionary."""
        total_tokens = sum(t.total_tokens for t in self._token_usage)
        total_prompt_tokens = sum(t.prompt_tokens for t in self._token_usage)
        total_completion_tokens = sum(t.completion_tokens for t in self._token_usage)

        avg_latencies: dict[str, float] = {}
        for step, lats in self._step_latencies.items():
            if lats:
                avg_latencies[step] = round(sum(lats) / len(lats), 2)

        return {
            "total_requests": len(self._events),
            "total_tokens": total_tokens,
            "prompt_tokens": total_prompt_tokens,
            "completion_tokens": total_completion_tokens,
            "average_latencies_ms": avg_latencies,
            "error_counts": dict(self._error_counts),
        }

    def clear(self) -> None:
        """Reset all metrics data."""
        self._events.clear()
        self._token_usage.clear()
        self._step_latencies.clear()
        self._error_counts.clear()
