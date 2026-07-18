# 03. Orchestration Component

The `AIOrchestrator` acts as the entry point and transaction-like coordinator of the pipeline.

## Key Architecture

- Located in [ai/orchestrator/service.py](file:///Users/arunkumardhanasekaran/VS_code/Alfred/ai/orchestrator/service.py).
- Coordinates execution flow but **does not contain business logic**. It remains lightweight and generic.
- Safely handles errors and ensures memory writing is transactional (i.e. only saved upon successful model output formatting).

## API Signature

```python
class AIOrchestrator:
    async def respond(self, request: ChatRequest) -> tuple[AssistantResponse, OrchestrationTrace]: ...
    async def stream(self, request: ChatRequest) -> AsyncIterator[Mapping[str, Any]]: ...
```
