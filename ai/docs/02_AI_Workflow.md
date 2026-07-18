# 02. AI Pipeline Workflow

This document explains the sequential execution flow of the Alfred AI request life cycle.

## Pipeline Lifecycle

Every request follows a rigorous, deterministic sequence of actions:

1. **Planner (`IntentPlanner`)**: Classifies user intent and outputs an execution plan specifying required tools.
2. **Memory Retriever (`MemoryRetriever`)**: Extracts relevant facts, preferences, summaries, and tasks based on conversation history and execution plans.
3. **Tool Executor (`ToolExecutor`)**: Invokes declared tools from the registry that are explicitly authorized by the planner.
4. **Context Assembler (`ContextAssembler`)**: Combines memories, history, prompts, and tool results into an formatted context payload.
5. **Gateway (`LanguageModelGateway`)**: Communicates with OpenAI, Claude, Gemini, or DeepSeek.
6. **Response Formatter (`ResponseFormatter`)**: Parses the generated model response into the backend contract format.
7. **Memory Writer (`MemoryWriter`)**: Persists any new facts, summaries, or tasks learned from the chat interaction.

See [workflow.mermaid](file:///Users/arunkumardhanasekaran/VS_code/Alfred/ai/docs/diagrams/workflow.mermaid) for a flow visualization.
See [sequence.mermaid](file:///Users/arunkumardhanasekaran/VS_code/Alfred/ai/docs/diagrams/sequence.mermaid) for a trace visualization.
