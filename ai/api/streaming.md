# Streaming Event Contract

Describes standard transport-neutral mappings for event streams.

## Events Format

Streaming works via `text/event-stream` (Server-Sent Events). The events yielded from `AIOrchestrator.stream()` are represented as raw python mappings, which are then serialized by the backend.

### Stream Event Type
Every streaming event contains:
- `event` (string): Type of event (`token`, `error`, `done`).
- `delta` (string, optional): Fragment of the response.
- `metadata` (object, optional): Diagnostic or billing tokens.

```text
event: token
data: {"delta": "Hello"}

event: token
data: {"delta": " world"}

event: done
data: {"metadata": {"prompt_tokens": 12, "completion_tokens": 45}}
```
