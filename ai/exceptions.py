"""Domain exception classes for the AI module."""

from __future__ import annotations


class AIError(Exception):
    """Base exception for all errors in the AI module."""

    pass


class GatewayError(AIError):
    """Raised when there is an issue with the Language Model Gateway."""

    pass


class PlannerError(AIError):
    """Raised when the Intent Planner fails to generate or validate a plan."""

    pass


class ContextBuilderError(AIError):
    """Raised when context building fails."""

    pass


class MemoryServiceError(AIError):
    """Raised when memory retrieval or writing fails."""

    pass


class ToolError(AIError):
    """Raised when tool execution fails."""

    pass


class ResponseFormatterError(AIError):
    """Raised when response formatting fails."""

    pass


class ConfigurationError(AIError):
    """Raised when config parameters are invalid or missing."""

    pass
