"""Implementations of LLM API clients using python's standard libraries."""

from __future__ import annotations

import json
import logging
import urllib.request
import urllib.error
import asyncio
import time
import random
from abc import ABC, abstractmethod
from typing import Any, AsyncIterator

from ..constants import ROLE_USER, ROLE_ASSISTANT, ROLE_SYSTEM
from ..exceptions import GatewayError

logger = logging.getLogger(__name__)

# Default API configuration constants
_DEFAULT_OPENAI_API_BASE = "https://api.openai.com/v1"
_DEFAULT_DEEPSEEK_API_BASE = "https://api.deepseek.com/v1"
_DEFAULT_CLAUDE_API_BASE = "https://api.anthropic.com/v1"
_DEFAULT_GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"
_DEFAULT_ANTHROPIC_VERSION = "2023-06-01"
_DEFAULT_TIMEOUT = 30
_DEFAULT_MAX_TOKENS = 1024


# Retry configuration defaults
_DEFAULT_MAX_RETRIES = 3
_DEFAULT_RETRY_BASE_DELAY = 1.0  # seconds
_DEFAULT_RETRY_MAX_DELAY = 30.0  # seconds
_RETRYABLE_HTTP_CODES = {429, 500, 502, 503, 504}


def _retry_request(
    make_request_fn,
    payload: dict,
    *,
    max_retries: int = _DEFAULT_MAX_RETRIES,
    base_delay: float = _DEFAULT_RETRY_BASE_DELAY,
    max_delay: float = _DEFAULT_RETRY_MAX_DELAY,
) -> dict:
    """Execute an HTTP request function with exponential backoff and jitter.

    Retries on transient HTTP errors (429, 5xx) and connection failures.
    Non-retryable errors (4xx except 429) are raised immediately.
    """
    last_exception: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            return make_request_fn(payload)
        except GatewayError as exc:
            last_exception = exc
            error_msg = str(exc)
            # Check if HTTP error code is retryable
            is_retryable = False
            for code in _RETRYABLE_HTTP_CODES:
                if f"HTTP error {code}" in error_msg or f"error {code}" in error_msg:
                    is_retryable = True
                    break
            # Also retry on connection failures
            if "connection failed" in error_msg.lower() or "API connection failed" in error_msg:
                is_retryable = True

            if not is_retryable or attempt >= max_retries:
                raise

            delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
            logger.warning(
                "Request failed (attempt %d/%d), retrying in %.1fs: %s",
                attempt + 1, max_retries + 1, delay, exc,
            )
            time.sleep(delay)
        except Exception as exc:
            # Non-GatewayError exceptions (unexpected) — retry on connection issues
            last_exception = exc
            if attempt >= max_retries:
                raise GatewayError(f"Request failed after {max_retries + 1} attempts: {exc}") from exc
            delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
            logger.warning(
                "Unexpected error (attempt %d/%d), retrying in %.1fs: %s",
                attempt + 1, max_retries + 1, delay, exc,
            )
            time.sleep(delay)
    # Should never reach here, but just in case
    raise GatewayError(f"Request failed after {max_retries + 1} attempts") from last_exception


class LLMProvider(ABC):
    """Abstract interface for a specific LLM model client."""

    @abstractmethod
    async def generate(self, context: Any) -> dict[str, Any]:
        """Generate complete non-streaming response."""
        pass

    @abstractmethod
    def stream(self, context: Any) -> AsyncIterator[dict[str, Any]]:
        """Yield streaming chunks."""
        pass


class MockProvider(LLMProvider):
    """Fallback mock client for offline local testing and integration."""

    async def generate(self, context: Any) -> dict[str, Any]:
        prompt = str(context)
        content = f"[Mock LLM response for context: '{prompt[:40]}...']"
        return {
            "content": content,
            "provider": "mock",
            "provider_metadata": {
                "model": "mock-v1",
                "usage": {
                    "prompt_tokens": len(prompt) // 4,
                    "completion_tokens": len(content) // 4,
                    "total_tokens": (len(prompt) + len(content)) // 4,
                }
            }
        }

    async def stream(self, context: Any) -> AsyncIterator[dict[str, Any]]:
        prompt = str(context)
        chunks = [
            "[Mock",
            " LLM",
            " streaming",
            " response",
            " for",
            f" context: '{prompt[:30]}...']",
        ]
        for chunk in chunks:
            await asyncio.sleep(0.05)
            yield {"delta": chunk, "provider": "mock"}


