# Orchestrator

## Purpose

`AIOrchestrator` is the AI module's framework-independent entry point. It coordinates a request through planning, memory retrieval, authorized tool execution, context assembly, model generation, response formatting, and memory persistence.

## Responsibilities

- Enforce the pipeline order.
- Pass normalized values between collaborators.
- Provide complete and streaming entry points.
- Ensure memory is persisted only after a successful response.

It does not detect intent, select a provider, compose prompts, access storage, execute tool logic, or implement HTTP/SSE/WebSocket transport.

## Inputs

- `ChatRequest`: a validated, normalized request supplied by the backend adapter.
- `OrchestratorDependencies`: concrete implementations of each port in `contracts.py`.

## Outputs

- `respond()` returns an `AssistantResponse` and a non-sensitive `OrchestrationTrace`.
- `stream()` yields transport-neutral event mappings. The backend serializes them for its chosen transport.

## Dependencies

The package depends only on Python's standard library and abstract ports defined locally. Future AI components implement these ports; backend code owns request validation, transport, identity, and persistence adapters.

## Integration

Construct `OrchestratorDependencies` in the backend composition root, then inject it into `AIOrchestrator`. Do not instantiate providers, repositories, or web-framework objects inside this package.

## Future Improvements

- Typed shared domain models will replace the temporary `Any` plan/context/result boundaries as modules are introduced.
- Add configurable timeout, cancellation, and idempotency policies at the orchestration boundary.
- Add optional telemetry hooks that preserve prompt and user-data redaction requirements.
