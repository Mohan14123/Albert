from __future__ import annotations

import json
import logging
from ..orchestrator.contracts import IntentPlanner, LanguageModelGateway
from ..orchestrator.models import ChatRequest
from .models import ExecutionPlan, PlanStep

from ..prompts import PromptManager

logger = logging.getLogger(__name__)

# Maximum number of self-correction attempts when the LLM returns invalid JSON.
_MAX_PLAN_RETRIES = 2


class LLMIntentPlanner(IntentPlanner):
    """Planner that uses LLM generation to classify intent and select tools.

    If the LLM returns malformed JSON, the planner feeds the error back
    and retries up to ``_MAX_PLAN_RETRIES`` times before falling back to
    a safe ``direct_chat`` plan.
    """

    def __init__(
        self,
        gateway: LanguageModelGateway,
        prompt_manager: PromptManager | None = None,
        known_tool_names: set[str] | None = None,
    ) -> None:
        """Initialize the planner with an LLM gateway client.

        Parameters
        ----------
        gateway:
            The language model gateway used for intent classification.
        prompt_manager:
            Optional prompt manager for loading templates.
        known_tool_names:
            Optional set of registered tool names.  When provided the planner
            will filter out plan steps that reference unknown tools.
        """
        self._gateway = gateway
        self._prompt_manager = prompt_manager or PromptManager()
        self._known_tool_names: set[str] = known_tool_names or set()

    async def create_plan(self, request: ChatRequest) -> ExecutionPlan:
        """Classify user request message and output a structured execution plan."""
        system_instruction = self._prompt_manager.get_template("intent_classification")

        prompt = (
            f"User Prompt: {request.message}\n"
            f"History context length: {len(request.history)} messages."
        )

        context: list[dict[str, str]] = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt},
        ]

        # ---- Self-correction retry loop ----
        last_error_msg: str | None = None
        for attempt in range(_MAX_PLAN_RETRIES + 1):
            try:
                # If a previous attempt produced an error, append correction context
                if last_error_msg is not None:
                    context.append({
                        "role": "user",
                        "content": (
                            f"Your previous response was invalid JSON. "
                            f"Error: {last_error_msg}\n"
                            f"Please respond ONLY with a valid JSON object matching the schema."
                        ),
                    })

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
                plan = self._build_plan(data)
                return plan

            except json.JSONDecodeError as e:
                last_error_msg = str(e)
                logger.warning(
                    "LLM returned non-JSON plan (attempt %d/%d): %s",
                    attempt + 1, _MAX_PLAN_RETRIES + 1, e,
                )
            except Exception as e:
                logger.error(
                    "Unexpected error during plan creation (attempt %d/%d): %s",
                    attempt + 1, _MAX_PLAN_RETRIES + 1, e,
                    exc_info=True,
                )
                last_error_msg = str(e)

        # All retries exhausted — fall back to safe direct chat
        logger.warning("Plan creation failed after %d attempts — falling back to direct_chat", _MAX_PLAN_RETRIES + 1)
        return ExecutionPlan(intent="direct_chat", confidence=0.3, steps=[])

    # -- Internal helpers --------------------------------------------------------

    def _build_plan(self, data: dict[str, Any]) -> ExecutionPlan:
        """Parse and validate a JSON plan dictionary into an ExecutionPlan."""
        raw_steps = data.get("steps", [])
        validated_steps: list[PlanStep] = []

        for step_data in raw_steps:
            tool_name = step_data.get("tool_name", "unknown")

            # Validate tool exists in registry (if registry is provided)
            if self._known_tool_names and tool_name not in self._known_tool_names:
                logger.warning(
                    "Plan references unknown tool '%s' — skipping step", tool_name
                )
                continue

            # Validate args is a dict
            args = step_data.get("args", {})
            if not isinstance(args, dict):
                logger.warning(
                    "Plan step '%s' has non-dict args (%s) — defaulting to empty",
                    step_data.get("step_id", "?"), type(args).__name__,
                )
                args = {}

            validated_steps.append(
                PlanStep(
                    step_id=step_data.get("step_id", "step"),
                    tool_name=tool_name,
                    args=args,
                )
            )

        return ExecutionPlan(
            intent=data.get("intent", "direct_chat"),
            confidence=float(data.get("confidence", 1.0)),
            steps=validated_steps,
        )
