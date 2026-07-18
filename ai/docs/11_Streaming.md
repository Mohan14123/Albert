# 11. Streaming Model Responses

Defines streaming mechanics inside the AI pipeline.

## Stream Mechanics

1. The Orchestrator yields an asynchronous iterator from `stream()`.
2. The `LanguageModelGateway` yields chunks dynamically.
3. The `ResponseFormatter` transforms the model chunks.
4. The caller serializes formatting output to transport formats (e.g. SSE `/api/v1/chat`).
