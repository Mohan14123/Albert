# 01. AI Module Architecture

This document describes the high-level architecture of the modular AI system in Alfred.

## Core Design Principles

1. **Framework Agnosticism**: The core pipeline coordinates steps using abstract Python contracts, completely decoupled from HTTP frameworks (FastAPI, Django), database libraries, and LLM SDK packages.
2. **Single Responsibility Principle (SRP)**: Each component does one thing:
   - Orchestration enforces the workflow.
   - Planner detects intent and selects tools.
   - Memory holds contextual states.
   - Gateway interacts with LLMs.
3. **Dependency Injection**: Collaborating components are injected dynamically into the Orchestrator, facilitating mock tests and configuration shifts.

## Architectural Diagram

See [architecture.mermaid](file:///Users/arunkumardhanasekaran/VS_code/Alfred/ai/docs/diagrams/architecture.mermaid) for a visual representation.
