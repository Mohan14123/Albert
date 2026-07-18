# 13. Error Handling Policy

Describes the error handling boundaries inside the AI module.

## Exception Hierarchy

All exceptions subclass `AIError`.
- `GatewayError`: Maps service interruptions or model rate limits.
- `PlannerError`: Handles syntax issues during instruction composition.
- `ToolError`: Captures exceptions during execution of steps.

## Fail-safe Execution

- Tool failures return formatted fallback responses rather than bubbling crashes.
- Configuration errors validate inputs during initialization stages.
