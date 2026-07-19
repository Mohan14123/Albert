from __future__ import annotations

import logging
from typing import Any, Sequence
from ..orchestrator.contracts import ContextAssembler
from ..orchestrator.models import ChatRequest
from ..constants import ROLE_SYSTEM, ROLE_USER

from ..prompts import PromptManager

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Token estimation — a lightweight approximation (1 token ≈ 4 characters).
# Production systems should replace this with a proper tokenizer.
# ---------------------------------------------------------------------------

_CHARS_PER_TOKEN = 4
_DEFAULT_TOKEN_BUDGET = 8192  # default context window budget


def estimate_tokens(text: str) -> int:
    """Return an approximate token count for *text*."""
    return max(1, len(text) // _CHARS_PER_TOKEN)


def _total_tokens(messages: list[dict[str, str]]) -> int:
    """Sum estimated tokens across all messages."""
    return sum(estimate_tokens(m.get("content", "")) for m in messages)


class DefaultContextBuilder(ContextAssembler):
    """Assembles prompt contexts for LLM generation from orchestrator inputs.

    Features:
    - Structured injection of memories and tool results into the system prompt.
    - Token budgeting with history compression when context exceeds budget.
    """

    def __init__(
        self,
        prompt_manager: PromptManager | None = None,
        token_budget: int = _DEFAULT_TOKEN_BUDGET,
    ) -> None:
        """Initialize builder with prompt manager and token budget."""
        self._prompt_manager = prompt_manager or PromptManager()
        self._token_budget = token_budget

    async def build(
        self,
        request: ChatRequest,
        plan: Any,
        memories: Sequence[Any],
        tool_results: Sequence[Any],
    ) -> list[dict[str, str]]:
        """Compile user query, history, memories, and tool results into model prompts.

        If the assembled context exceeds the token budget, the builder
        progressively trims conversation history (oldest first) while always
        preserving the system instruction, the latest user message, and
        injected memories / tool results.
        """
        system_content = self._prompt_manager.get_template("system_instruction")

        # 1. Format Memories (Facts, Preferences, etc.)
        if memories:
            system_content += "\nRetrieved context memories from user profile:\n"
            for mem in memories:
                # Assuming memories have content/type, or string format
                if hasattr(mem, "content"):
                    mem_type = getattr(mem, "type", "fact")
                    system_content += f"- [{mem_type}] {mem.content}\n"
                else:
                    system_content += f"- {str(mem)}\n"

        # 2. Format Tool Results
        if tool_results:
            system_content += "\nResults of executed tools:\n"
            for res in tool_results:
                # Format result object or dict
                if isinstance(res, dict):
                    tool_name = res.get("tool_name", "unknown")
                    success = res.get("success", True)
                    result_data = res.get("result", "")
                    error = res.get("error")
                    if success:
                        system_content += f"- Tool '{tool_name}' successfully returned: {result_data}\n"
                    else:
                        system_content += f"- Tool '{tool_name}' failed with error: {error}\n"
                else:
                    system_content += f"- Tool execution output: {str(res)}\n"

        # 3. Build initial messages list
        system_msg = {"role": ROLE_SYSTEM, "content": system_content}
        user_msg = {"role": ROLE_USER, "content": request.message}

        history_msgs: list[dict[str, str]] = []
        for msg in request.history:
            history_msgs.append({"role": msg.role, "content": msg.content})

        # 4. Apply token budgeting — trim history oldest-first
        messages = [system_msg] + history_msgs + [user_msg]
        trimmed_count = 0
        while _total_tokens(messages) > self._token_budget and len(history_msgs) > 0:
            # Remove the oldest history message
            history_msgs.pop(0)
            trimmed_count += 1
            messages = [system_msg] + history_msgs + [user_msg]

        if trimmed_count > 0:
            logger.info(
                "Token budget exceeded — trimmed %d oldest history messages "
                "(budget=%d, final_tokens=%d)",
                trimmed_count, self._token_budget, _total_tokens(messages),
            )

        return messages
