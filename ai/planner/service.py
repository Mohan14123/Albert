from __future__ import annotations

import json
import logging
from ..orchestrator.contracts import IntentPlanner, LanguageModelGateway
from ..orchestrator.models import ChatRequest
from .models import ExecutionPlan, PlanStep

from ..prompts import PromptManager

logger = logging.getLogger(__name__)


class LLMIntentPlanner(IntentPlanner):
    """Planner that uses LLM generation to classify intent and select tools."""

    def __init__(
        self, gateway: LanguageModelGateway, prompt_manager: PromptManager | None = None
    ) -> None:
        """Initialize the planner with an LLM gateway client."""
        self._gateway = gateway
        self._prompt_manager = prompt_manager or PromptManager()

    async def create_plan(self, request: ChatRequest) -> ExecutionPlan:
        """Classify user request message and output a structured execution plan."""
        system_instruction = self._prompt_manager.get_template("intent_classification")

        prompt = (
            f"User Prompt: {request.message}\n"
            f"History context length: {len(request.history)} messages."
        )

        context = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt},
        ]

        try:
            res = await self._gateway.generate(context)
            content = res.get("content", "").strip()

            # Clean up markdown JSON code blocks if present
            if content.startswith("```"):
                lines = content.splitlines()
                if lines[0].startswith("```json"):
                    content = "\n".join(lines[1:-1])
                elif lines[0].startswith("```"):
                    content = "\n".join(lines[1:-1])

            # Handle mock provider responses transparently
            if content.startswith("[Mock LLM"):
                # Return a default mock plan
                return ExecutionPlan(
                    intent="mock_chat",
                    confidence=1.0,
                    steps=[
                        PlanStep(
                            step_id="mock_step_1",
                            tool_name="mock.tool",
                            args={"echo": request.message},
                        )
                    ],
                )

            data = json.loads(content)
            steps = []
            for step_data in data.get("steps", []):
                steps.append(
                    PlanStep(
                        step_id=step_data.get("step_id", "step"),
                        tool_name=step_data.get("tool_name", "unknown"),
                        args=step_data.get("args", {}),
                    )
                )

            return ExecutionPlan(
                intent=data.get("intent", "direct_chat"),
                confidence=float(data.get("confidence", 1.0)),
                steps=steps,
            )

        except json.JSONDecodeError as e:
            logger.warning(
                "LLM returned non-JSON plan, falling back to direct_chat: %s", e
            )
            return ExecutionPlan(intent="direct_chat", confidence=0.5, steps=[])
        except Exception as e:
            logger.error(
                "Unexpected error during plan creation, falling back to direct_chat: %s",
                e,
                exc_info=True,
            )
            return ExecutionPlan(intent="direct_chat", confidence=0.5, steps=[])
