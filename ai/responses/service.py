from __future__ import annotations

from typing import Any, Mapping
from ..orchestrator.contracts import ResponseFormatter
from ..orchestrator.models import AssistantResponse
from ..exceptions import ResponseFormatterError


class DefaultResponseFormatter(ResponseFormatter):
    """Formats LLM gateway generation outputs into API response envelopes."""

    async def format(self, model_result: Any, plan: Any) -> AssistantResponse:
        """Parse complete model result dictionary and construct an AssistantResponse."""
        if not isinstance(model_result, dict):
            raise ResponseFormatterError("Raw model result must be a dictionary")

        content = model_result.get("content")
        if content is None:
            raise ResponseFormatterError(
                "Model result dictionary did not contain a 'content' key"
            )

        metadata = {
            "intent": getattr(plan, "intent", "unknown"),
        }

        # Pull provider metadata if present
        if "provider_metadata" in model_result:
            metadata.update(model_result["provider_metadata"])
        elif "provider" in model_result:
            metadata["provider"] = model_result["provider"]

        return AssistantResponse(content=content, metadata=metadata)

    async def format_stream_event(self, event: Any) -> Mapping[str, Any] | None:
        """Map raw provider streaming events to standardized SSE JSON chunks."""
        if not isinstance(event, dict):
            return None

        delta = event.get("delta")
        if delta is None:
            return None

        return {
            "event": "token",
            "delta": delta,
            "provider": event.get("provider", "unknown"),
        }
