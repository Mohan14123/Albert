# 06. Context Builder

The `ContextAssembler` combines distinct information components into a unified generation prompt payload.

## Context Elements

- **System Prompt**: Loaded from Prompt Manager templates.
- **Conversation History**: Retained chat message logs.
- **User Preferences**: Retrieved from memory (e.g. formatting styles, persona).
- **Memory Context**: Facts retrieved relevant to the intent.
- **Tool Outputs**: Result payloads of executed steps.

## Pipeline Integration

```python
class ContextAssembler(ABC):
    @abstractmethod
    async def build(
        self,
        request: ChatRequest,
        plan: Any,
        memories: Sequence[Any],
        tool_results: Sequence[Any],
    ) -> Any: ...
```
