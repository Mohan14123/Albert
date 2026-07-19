from __future__ import annotations

from typing import Any, Sequence
from ..orchestrator.contracts import ContextAssembler
from ..orchestrator.models import ChatRequest
from ..constants import ROLE_SYSTEM, ROLE_USER

from ..prompts import PromptManager


class DefaultContextBuilder(ContextAssembler):
    """Assembles prompt contexts for LLM generation from orchestrator inputs."""

    def __init__(self, prompt_manager: PromptManager | None = None) -> None:
        """Initialize builder with prompt manager."""
        self._prompt_manager = prompt_manager or PromptManager()

    async def build(
        self,
        request: ChatRequest,
        plan: Any,
        memories: Sequence[Any],
        tool_results: Sequence[Any],
    ) -> list[dict[str, str]]:
        """Compile user query, history, memories, and tool results into model prompts."""
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
                        system_content += (
                            f"- Tool '{tool_name}' failed with error: {error}\n"
                        )
                else:
                    system_content += f"- Tool execution output: {str(res)}\n"

        messages = [{"role": ROLE_SYSTEM, "content": system_content}]

        # 3. Add History
        for msg in request.history:
            messages.append({"role": msg.role, "content": msg.content})

        # 4. Add Latest User Message
        messages.append({"role": ROLE_USER, "content": request.message})

        return messages
