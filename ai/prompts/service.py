from __future__ import annotations

import os
from typing import Any

class PromptManager:
    """Loads, caches, and renders external prompt templates."""

    def __init__(self, templates_dir: str | None = None) -> None:
        """Initialize PromptManager with templates directory path."""
        if templates_dir is None:
            # Resolve relative to this file
            templates_dir = os.path.join(os.path.dirname(__file__), "templates")
        self._templates_dir = templates_dir
        self._cache: dict[str, str] = {}

    def get_template(self, key: str) -> str:
        """Retrieve raw template content by file key (cached in memory)."""
        if key not in self._cache:
            file_path = os.path.join(self._templates_dir, f"{key}.txt")
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Prompt template file not found at: {file_path}")
            with open(file_path, "r", encoding="utf-8") as f:
                self._cache[key] = f.read()
        return self._cache[key]

    def render(self, key: str, **kwargs: Any) -> str:
        """Retrieve and format a prompt template replacing placeholders with arguments."""
        template = self.get_template(key)
        return template.format(**kwargs)
