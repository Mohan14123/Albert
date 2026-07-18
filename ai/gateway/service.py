from __future__ import annotations

"""Service layer implementing the LanguageModelGateway contract."""

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


class MultiProviderGateway(LanguageModelGateway):
    """Factory gateway routing context prompts to the configured LLM provider client."""

    def __init__(self, config: AIConfig) -> None:
        """Initialize the gateway using an instance of AIConfig."""
        self._config = config
        self._provider = self._init_provider()

    def _init_provider(self) -> LLMProvider:
        """Instantiate the active provider client, falling back to mock if keys are missing."""
        prov_name = self._config.default_provider.lower()
        
        if prov_name == "openai":
            cfg = self._config.openai
            if not cfg.api_key:
                logger.warning("No OPENAI_API_KEY set — falling back to MockProvider")
                return MockProvider()
            return OpenAICompatibleProvider(
                api_key=cfg.api_key,
                api_base=cfg.api_base or _DEFAULT_OPENAI_API_BASE,
                model=cfg.default_model or DEFAULT_OPENAI_MODEL
            )
        elif prov_name == "deepseek":
            cfg = self._config.deepseek
            if not cfg.api_key:
                logger.warning("No DEEPSEEK_API_KEY set — falling back to MockProvider")
                return MockProvider()
            return OpenAICompatibleProvider(
                api_key=cfg.api_key,
                api_base=cfg.api_base or _DEFAULT_DEEPSEEK_API_BASE,
                model=cfg.default_model or DEFAULT_DEEPSEEK_MODEL
            )
        elif prov_name == "claude":
            cfg = self._config.claude
            if not cfg.api_key:
                logger.warning("No CLAUDE_API_KEY set — falling back to MockProvider")
                return MockProvider()
            return ClaudeProvider(
                api_key=cfg.api_key,
                api_base=cfg.api_base,
                model=cfg.default_model or DEFAULT_CLAUDE_MODEL
            )
        elif prov_name == "gemini":
            cfg = self._config.gemini
            if not cfg.api_key:
                logger.warning("No GEMINI_API_KEY set — falling back to MockProvider")
                return MockProvider()
            return GeminiProvider(
                api_key=cfg.api_key,
                api_base=cfg.api_base,
                model=cfg.default_model or DEFAULT_GEMINI_MODEL
            )
        
        logger.warning("Unknown provider '%s' — falling back to MockProvider", prov_name)
        return MockProvider()

    async def generate(self, context: Any) -> Any:
        """Route generation to the active client."""
        return await self._provider.generate(context)

    def stream(self, context: Any) -> AsyncIterator[Any]:
        """Route streaming to the active client."""
        return self._provider.stream(context)
