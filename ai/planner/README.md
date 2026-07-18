# Intent Planner Module

## Purpose

The Intent Planner determines the deterministic execution plan for a user request. It identifies the user's intent and selects any necessary tools from the registry.

## Responsibilities

- Detect intent of user requests.
- Choose tools to be executed.
- Formulate a plan representation (`ExecutionPlan`) containing steps (`PlanStep`) to be processed.
- Enforce that the LLM does not execute actions or change state directly; instead, it outputs a deterministic data-driven plan.

## Inputs

- `ChatRequest`: The user prompt and history.

## Outputs

- `ExecutionPlan`: Containing the detected intent, a confidence score, and a sequence of `PlanStep` objects specifying tool names and arguments.

## Dependencies

- Relies on root configuration (`config.py`) and exception classes (`exceptions.py`).
- Integrates with the LLM Gateway (`ai/gateway`) to perform classification and tool extraction.

## Future Improvements

- Add structured JSON output parsing to enforce schemas on intent and tool arguments.
- Add local keyword/regex rules for quick intent classification bypassing LLM queries.
- Support parallel execution trees or multi-stage planning in the plan model.
