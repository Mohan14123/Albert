# LLM Gateway Module

## Purpose

The LLM Gateway provides a provider-agnostic bridge to major LLM engines (OpenAI, Gemini, Claude, DeepSeek). It implements the `LanguageModelGateway` contract defined in orchestration contracts.

## Responsibilities

- Wrap provider-specific client libraries and HTTP integrations.
- Convert incoming standardized context payloads to provider-specific payloads.
- Normalize provider-specific responses and stream chunks into generic formats.
- Support switching providers dynamically based on configurations.

## Inputs

- `context`: An assembled context payload from the `ContextAssembler` (usually containing prompts, system settings, history, and tool outputs).

## Outputs

- `generate(context)` returns a standardized dictionary representing the generation (e.g. `{"content": "..."}`).
- `stream(context)` yields standardized event dictionaries (e.g. `{"delta": "..."}`).

## Dependencies

- Uses python's standard libraries (`urllib.request` or `http.client`) to interact with model APIs, avoiding external dependencies.
- Relies on root exceptions (`exceptions.py`) and config loader (`config.py`).

## Future Improvements

- Add request retries, exponential backoffs, and fallback routing policies if a primary provider fails.
- Support structured JSON outputs using provider-native schema enforcement.