class OpenAICompatibleProvider(LLMProvider):
    """Base client for OpenAI and DeepSeek compatible APIs."""

    def __init__(self, api_key: str, api_base: str, model: str):
        self.api_key = api_key
        self.api_base = api_base
        self.model = model

    def _make_request(self, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.api_base}/chat/completions"
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=_DEFAULT_TIMEOUT) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            raise GatewayError(f"HTTP error {e.code}: {err_body}") from e
        except Exception as e:
            raise GatewayError(f"API connection failed: {e}") from e

    async def generate(self, context: Any) -> dict[str, Any]:
        messages = self._normalize_context(context)
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }
        res = await asyncio.to_thread(_retry_request, self._make_request, payload)
        try:
            return {
                "content": res["choices"][0]["message"]["content"],
                "provider_metadata": {
                    "model": res.get("model"),
                    "usage": res.get("usage"),
                },
            }
        except (KeyError, IndexError) as e:
            raise GatewayError(f"Malformed OpenAI-style response: {e}") from e

    async def stream(self, context: Any) -> AsyncIterator[dict[str, Any]]:
        messages = self._normalize_context(context)
        payload = {"model": self.model, "messages": messages, "stream": True}

        queue: asyncio.Queue[dict[str, Any] | Exception | None] = asyncio.Queue()
        loop = asyncio.get_running_loop()

        def run_stream() -> None:
            url = f"{self.api_base}/chat/completions"
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=_DEFAULT_TIMEOUT) as response:
                    for line in response:
                        decoded = line.decode("utf-8").strip()
                        if not decoded:
                            continue
                        if decoded == "data: [DONE]":
                            break
                        if decoded.startswith("data: "):
                            data_str = decoded[len("data: ") :]
                            try:
                                data = json.loads(data_str)
                                delta = data["choices"][0]["delta"].get("content", "")
                                if delta:
                                    loop.call_soon_threadsafe(
                                        queue.put_nowait, {"delta": delta}
                                    )
                            except (
                                json.JSONDecodeError,
                                KeyError,
                                IndexError,
                            ) as parse_err:
                                logger.debug(
                                    "Skipping unparseable stream chunk: %s", parse_err
                                )
            except urllib.error.HTTPError as e:
                err_body = e.read().decode("utf-8")
                loop.call_soon_threadsafe(
                    queue.put_nowait,
                    GatewayError(f"HTTP stream error {e.code}: {err_body}"),
                )
            except Exception as e:
                loop.call_soon_threadsafe(
                    queue.put_nowait, GatewayError(f"Stream connection failed: {e}")
                )
            finally:
                loop.call_soon_threadsafe(queue.put_nowait, None)

        asyncio.create_task(asyncio.to_thread(run_stream))

        while True:
            item = await queue.get()
            if item is None:
                break
            if isinstance(item, Exception):
                raise item
            yield item

    def _normalize_context(self, context: Any) -> list[dict[str, str]]:
        if isinstance(context, list):
            return context
        if isinstance(context, str):
            return [{"role": ROLE_USER, "content": context}]
        return [{"role": ROLE_USER, "content": str(context)}]


