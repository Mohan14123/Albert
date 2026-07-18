"""API layer exposing the AI orchestrator via HTTP endpoints."""

from __future__ import annotations

from .routes import router

__all__ = ["router"]
