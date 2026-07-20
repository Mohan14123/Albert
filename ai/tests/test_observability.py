"""Tests for Observability metrics collector and telemetry logger."""

import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from ai.observability.models import AIMetricEvent
from ai.observability.metrics import MetricsCollector
from ai.observability.logger import AITelemetryLogger


# -- Test 1: Metrics Collector token and event tracking --------------------


def test_metrics_collector():
    """Verify recording of telemetry events and token usage aggregation."""
    collector = MetricsCollector()

    event1 = AIMetricEvent(
        event_id="e1",
        event_type="planner",
        conversation_id="c1",
        duration_ms=45.2,
    )
    event2 = AIMetricEvent(
        event_id="e2",
        event_type="gateway",
        conversation_id="c1",
        duration_ms=320.0,
    )

    collector.record_event(event1)
    collector.record_event(event2)

    collector.record_tokens("openai", "gpt-4o", prompt_tokens=150, completion_tokens=50)
    collector.record_tokens(
        "openai", "gpt-4o", prompt_tokens=200, completion_tokens=100
    )

    summary = collector.get_summary()

    assert summary["total_requests"] == 2
    assert summary["total_tokens"] == 500
    assert summary["prompt_tokens"] == 350
    assert summary["completion_tokens"] == 150
    assert summary["average_latencies_ms"]["planner"] == 45.2
    assert summary["average_latencies_ms"]["gateway"] == 320.0
    print("  PASSED: Metrics collector aggregation and summary")


# -- Test 2: Structured Telemetry Logger -----------------------------------


def test_telemetry_logger():
    """Verify telemetry logger formats event without error."""
    telemetry = AITelemetryLogger()

    event = AIMetricEvent(
        event_id="e3",
        event_type="tool_execution",
        conversation_id="c2",
        duration_ms=12.5,
        metadata={"tool_name": "calculator.compute", "success": True},
    )

    telemetry.log_event(event)
    print("  PASSED: Structured telemetry logger")


# -- Main -------------------------------------------------------------------


async def main():
    print("--- Observability Tests ---")
    test_metrics_collector()
    test_telemetry_logger()

    print("\n All observability tests passed!")


if __name__ == "__main__":
    asyncio.run(main())
