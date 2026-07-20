"""Tests for LLM Gateway retry logic, model registry, and provider fallback."""

import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from ai.config import AIConfig
from ai.gateway.service import MultiProviderGateway, MODEL_REGISTRY
from ai.gateway.providers import (
    _retry_request,
    MockProvider,
    GatewayError,
)


# -- Test 1: _retry_request with transient failures -------------------------


def test_retry_on_transient_failure():
    """Simulate transient GatewayError (500) that succeeds after retries."""
    call_count = 0

    def flaky_request(payload):
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise GatewayError(
                f"HTTP error 500: Internal Server Error (attempt {call_count})"
            )
        return {"content": "success", "usage": {}}

    result = _retry_request(
        flaky_request,
        {},
        max_retries=3,
        base_delay=0.01,  # fast for testing
        max_delay=0.05,
    )
    assert result["content"] == "success", "Expected successful result after retries"
    assert call_count == 3, f"Expected 3 attempts, got {call_count}"
    print("  PASSED: Retry on transient 500 errors")


def test_no_retry_on_non_retryable():
    """Non-retryable errors (e.g. 401) should raise immediately."""
    call_count = 0

    def auth_fail(payload):
        nonlocal call_count
        call_count += 1
        raise GatewayError("HTTP error 401: Unauthorized")

    try:
        _retry_request(
            auth_fail,
            {},
            max_retries=3,
            base_delay=0.01,
            max_delay=0.05,
        )
        assert False, "Should have raised"
    except GatewayError as e:
        assert "401" in str(e)
        assert (
            call_count == 1
        ), f"Should NOT have retried, but got {call_count} attempts"
    print("  PASSED: No retry on non-retryable 401 errors")


def test_retry_on_rate_limit():
    """429 (rate limit) should be retried."""
    call_count = 0

    def rate_limited(payload):
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise GatewayError("HTTP error 429: Too Many Requests")
        return {"content": "ok"}

    result = _retry_request(
        rate_limited,
        {},
        max_retries=3,
        base_delay=0.01,
        max_delay=0.05,
    )
    assert result["content"] == "ok"
    assert call_count == 2
    print("  PASSED: Retry on 429 rate limit errors")


def test_retry_exhaustion():
    """All retries exhausted should raise the final error."""

    def always_fail(payload):
        raise GatewayError("HTTP error 503: Service Unavailable")

    try:
        _retry_request(
            always_fail,
            {},
            max_retries=2,
            base_delay=0.01,
            max_delay=0.05,
        )
        assert False, "Should have raised"
    except GatewayError as e:
        assert "503" in str(e)
    print("  PASSED: Raises after all retries exhausted")


# -- Test 2: Model registry ------------------------------------------------


def test_model_registry():
    """Validate that the model registry contains expected entries."""
    assert "openai" in MODEL_REGISTRY
    assert "gemini" in MODEL_REGISTRY
    assert "claude" in MODEL_REGISTRY
    assert "deepseek" in MODEL_REGISTRY
    assert "gpt-4o" in MODEL_REGISTRY["openai"]
    assert "gemini-1.5-pro" in MODEL_REGISTRY["gemini"]

    # Test the static helper
    models = MultiProviderGateway.registered_models("openai")
    assert "gpt-4o" in models
    assert MultiProviderGateway.registered_models("nonexistent") == []
    print("  PASSED: Model registry validation")


# -- Test 3: Provider fallback ----------------------------------------------


async def test_provider_fallback():
    """When no API keys are set, MockProvider should be used as fallback."""
    config = AIConfig(default_provider="openai")  # No API keys set
    gateway = MultiProviderGateway(config)

    assert "mock" in gateway.available_providers(), "MockProvider should be available"

    result = await gateway.generate("Hello")
    assert "content" in result
    assert "[Mock LLM" in result["content"]
    print("  PASSED: Provider fallback to MockProvider")


# -- Test 4: Usage tracking in MockProvider ---------------------------------


async def test_mock_usage_tracking():
    """MockProvider should return token usage estimates."""
    provider = MockProvider()
    result = await provider.generate("test prompt for usage tracking")

    assert "provider_metadata" in result
    usage = result["provider_metadata"]["usage"]
    assert "prompt_tokens" in usage
    assert "completion_tokens" in usage
    assert "total_tokens" in usage
    assert usage["total_tokens"] == usage["prompt_tokens"] + usage["completion_tokens"]
    print("  PASSED: MockProvider usage tracking")


# -- Main -------------------------------------------------------------------


async def main():
    print("--- Gateway Retry Logic Tests ---")
    test_retry_on_transient_failure()
    test_no_retry_on_non_retryable()
    test_retry_on_rate_limit()
    test_retry_exhaustion()

    print("\n--- Model Registry Tests ---")
    test_model_registry()

    print("\n--- Provider Fallback Tests ---")
    await test_provider_fallback()

    print("\n--- Usage Tracking Tests ---")
    await test_mock_usage_tracking()

    print("\n All gateway tests passed!")


if __name__ == "__main__":
    asyncio.run(main())
