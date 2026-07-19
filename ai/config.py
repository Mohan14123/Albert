"""Main configuration for the AI module, loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from .constants import (
    DEFAULT_OPENAI_MODEL,
    DEFAULT_GEMINI_MODEL,
    DEFAULT_CLAUDE_MODEL,
    DEFAULT_DEEPSEEK_MODEL,
)


@dataclass(frozen=True)
class LLMProviderConfig:
    """Configuration for a specific LLM provider."""

    api_key: str | None = None
    api_base: str | None = None
    default_model: str | None = None


@dataclass(frozen=True)
class AIConfig:
    """Main AI module configuration loaded from environment variables."""

    openai: LLMProviderConfig = field(default_factory=LLMProviderConfig)
    gemini: LLMProviderConfig = field(default_factory=LLMProviderConfig)
    claude: LLMProviderConfig = field(default_factory=LLMProviderConfig)
    deepseek: LLMProviderConfig = field(default_factory=LLMProviderConfig)

    # Active default provider
    default_provider: str = "openai"

    @classmethod
    def from_env(cls) -> "AIConfig":
        """Load configuration from environment variables."""
        openai_key = os.environ.get("OPENAI_API_KEY")
        gemini_key = os.environ.get("GEMINI_API_KEY")
        claude_key = os.environ.get("CLAUDE_API_KEY")
        deepseek_key = os.environ.get("DEEPSEEK_API_KEY")

        return cls(
            openai=LLMProviderConfig(
                api_key=openai_key,
                api_base=os.environ.get("OPENAI_API_BASE"),
                default_model=os.environ.get(
                    "OPENAI_DEFAULT_MODEL", DEFAULT_OPENAI_MODEL
                ),
            ),
            gemini=LLMProviderConfig(
                api_key=gemini_key,
                api_base=os.environ.get("GEMINI_API_BASE"),
                default_model=os.environ.get(
                    "GEMINI_DEFAULT_MODEL", DEFAULT_GEMINI_MODEL
                ),
            ),
            claude=LLMProviderConfig(
                api_key=claude_key,
                api_base=os.environ.get("CLAUDE_API_BASE"),
                default_model=os.environ.get(
                    "CLAUDE_DEFAULT_MODEL", DEFAULT_CLAUDE_MODEL
                ),
            ),
            deepseek=LLMProviderConfig(
                api_key=deepseek_key,
                api_base=os.environ.get("DEEPSEEK_API_BASE"),
                default_model=os.environ.get(
                    "DEEPSEEK_DEFAULT_MODEL", DEFAULT_DEEPSEEK_MODEL
                ),
            ),
            default_provider=os.environ.get("DEFAULT_AI_PROVIDER", "openai"),
        )
