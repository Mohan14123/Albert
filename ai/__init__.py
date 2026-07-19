"""Composable AI assistant module.

The package contains framework-agnostic AI pipeline components.  Backend
applications integrate it by supplying adapters for its contracts.
"""

from __future__ import annotations

from .orchestrator import AIOrchestrator, OrchestratorDependencies
from .config import AIConfig, LLMProviderConfig
from .exceptions import (
    AIError,
    GatewayError,
    PlannerError,
    ContextBuilderError,
    MemoryServiceError,
    ToolError,
    ResponseFormatterError,
    ConfigurationError,
)

__all__ = [
    "AIOrchestrator",
    "OrchestratorDependencies",
    "AIConfig",
    "LLMProviderConfig",
    "AIError",
    "GatewayError",
    "PlannerError",
    "ContextBuilderError",
    "MemoryServiceError",
    "ToolError",
    "ResponseFormatterError",
    "ConfigurationError",
]