class ClaudeProvider(LLMProvider):
    """Client for Anthropic Claude API."""

    def __init__(
        self,
        api_key: str,
        api_base: str | None = None,
        model: str = "claude-3-5-sonnet",
    ):
        self.api_key = api_key
        self.api_base = api_base or _DEFAULT_CLAUDE_API_BASE
        self.model = model

    def _make_request(self, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.api_base}/messages"
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": _DEFAULT_ANTHROPIC_VERSION,
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=_DEFAULT_TIMEOUT) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            raise GatewayError(f"Anthropic HTTP error {e.code}: {err_body}") from e
        except Exception as e:
            raise GatewayError(f"Anthropic API connection failed: {e}") from e

    def _extract_system_and_messages(
        self, context: Any
    ) -> tuple[str | None, list[dict[str, str]]]:
        """Separate system messages from user/assistant messages.

        Claude API requires the system prompt as a top-level parameter,
        not as a message with role 'system'.
        """
        raw_messages = self._normalize_context(context)
        system_parts: list[str] = []
        filtered: list[dict[str, str]] = []
        for msg in raw_messages:
            if msg.get("role") == ROLE_SYSTEM:
                system_parts.append(msg.get("content", ""))
            else:
                filtered.append(msg)
        system_text = "\n".join(system_parts) if system_parts else None
        return system_text, filtered

    async def generate(self, context: Any) -> dict[str, Any]:
        system_text, messages = self._extract_system_and_messages(context)
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "max_tokens": _DEFAULT_MAX_TOKENS,
            "stream": False,
        }
        if system_text:
            payload["system"] = system_text

        res = await asyncio.to_thread(_retry_request, self._make_request, payload)
        try:
            return {
                "content": res["content"][0]["text"],
                "provider_metadata": {
                    "model": res.get("model"),
                    "usage": res.get("usage"),
                },
            }
        except (KeyError, IndexError) as e:
            raise GatewayError(f"Malformed Anthropic response: {e}") from e

    async def stream(self, context: Any) -> AsyncIterator[dict[str, Any]]:
        system_text, messages = self._extract_system_and_messages(context)
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "max_tokens": _DEFAULT_MAX_TOKENS,
            "stream": True,
        }
        if system_text:
            payload["system"] = system_text

        queue: asyncio.Queue[dict[str, Any] | Exception | None] = asyncio.Queue()
        loop = asyncio.get_running_loop()

        def run_stream() -> None:
            url = f"{self.api_base}/messages"
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": _DEFAULT_ANTHROPIC_VERSION,
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=_DEFAULT_TIMEOUT) as response:
                    current_event = None
                    for line in response:
                        decoded = line.decode("utf-8").strip()
                        if not decoded:
                            continue
                        if decoded.startswith("event: "):
                            current_event = decoded[len("event: ") :]
                        elif decoded.startswith("data: "):
                            data_str = decoded[len("data: ") :]
                            if current_event == "content_block_delta":
                                try:
                                    data = json.loads(data_str)
                                    delta = data["delta"].get("text", "")
                                    if delta:
                                        loop.call_soon_threadsafe(
                                            queue.put_nowait, {"delta": delta}
                                        )
                                except (json.JSONDecodeError, KeyError) as parse_err:
                                    logger.debug(
                                        "Skipping unparseable Claude chunk: %s",
                                        parse_err,
                                    )
            except urllib.error.HTTPError as e:
                err_body = e.read().decode("utf-8")
                loop.call_soon_threadsafe(
                    queue.put_nowait,
                    GatewayError(f"Anthropic HTTP stream error {e.code}: {err_body}"),
                )
            except Exception as e:
                loop.call_soon_threadsafe(
                    queue.put_nowait,
                    GatewayError(f"Anthropic stream connection failed: {e}"),
                )
            finally:
                loop.call_soon_threadsafe(queue.put_nowait, None)

        asyncio.create_task(asyncio.to_thread(run_stream))

        while True:
            item = await queue.get()
            if item is None:
                break
            if isinstance(item, Exception):
                raise item
            yield item

    def _normalize_context(self, context: Any) -> list[dict[str, str]]:
        if isinstance(context, list):
            return context
        return [{"role": ROLE_USER, "content": str(context)}]


