# 05. Intent Planner

The Planner determines how a user request should be executed.

## Core Responsibilities

1. **Intent Classification**: Evaluates request message text to determine intent.
2. **Tool Selection**: Looks up tools relevant to resolving the intent.
3. **Execution Plan Generation**: Outlines steps to be executed.

## Design Philosophy

The LLM is kept out of direct workflow execution control. Instead, the Planner compiles a structured intent plan, which is executed deterministically by the orchestrator.

See [planner.mermaid](file:///Users/arunkumardhanasekaran/VS_code/Alfred/ai/docs/diagrams/planner.mermaid) for details.
