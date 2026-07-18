# Context Builder Module

## Purpose

The Context Builder compiles different pipeline inputs (conversation history, memories, preferences, and tool execution results) into a structured prompt context consumed by the LLM Gateway.

## Responsibilities

- Assemble user system instructions.
- Format retrieved context memory items clearly to guide LLM responses.
- Format tool execution results and errors to feed back to the generation engine.
- Reconstruct chat messages sequence (history context + latest turn).

## Inputs

- `request`: The active `ChatRequest` containing message and history.
- `plan`: The calculated `ExecutionPlan`.
- `memories`: Sequence of retrieved `MemoryRecord` elements.
- `tool_results`: Sequence of tool execution results.

## Outputs

- A provider-ready sequence of message mappings representing the compiled generation prompt context.

## Dependencies

- Extends interfaces in `ai/orchestrator/contracts.py`.

## Future Improvements

- Add a dynamic token estimation check to truncate history context if it exceeds model limits.
- Inject personalized formatting guidelines dynamically based on user profile preferences.
- Provide custom templating using a prompt template rendering engine.
