# Orchestration Events Contract

Describes trace logs and pipeline-wide execution events emitted by `AIOrchestrator`.

## Events Schema

### `OrchestrationTrace`
Emitted at the end of each run to allow telemetry tracing.
```json
{
  "conversation_id": "conv-uuid",
  "completed_steps": [
    "planning",
    "memory_retrieval",
    "tool_execution",
    "context_build",
    "llm_generation",
    "response_formatting",
    "memory_save"
  ]
}
```
Does not expose raw messages or prompt contents to preserve user privacy.
