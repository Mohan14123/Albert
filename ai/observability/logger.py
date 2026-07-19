from __future__ import annotations

import json
import logging
from typing import Any
from .models import AIMetricEvent

logger = logging.getLogger(__name__)


class AITelemetryLogger:
    """Formats and emits structured JSON telemetry logs for AI pipeline steps."""

    def __init__(self, logger_name: str = "ai.telemetry") -> None:
        self._logger = logging.getLogger(logger_name)

    def log_event(self, event: AIMetricEvent) -> None:
        """Log a telemetry event as a structured JSON record."""
        payload = {
            "event_id": event.event_id,
            "event_type": event.event_type,
            "conversation_id": event.conversation_id,
            "duration_ms": round(event.duration_ms, 2),
            "timestamp": event.timestamp.isoformat(),
            "metadata": event.metadata,
        }
        self._logger.info("AI_TELEMETRY %s", json.dumps(payload))
