"""Framework-independent coordinator for the AI request lifecycle."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, AsyncIterator, Mapping

from ..exceptions import AIError
from .contracts import (
    ContextAssembler,
    IntentPlanner,
    LanguageModelGateway,
    MemoryRetriever,
    MemoryWriter,
    ResponseFormatter,
    ToolExecutor,
)
from .models import AssistantResponse, ChatRequest, OrchestrationTrace

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class OrchestratorDependencies:
    """Explicit, injectable collaborators used by :class:`AIOrchestrator`."""

    planner: IntentPlanner
    memory_retriever: MemoryRetriever
    tool_executor: ToolExecutor
    context_assembler: ContextAssembler
    gateway: LanguageModelGateway
    response_formatter: ResponseFormatter
    memory_writer: MemoryWriter


class AIOrchestrator:
    """Coordinate the AI pipeline without owning domain or provider logic.

    The backend invokes this class with a normalized :class:`ChatRequest`.
    Concrete components are injected, allowing the same coordinator to work
    with any HTTP framework, queue consumer, LLM vendor, or memory backend.
    """

    def __init__(self, dependencies: OrchestratorDependencies) -> None:
        """Create an orchestrator with all required pipeline collaborators."""

        self._dependencies = dependencies

    async def respond(
        self, request: ChatRequest
    ) -> tuple[AssistantResponse, OrchestrationTrace]:
        """Run a complete non-streaming pipeline for ``request``.

        Memory is saved only after formatting succeeds, preventing a failed
        generation or formatter from becoming durable user context.
        """
        try:
            plan, context, steps = await self._prepare(request)
        except Exception as exc:
            logger.exception(
                "Pipeline preparation failed for conversation %s",
                request.conversation_id,
            )
            raise AIError(f"Pipeline preparation failed: {exc}") from exc

        try:
            model_result = await self._dependencies.gateway.generate(context)
        except Exception as exc:
            logger.exception(
                "LLM generation failed for conversation %s", request.conversation_id
            )
            raise AIError(f"LLM generation failed: {exc}") from exc

        try:
            response = await self._dependencies.response_formatter.format(
                model_result, plan
            )
        except Exception as exc:
            logger.exception(
                "Response formatting failed for conversation %s",
                request.conversation_id,
            )
            raise AIError(f"Response formatting failed: {exc}") from exc

        try:
            await self._dependencies.memory_writer.save(request, response, plan)
            steps.append("memory_save")
        except Exception as exc:
            # Memory save failure should not break the response
            logger.warning(
                "Memory save failed (non-fatal) for conversation %s: %s",
                request.conversation_id,
                exc,
            )
            steps.append("memory_save_failed")

        return response, OrchestrationTrace(request.conversation_id, tuple(steps))

    async def stream(self, request: ChatRequest) -> AsyncIterator[Mapping[str, Any]]:
        """Yield transport-neutral response events for a streaming request.

        The backend owns the transport (for example SSE or WebSocket).  This
        method deliberately exposes mappings rather than framework events.
        """

        plan, context, _ = await self._prepare(request)
        collected_content: list[str] = []
        try:
            async for event in self._dependencies.gateway.stream(context):
                formatted_event = (
                    await self._dependencies.response_formatter.format_stream_event(
                        event
                    )
                )
                if formatted_event is None:
                    continue
                content = formatted_event.get("delta")
                if isinstance(content, str):
                    collected_content.append(content)
                yield formatted_event
        except Exception as exc:
            logger.exception(
                "Streaming generation failed for conversation %s",
                request.conversation_id,
            )
            yield {"event": "error", "error": str(exc)}
            return

        try:
            response = AssistantResponse(content="".join(collected_content))
            await self._dependencies.memory_writer.save(request, response, plan)
        except Exception as exc:
            logger.warning("Memory save after streaming failed (non-fatal): %s", exc)

    async def _prepare(self, request: ChatRequest) -> tuple[Any, Any, list[str]]:
        """Execute the shared preparation stages for complete and streamed calls."""

        logger.debug("Starting pipeline for conversation %s", request.conversation_id)

        plan = await self._dependencies.planner.create_plan(request)
        steps = ["planning"]

        memories = await self._dependencies.memory_retriever.retrieve(request, plan)
        steps.append("memory_retrieval")

        tool_results = await self._dependencies.tool_executor.execute(request, plan)
        steps.append("tool_execution")

        context = await self._dependencies.context_assembler.build(
            request, plan, memories, tool_results
        )
        steps.append("context_build")

        logger.debug("Pipeline preparation complete: %s", steps)
        return plan, context, steps