class GeminiProvider(LLMProvider):
    """Client for Google Gemini API."""

    def __init__(
        self, api_key: str, api_base: str | None = None, model: str = "gemini-1.5-pro"
    ):
        self.api_key = api_key
        self.api_base = api_base or _DEFAULT_GEMINI_API_BASE
        self.model = model

    def _make_request(self, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.api_base}/models/{self.model}:generateContent?key={self.api_key}"
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=_DEFAULT_TIMEOUT) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            raise GatewayError(f"Gemini HTTP error {e.code}: {err_body}") from e
        except Exception as e:
            raise GatewayError(f"Gemini API connection failed: {e}") from e

    def _extract_system_and_contents(
        self, context: Any
    ) -> tuple[str | None, list[dict[str, Any]]]:
        """Separate system instructions from user/model messages.

        Gemini API requires system instructions via the top-level
        ``systemInstruction`` field, not as a content role.
        """
        raw_messages = self._normalize_context(context)
        system_parts: list[str] = []
        filtered: list[dict[str, Any]] = []
        for msg in raw_messages:
            if msg.get("role") == ROLE_SYSTEM:
                system_parts.append(msg.get("content", ""))
            else:
                # Convert to Gemini format
                role = "model" if msg.get("role") == ROLE_ASSISTANT else ROLE_USER
                filtered.append(
                    {"role": role, "parts": [{"text": msg.get("content", "")}]}
                )
        system_text = "\n".join(system_parts) if system_parts else None
        return system_text, filtered

    async def generate(self, context: Any) -> dict[str, Any]:
        system_text, contents = self._extract_system_and_contents(context)
        payload: dict[str, Any] = {"contents": contents}
        if system_text:
            payload["systemInstruction"] = {"parts": [{"text": system_text}]}

        res = await asyncio.to_thread(_retry_request, self._make_request, payload)
        try:
            return {
                "content": res["candidates"][0]["content"]["parts"][0]["text"],
                "provider_metadata": {"model": self.model},
            }
        except (KeyError, IndexError) as e:
            raise GatewayError(f"Malformed Gemini response: {e}") from e

    async def stream(self, context: Any) -> AsyncIterator[dict[str, Any]]:
        """Stream from Gemini's streamGenerateContent endpoint.

        Gemini streams a JSON array of candidate objects. We read the entire
        response and parse the JSON array, then yield text parts as deltas.
        If streaming parsing fails, falls back to a non-streaming generate call.
        """
        system_text, contents = self._extract_system_and_contents(context)
        payload: dict[str, Any] = {"contents": contents}
        if system_text:
            payload["systemInstruction"] = {"parts": [{"text": system_text}]}

        queue: asyncio.Queue[dict[str, Any] | Exception | None] = asyncio.Queue()
        loop = asyncio.get_running_loop()

        def run_stream() -> None:
            url = f"{self.api_base}/models/{self.model}:streamGenerateContent?alt=sse&key={self.api_key}"
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=_DEFAULT_TIMEOUT) as response:
                    for line in response:
                        decoded = line.decode("utf-8").strip()
                        if not decoded:
                            continue
                        if decoded.startswith("data: "):
                            data_str = decoded[len("data: ") :]
                            try:
                                data = json.loads(data_str)
                                # Extract text from candidates[0].content.parts[0].text
                                candidates = data.get("candidates", [])
                                if candidates:
                                    parts = (
                                        candidates[0]
                                        .get("content", {})
                                        .get("parts", [])
                                    )
                                    for part in parts:
                                        text = part.get("text", "")
                                        if text:
                                            loop.call_soon_threadsafe(
                                                queue.put_nowait, {"delta": text}
                                            )
                            except (
                                json.JSONDecodeError,
                                KeyError,
                                IndexError,
                            ) as parse_err:
                                logger.debug(
                                    "Skipping unparseable Gemini chunk: %s", parse_err
                                )
            except urllib.error.HTTPError as e:
                err_body = e.read().decode("utf-8")
                loop.call_soon_threadsafe(
                    queue.put_nowait,
                    GatewayError(f"Gemini stream HTTP error {e.code}: {err_body}"),
                )
            except Exception as e:
                # Fallback: generate non-streaming and chunk the result
                logger.warning(
                    "Gemini SSE stream failed, falling back to chunked generate: %s", e
                )
                try:
                    # Use generateContent (non-streaming) and split into chunks
                    gen_url = f"{self.api_base}/models/{self.model}:generateContent?key={self.api_key}"
                    gen_req = urllib.request.Request(
                        gen_url,
                        data=json.dumps(payload).encode("utf-8"),
                        headers={"Content-Type": "application/json"},
                        method="POST",
                    )
                    with urllib.request.urlopen(
                        gen_req, timeout=_DEFAULT_TIMEOUT
                    ) as gen_resp:
                        res = json.loads(gen_resp.read().decode("utf-8"))
                    text = res["candidates"][0]["content"]["parts"][0]["text"]
                    chunk_size = 20
                    for i in range(0, len(text), chunk_size):
                        loop.call_soon_threadsafe(
                            queue.put_nowait, {"delta": text[i : i + chunk_size]}
                        )
                except Exception as fallback_err:
                    loop.call_soon_threadsafe(
                        queue.put_nowait,
                        GatewayError(
                            f"Gemini stream fallback also failed: {fallback_err}"
                        ),
                    )
            finally:
                loop.call_soon_threadsafe(queue.put_nowait, None)

        asyncio.create_task(asyncio.to_thread(run_stream))

        while True:
            item = await queue.get()
            if item is None:
                break
            if isinstance(item, Exception):
                raise item
            yield item

    def _normalize_context(self, context: Any) -> list[dict[str, Any]]:
        """Normalize input context to a list of message dicts.

        Accepts either a list of OpenAI-format message dicts (with ``role``
        and ``content`` keys) or a plain string.  System-role messages are
        preserved here and extracted later by ``_extract_system_and_contents``.
        """
        if isinstance(context, list):
            return context
        return [{"role": ROLE_USER, "content": str(context)}]
