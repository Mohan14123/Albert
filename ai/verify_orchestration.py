import asyncio
import sys
import os

# Adjust path to import from workspace root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai.config import AIConfig
from ai.orchestrator.models import ChatRequest, ChatMessage
from ai.orchestrator.service import AIOrchestrator, OrchestratorDependencies
from ai.gateway.service import MultiProviderGateway
from ai.planner.service import LLMIntentPlanner
from ai.memory.service import InMemoryMemoryAdapter
from ai.tools.service import ToolRegistry, DefaultToolExecutor, CalculatorTool, SearchTool
from ai.context.service import DefaultContextBuilder
from ai.responses.service import DefaultResponseFormatter

async def main():
    print("--- Initializing AI Components ---")
    
    # 1. Config (using MockProvider because API keys are not required)
    config = AIConfig(default_provider="mock")
    
    # 2. LLM Gateway
    gateway = MultiProviderGateway(config)
    
    # 3. Intent Planner
    planner = LLMIntentPlanner(gateway)
    
    # 4. Memory Adapter
    memory_adapter = InMemoryMemoryAdapter()
    
    # 5. Tool Executor & Registry
    registry = ToolRegistry()
    registry.register(CalculatorTool())
    registry.register(SearchTool())
    tool_executor = DefaultToolExecutor(registry)
    
    # 6. Context Builder
    context_assembler = DefaultContextBuilder()
    
    # 7. Response Formatter
    response_formatter = DefaultResponseFormatter()
    
    # Bundle dependencies
    deps = OrchestratorDependencies(
        planner=planner,
        memory_retriever=memory_adapter,
        tool_executor=tool_executor,
        context_assembler=context_assembler,
        gateway=gateway,
        response_formatter=response_formatter,
        memory_writer=memory_adapter
    )
    
    orchestrator = AIOrchestrator(deps)
    
    print("\n--- Testing Non-Streaming respond() ---")
    request = ChatRequest(
        conversation_id="conv-123",
        user_id="user-123",
        message="Compute 5 * 5 and remember that my favorite color is indigo",
        history=[
            ChatMessage(role="user", content="Hi!"),
            ChatMessage(role="assistant", content="Hello! How can I help you today?")
        ]
    )
    
    response, trace = await orchestrator.respond(request)
    print(f"Response content:\n{response.content}")
    print(f"Response metadata: {response.metadata}")
    print(f"Orchestration Trace steps: {trace.completed_steps}")
    
    # Verify that memory writer saved the fact "my favorite color is indigo"
    print("\n--- Verifying Memory Persistence ---")
    memories = await memory_adapter.retrieve(
        ChatRequest(conversation_id="conv-123", user_id="user-123", message="color"),
        None
    )
    print(f"Retrieved memories for query 'color':")
    for m in memories:
        print(f"  - [{m.type}] {m.content}")
    
    assert any("indigo" in m.content for m in memories), "Error: Memory was not saved successfully!"
    
    print("\n--- Testing Streaming stream() ---")
    stream_request = ChatRequest(
        conversation_id="conv-123",
        user_id="user-123",
        message="Help me with streaming response"
    )
    
    print("Received streaming tokens:")
    async for chunk in orchestrator.stream(stream_request):
        if chunk.get("event") == "token":
            print(chunk.get("delta"), end="", flush=True)
    print()

    print("\nAll integration tests passed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
