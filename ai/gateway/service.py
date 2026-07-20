"""Service layer implementing the LanguageModelGateway contract."""

from __future__ import annotations

import logging
from typing import Any, AsyncIterator
from ..orchestrator.contracts import LanguageModelGateway
from ..config import AIConfig
from ..constants import (
    DEFAULT_OPENAI_MODEL,
    DEFAULT_GEMINI_MODEL,
    DEFAULT_CLAUDE_MODEL,
    DEFAULT_DEEPSEEK_MODEL,
)
from ..exceptions import GatewayError
from .providers import (
    LLMProvider,
    MockProvider,
    OpenAICompatibleProvider,
    ClaudeProvider,
    GeminiProvider,
    _DEFAULT_OPENAI_API_BASE,
    _DEFAULT_DEEPSEEK_API_BASE,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Model Registry — maps provider names to their known model identifiers.
# Extend this dict when new models become available without code changes.
# ---------------------------------------------------------------------------

MODEL_REGISTRY: dict[str, list[str]] = {
    "openai": [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo",
    ],
    "gemini": [
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-2.0-flash",
        "gemini-2.5-pro",
        "gemini-2.5-flash",
    ],
    "claude": [
        "claude-3-5-sonnet",
        "claude-3-5-haiku",
        "claude-3-opus",
        "claude-sonnet-4",
        "claude-opus-4",
    ],
    "deepseek": [
        "deepseek-chat",
        "deepseek-coder",
        "deepseek-reasoner",
    ],
}

# Default provider fallback order (tried in sequence when the primary fails).
_FALLBACK_ORDER: tuple[str, ...] = ("openai", "gemini", "claude", "deepseek")


class MultiProviderGateway(LanguageModelGateway):
    """Factory gateway routing context prompts to the configured LLM provider client.

    Supports automatic fallback: if the primary provider raises a
    :class:`GatewayError`, the gateway will try each configured fallback
    provider in order before giving up.
    """

    def __init__(self, config: AIConfig) -> None:
        """Initialize the gateway using an instance of AIConfig."""
        self._config = config
        self._providers: dict[str, LLMProvider] = self._init_all_providers()
        self._primary = config.default_provider.lower()

    # -- Provider Initialization -------------------------------------------------

    def _init_all_providers(self) -> dict[str, LLMProvider]:
        """Build a dict of *all* providers that have valid API keys configured."""
        providers: dict[str, LLMProvider] = {}

        # OpenAI
        cfg = self._config.openai
        if cfg.api_key:
            providers["openai"] = OpenAICompatibleProvider(
                api_key=cfg.api_key,
                api_base=cfg.api_base or _DEFAULT_OPENAI_API_BASE,
                model=cfg.default_model or DEFAULT_OPENAI_MODEL,
            )

        # DeepSeek (OpenAI-compatible)
        cfg = self._config.deepseek
        if cfg.api_key:
            providers["deepseek"] = OpenAICompatibleProvider(
                api_key=cfg.api_key,
                api_base=cfg.api_base or _DEFAULT_DEEPSEEK_API_BASE,
                model=cfg.default_model or DEFAULT_DEEPSEEK_MODEL,
            )

        # Claude
        cfg = self._config.claude
        if cfg.api_key:
            providers["claude"] = ClaudeProvider(
                api_key=cfg.api_key,
                api_base=cfg.api_base,
                model=cfg.default_model or DEFAULT_CLAUDE_MODEL,
            )

        # Gemini
        cfg = self._config.gemini
        if cfg.api_key:
            providers["gemini"] = GeminiProvider(
                api_key=cfg.api_key,
                api_base=cfg.api_base,
                model=cfg.default_model or DEFAULT_GEMINI_MODEL,
            )

        # If no real provider is configured, add the mock so the pipeline boots.
        if not providers:
            logger.warning("No LLM API keys configured — falling back to MockProvider")
            providers["mock"] = MockProvider()

        return providers

    def _fallback_sequence(self) -> list[str]:
        """Return an ordered list of provider names to attempt, primary first."""
        sequence = [self._primary] if self._primary in self._providers else []
        for name in _FALLBACK_ORDER:
            if name in self._providers and name not in sequence:
                sequence.append(name)
        # Include mock if it's the only option
        if "mock" in self._providers and "mock" not in sequence:
            sequence.append("mock")
        return sequence

    # -- LanguageModelGateway contract ------------------------------------------

    async def generate(self, context: Any) -> Any:
        """Route generation to the active client with automatic fallback."""
        sequence = self._fallback_sequence()
        last_error: Exception | None = None
        for name in sequence:
            provider = self._providers[name]
            try:
                logger.debug("Attempting generate via '%s'", name)
                result = await provider.generate(context)
                return result
            except Exception as exc:
                last_error = exc
                logger.warning("Provider '%s' generate failed: %s", name, exc)
        raise GatewayError(
            f"All providers failed. Last error: {last_error}"
        ) from last_error

    def stream(self, context: Any) -> AsyncIterator[Any]:
        """Route streaming to the primary provider (no fallback during streaming)."""
        sequence = self._fallback_sequence()
        if not sequence:
            raise GatewayError("No providers available for streaming")
        provider = self._providers[sequence[0]]
        return provider.stream(context)

    # -- Introspection helpers ---------------------------------------------------

    def available_providers(self) -> list[str]:
        """Return names of providers that have been successfully initialized."""
        return list(self._providers.keys())

    @staticmethod
    def registered_models(provider: str) -> list[str]:
        """Return the known model identifiers for *provider*."""
        return list(MODEL_REGISTRY.get(provider.lower(), []))
