import asyncio
import sys
import os

# Adjust path to import from workspace root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from ai.orchestrator.models import ChatRequest
from ai.planner.models import ExecutionPlan, PlanStep
from ai.tools import (
    ToolRegistry,
    DefaultToolExecutor,
    CalculatorTool,
    SearchTool,
    GmailTool,
    CalendarTool,
    NewsTool,
)


async def main():
    print("Initializing Tool Registry...")
    registry = ToolRegistry()

    print("\nRegistering Tools...")
    registry.register(CalculatorTool())
    registry.register(SearchTool())
    registry.register(GmailTool())
    registry.register(CalendarTool())
    registry.register(NewsTool())

    print(f"Registered tool names: {[t.name for t in registry.list_tools()]}")
    assert len(registry.list_tools()) == 5, "Error: Should have 5 registered tools"

    print("\nPreparing ToolExecutor & Execution Plan...")
    executor = DefaultToolExecutor(registry)

    # 1. Normal Multi-Step Execution Plan
    plan = ExecutionPlan(
        intent="math_and_search",
        confidence=0.98,
        steps=[
            PlanStep(
                step_id="step_math",
                tool_name="calculator.compute",
                args={"expression": "3 * 5 + 4"},
            ),
            PlanStep(
                step_id="step_search",
                tool_name="search.web",
                args={"query": "weather in Munich"},
            ),
        ],
    )

    request = ChatRequest(
        conversation_id="conv-789",
        user_id="user-789",
        message="Compute 3*5+4 and search weather in Munich.",
    )

    print("Running execute()...")
    results = await executor.execute(request, plan)

    print(f"Executed steps. Results returned: {len(results)}")
    for i, res in enumerate(results):
        print(f"  Result {i+1}:")
        print(f"    Tool: {res['tool_name']}")
        print(f"    Success: {res['success']}")
        print(f"    Output: {res['result']}")
        print(f"    Error: {res['error']}")

    assert results[0]["success"] is True, "Error: Calculator execution failed"
    assert results[0]["result"] == 19, "Error: Calculator math result is wrong"
    assert "Munich" in results[1]["result"], "Error: Search execution output wrong"

    # 2. Error handling test: dangerous expression and unregistered tool
    print("\nTesting Error Handling in execution...")
    erroneous_plan = ExecutionPlan(
        intent="error_test",
        confidence=1.0,
        steps=[
            PlanStep(
                step_id="step_dangerous",
                tool_name="calculator.compute",
                args={"expression": "__import__('os').system('ls')"},
            ),
            PlanStep(step_id="step_missing", tool_name="missing.tool", args={}),
        ],
    )

    err_results = await executor.execute(request, erroneous_plan)

    print(f"Executed erroneous plan. Results returned: {len(err_results)}")
    for i, res in enumerate(err_results):
        print(f"  Result {i+1}:")
        print(f"    Tool: {res['tool_name']}")
        print(f"    Success: {res['success']}")
        print(f"    Output: {res['result']}")
        print(f"    Error: {res['error']}")

    assert (
        err_results[0]["success"] is False
    ), "Error: Dangerous math execution should have failed"
    assert (
        err_results[1]["success"] is False
    ), "Error: Unregistered tool should have failed"

    print("\nSuccess! Tool Registry verified.")


if __name__ == "__main__":
    asyncio.run(main())
