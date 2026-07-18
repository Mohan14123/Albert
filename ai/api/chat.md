# Chat Interaction Contract

Describes the chat message structures and expectations for backend adapters.

## Data Structures

### `ChatMessage`
* `role` (string): The sender role (`user`, `assistant`, `system`).
* `content` (string): Text content of the message.

### `ChatRequest`
* `conversation_id` (string): A unique identifier for the chat session.
* `user_id` (string): The identifier of the requesting user.
* `message` (string): The latest user input.
* `history` (array of `ChatMessage`): Previous messages in chronological order.
* `metadata` (object): Key-value parameters passed through to components.

## Pipeline Integration

1. The backend parses incoming HTTP/WebSocket messages.
2. The backend constructs a `ChatRequest`.
3. The backend calls `AIOrchestrator.respond(request)` or `AIOrchestrator.stream(request)`.
4. Orchestrator delegates to LLM providers via the gateway.
