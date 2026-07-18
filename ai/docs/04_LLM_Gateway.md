# 04. LLM Gateway

The Language Model Gateway provides a provider-agnostic bridge to major LLM engines.

## Supported Providers

- OpenAI (via GPT models)
- Gemini (via Google API)
- Claude (via Anthropic API)
- DeepSeek (via DeepSeek API)

## Contract Definition

```python
class LanguageModelGateway(ABC):
    @abstractmethod
    async def generate(self, context: Any) -> Any: ...

    @abstractmethod
    def stream(self, context: Any) -> AsyncIterator[Any]: ...
```

Concrete implementations wrap SDKs to map prompt inputs to standard token outputs.
