"""Tests for Context Builder token budgeting and history compression."""

import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from ai.context.service import DefaultContextBuilder, estimate_tokens, _total_tokens
from ai.orchestrator.models import ChatRequest, ChatMessage


# -- Test 1: Token estimation -----------------------------------------------


def test_token_estimation():
    """Validate the character-based token estimation utility."""
    assert estimate_tokens("") == 1, "Empty string should return 1 (min)"
    assert estimate_tokens("abcd") == 1, "4 chars = 1 token"
    assert estimate_tokens("a" * 100) == 25, "100 chars = 25 tokens"
    assert estimate_tokens("a" * 4096) == 1024, "4096 chars = 1024 tokens"
    print("  PASSED: Token estimation")


# -- Test 2: Budget enforcement with history trimming -----------------------


async def test_budget_trims_history():
    """When history is too large, oldest messages should be trimmed."""
    builder = DefaultContextBuilder(token_budget=100)

    # Create a request with a LOT of history (each message ~50 tokens)
    long_history = [
        ChatMessage(role="user" if i % 2 == 0 else "assistant", content="x" * 200)
        for i in range(20)
    ]
    request = ChatRequest(
        conversation_id="c1",
        user_id="u1",
        message="Hello",
        history=long_history,
    )

    messages = await builder.build(request, None, [], [])

    total = _total_tokens(messages)
    assert total <= 100, f"Total tokens ({total}) exceeds budget (100)"
    assert (
        len(messages) < 22
    ), f"History should have been trimmed (got {len(messages)} messages)"
    # System + user message always present
    assert messages[0]["role"] == "system"
    assert messages[-1]["role"] == "user"
    assert messages[-1]["content"] == "Hello"
    print(f"  PASSED: Budget enforcement — {len(messages)} messages, {total} tokens")


# -- Test 3: No trimming when under budget ----------------------------------


async def test_no_trimming_when_under_budget():
    """Short history should not be trimmed."""
    builder = DefaultContextBuilder(token_budget=8192)

    history = [
        ChatMessage(role="user", content="Hi"),
        ChatMessage(role="assistant", content="Hello!"),
    ]
    request = ChatRequest(
        conversation_id="c2",
        user_id="u2",
        message="How are you?",
        history=history,
    )

    messages = await builder.build(request, None, [], [])

    # system + 2 history + user = 4
    assert len(messages) == 4, f"Expected 4 messages, got {len(messages)}"
    print("  PASSED: No trimming when under budget")


# -- Test 4: Memory and tool injection preserved after trimming -------------


async def test_injection_preserved():
    """Memories and tool results should appear in system prompt even after trimming."""
    builder = DefaultContextBuilder(token_budget=200)

    # Create mock memory objects with content attribute
    class MockMemory:
        def __init__(self, content, type="fact"):
            self.content = content
            self.type = type

    memories = [MockMemory("User likes Python", "preference")]
    tool_results = [
        {
            "tool_name": "calculator.compute",
            "success": True,
            "result": 42,
            "error": None,
        }
    ]

    request = ChatRequest(
        conversation_id="c3",
        user_id="u3",
        message="What's my preference?",
        history=[ChatMessage(role="user", content="x" * 300) for _ in range(5)],
    )

    messages = await builder.build(request, None, memories, tool_results)

    system_content = messages[0]["content"]
    assert "User likes Python" in system_content, "Memory should be in system prompt"
    assert (
        "calculator.compute" in system_content
    ), "Tool result should be in system prompt"
    assert messages[-1]["content"] == "What's my preference?"
    print("  PASSED: Memory and tool injection preserved after trimming")


# -- Test 5: Empty history handled gracefully --------------------------------


async def test_empty_history():
    """Requests with no history should work cleanly."""
    builder = DefaultContextBuilder(token_budget=1000)

    request = ChatRequest(
        conversation_id="c4",
        user_id="u4",
        message="Hello world",
    )

    messages = await builder.build(request, None, [], [])
    assert len(messages) == 2  # system + user
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    print("  PASSED: Empty history handled gracefully")


# -- Main -------------------------------------------------------------------


async def main():
    print("--- Token Estimation Tests ---")
    test_token_estimation()

    print("\n--- Context Budget Tests ---")
    await test_budget_trims_history()
    await test_no_trimming_when_under_budget()
    await test_injection_preserved()
    await test_empty_history()

    print("\n All context builder tests passed!")


if __name__ == "__main__":
    asyncio.run(main())
