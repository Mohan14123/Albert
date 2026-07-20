"""Tests for Intent Planner validation, self-correction retry, and tool filtering."""

import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from ai.planner.service import LLMIntentPlanner
from ai.orchestrator.contracts import LanguageModelGateway
from ai.orchestrator.models import ChatRequest


# -- Fake gateway for testing -----------------------------------------------


class FakeGateway(LanguageModelGateway):
    """Gateway stub that returns predetermined responses for testing."""

    def __init__(self, responses: list[dict]):
        self._responses = list(responses)
        self._call_count = 0

    async def generate(self, context):
        idx = min(self._call_count, len(self._responses) - 1)
        self._call_count += 1
        return self._responses[idx]

    def stream(self, context):
        raise NotImplementedError


# -- Test 1: Valid JSON plan -----------------------------------------------


async def test_valid_json_plan():
    """Planner should parse a well-formed JSON plan."""
    gateway = FakeGateway(
        [
            {
                "content": '{"intent": "search", "confidence": 0.95, "steps": [{"step_id": "s1", "tool_name": "search.web", "args": {"query": "weather"}}]}'
            }
        ]
    )
    planner = LLMIntentPlanner(gateway)
    request = ChatRequest(conversation_id="c1", user_id="u1", message="weather?")

    plan = await planner.create_plan(request)
    assert plan.intent == "search"
    assert plan.confidence == 0.95
    assert len(plan.steps) == 1
    assert plan.steps[0].tool_name == "search.web"
    print("  PASSED: Valid JSON plan parsing")


# -- Test 2: Self-correction on malformed JSON ------------------------------


async def test_self_correction_retry():
    """Planner should retry when LLM returns invalid JSON, then succeed."""
    gateway = FakeGateway(
        [
            {"content": "This is not JSON at all"},  # attempt 1: fails
            {"content": "{broken json"},  # attempt 2: fails
            {
                "content": '{"intent": "chat", "confidence": 0.8, "steps": []}'
            },  # attempt 3: OK
        ]
    )
    planner = LLMIntentPlanner(gateway)
    request = ChatRequest(conversation_id="c2", user_id="u2", message="hello")

    plan = await planner.create_plan(request)
    assert plan.intent == "chat"
    assert plan.confidence == 0.8
    assert len(plan.steps) == 0
    assert gateway._call_count == 3, f"Expected 3 attempts, got {gateway._call_count}"
    print("  PASSED: Self-correction retry succeeds on 3rd attempt")


# -- Test 3: Fallback after all retries exhausted --------------------------


async def test_fallback_on_all_retries_exhausted():
    """After MAX_PLAN_RETRIES+1 failures, planner should fallback to direct_chat."""
    gateway = FakeGateway(
        [
            {"content": "not json 1"},
            {"content": "not json 2"},
            {"content": "not json 3"},
            {"content": "not json 4"},  # will never reach with max_retries=2
        ]
    )
    planner = LLMIntentPlanner(gateway)
    request = ChatRequest(conversation_id="c3", user_id="u3", message="test")

    plan = await planner.create_plan(request)
    assert plan.intent == "direct_chat"
    assert plan.confidence == 0.3
    assert len(plan.steps) == 0
    print("  PASSED: Fallback to direct_chat after all retries exhausted")


# -- Test 4: Unknown tool filtering ----------------------------------------


async def test_unknown_tool_filtering():
    """When known_tool_names is provided, unknown tools should be filtered out."""
    gateway = FakeGateway(
        [
            {
                "content": '{"intent": "multi", "confidence": 0.9, "steps": [{"step_id": "s1", "tool_name": "search.web", "args": {"query": "test"}}, {"step_id": "s2", "tool_name": "nonexistent.tool", "args": {}}]}'
            }
        ]
    )
    planner = LLMIntentPlanner(
        gateway,
        known_tool_names={"search.web", "calculator.compute"},
    )
    request = ChatRequest(conversation_id="c4", user_id="u4", message="test")

    plan = await planner.create_plan(request)
    assert (
        len(plan.steps) == 1
    ), f"Expected 1 step (unknown filtered out), got {len(plan.steps)}"
    assert plan.steps[0].tool_name == "search.web"
    print("  PASSED: Unknown tool filtering")


# -- Test 5: Non-dict args defaulting -------------------------------------


async def test_non_dict_args_default():
    """Plan steps with non-dict args should default to empty dict."""
    gateway = FakeGateway(
        [
            {
                "content": '{"intent": "test", "confidence": 1.0, "steps": [{"step_id": "s1", "tool_name": "search.web", "args": "invalid_args_string"}]}'
            }
        ]
    )
    planner = LLMIntentPlanner(gateway)
    request = ChatRequest(conversation_id="c5", user_id="u5", message="test")

    plan = await planner.create_plan(request)
    assert len(plan.steps) == 1
    assert plan.steps[0].args == {}, f"Expected empty dict, got {plan.steps[0].args}"
    print("  PASSED: Non-dict args defaulting to empty dict")


# -- Test 6: Markdown code block cleanup -----------------------------------


async def test_markdown_code_block_cleanup():
    """Planner should strip ```json code blocks from LLM response."""
    json_plan = '{"intent": "code_cleanup", "confidence": 0.99, "steps": []}'
    gateway = FakeGateway([{"content": f"```json\n{json_plan}\n```"}])
    planner = LLMIntentPlanner(gateway)
    request = ChatRequest(conversation_id="c6", user_id="u6", message="test")

    plan = await planner.create_plan(request)
    assert plan.intent == "code_cleanup"
    print("  PASSED: Markdown code block cleanup")


# -- Test 7: Mock provider handled gracefully ------------------------------


async def test_mock_provider_detection():
    """Mock provider responses starting with [Mock LLM should return mock plan."""
    gateway = FakeGateway([{"content": "[Mock LLM response for context: 'test...']"}])
    planner = LLMIntentPlanner(gateway)
    request = ChatRequest(conversation_id="c7", user_id="u7", message="test")

    plan = await planner.create_plan(request)
    assert plan.intent == "mock_chat"
    assert plan.confidence == 1.0
    assert plan.steps[0].tool_name == "mock.tool"
    print("  PASSED: Mock provider detection")


# -- Main -------------------------------------------------------------------


async def main():
    print("--- Planner Plan Parsing Tests ---")
    await test_valid_json_plan()
    await test_markdown_code_block_cleanup()
    await test_mock_provider_detection()

    print("\n--- Planner Self-Correction Tests ---")
    await test_self_correction_retry()
    await test_fallback_on_all_retries_exhausted()

    print("\n--- Planner Validation Tests ---")
    await test_unknown_tool_filtering()
    await test_non_dict_args_default()

    print("\n All planner tests passed!")


if __name__ == "__main__":
    asyncio.run(main())
