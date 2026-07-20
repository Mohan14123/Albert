"""API endpoints exposing the AI assistant orchestrator."""

from __future__ import annotations

import json
import logging
from functools import lru_cache
from typing import Any, AsyncGenerator
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ..orchestrator import AIOrchestrator, OrchestratorDependencies, ChatRequest
from ..config import AIConfig
from ..gateway import MultiProviderGateway
from ..planner import LLMIntentPlanner
from ..context import DefaultContextBuilder
from ..memory import InMemoryMemoryAdapter
from ..tools import (
    ToolRegistry,
    DefaultToolExecutor,
    CalculatorTool,
    SearchTool,
    GmailTool,
    CalendarTool,
)
from ..responses import DefaultResponseFormatter
from ..prompts import PromptManager

router = APIRouter(prefix="/api/v1", tags=["AI Assistant"])
logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_orchestrator() -> AIOrchestrator:
    """Instantiate and return the AIOrchestrator with all injected dependencies.

    Uses ``lru_cache`` so the full dependency graph (gateway, memory, tools,
    etc.) is built once per process lifetime instead of per-request.
    """
    config = AIConfig.from_env()
    pm = PromptManager()

    gateway = MultiProviderGateway(config)
    planner = LLMIntentPlanner(gateway, pm)
    memory_adapter = InMemoryMemoryAdapter()

    registry = ToolRegistry()
    registry.register(CalculatorTool())
    registry.register(SearchTool())
    registry.register(GmailTool())
    registry.register(CalendarTool())
    executor = DefaultToolExecutor(registry)

    context_builder = DefaultContextBuilder(pm)
    formatter = DefaultResponseFormatter()

    dependencies = OrchestratorDependencies(
        planner=planner,
        memory_retriever=memory_adapter,
        tool_executor=executor,
        context_assembler=context_builder,
        gateway=gateway,
        response_formatter=formatter,
        memory_writer=memory_adapter,
    )

    logger.info("AIOrchestrator initialized (provider=%s)", config.default_provider)
    return AIOrchestrator(dependencies)


@router.post("/chat")
async def chat(
    request: Request,
    payload: ChatRequest,
    accept: str | None = Header(default="application/json"),
    orchestrator: AIOrchestrator = Depends(get_orchestrator),
) -> Any:
    """Coordinate the AI assistant pipeline for complete or streaming chat requests."""

    # 1. Check if the client requested a stream (Server-Sent Events)
    if accept and "text/event-stream" in accept:

        async def event_generator() -> AsyncGenerator[str, None]:
            try:
                async for event in orchestrator.stream(payload):
                    # Yield event in SSE format: event and data lines
                    event_type = event.get("event", "token")
                    data_json = json.dumps(event)
                    yield f"event: {event_type}\ndata: {data_json}\n\n"
            except Exception as e:
                logger.exception("Error in AI streaming endpoint")
                yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    # 2. Return a complete, formatted JSON response
    try:
        response, trace = await orchestrator.respond(payload)
        return {
            "content": response.content,
            "metadata": response.metadata,
            "trace": {
                "conversation_id": trace.conversation_id,
                "completed_steps": trace.completed_steps,
            },
        }
    except Exception as e:
        logger.exception("Error in AI respond endpoint")
        raise HTTPException(
            status_code=500,
            detail={"error": str(e), "message": "Failed to generate AI response"},
        )


@router.get("/health")
async def health() -> dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "healthy", "service": "albert-ai"}


class MemorySearchRequest(BaseModel):
    query: str
    limit: int = 5


@router.post("/memory/search")
async def memory_search(
    request: MemorySearchRequest,
    orchestrator: AIOrchestrator = Depends(get_orchestrator),
) -> Any:
    # Delegate to memory adapter
    memories = await orchestrator._dependencies.memory_retriever.search(  # type: ignore
        request.query, limit=request.limit
    )
    return {
        "results": [
            {"id": str(m.id), "content": m.content, "score": m.relevance_score}
            for m in memories
        ]
    }


class MemoryStoreRequest(BaseModel):
    content: str
    category: str | None = None


@router.post("/memory/store")
async def memory_store(
    request: MemoryStoreRequest,
    orchestrator: AIOrchestrator = Depends(get_orchestrator),
) -> Any:
    memory = await orchestrator._dependencies.memory_writer.store(  # type: ignore
        request.content, request.category
    )
    return {"status": "success", "memory_id": str(memory.id)}


class RagQueryRequest(BaseModel):
    query: str
    top_k: int = 3


@router.post("/rag/query")
async def rag_query(
    request: RagQueryRequest,
    # Inject vector store here ideally, stub for now
) -> Any:
    return {"results": []}


class ToolExecuteRequest(BaseModel):
    tool_name: str
    arguments: dict[str, Any]


@router.post("/tools/execute")
async def tool_execute(
    request: ToolExecuteRequest,
    orchestrator: AIOrchestrator = Depends(get_orchestrator),
) -> Any:
    result = await orchestrator._dependencies.tool_executor.execute(
        request.tool_name, request.arguments
    )
    return {"result": result.content, "is_error": result.is_error}  # type: ignore


@router.get("/chat/history")
async def get_chat_history() -> Any:
    # Stub: history should be fetched from backend DB in a real app,
    # or AI service queries backend
    return {"history": []}


@router.delete("/chat/{chat_id}")
async def delete_chat(chat_id: str) -> Any:
    return {"status": "deleted", "chat_id": chat_id}
