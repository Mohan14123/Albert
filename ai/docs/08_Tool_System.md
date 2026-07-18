# 08. Tool System

Describes the plug-and-play capability to define and run tools.

## Architecture

- **Tool Registry**: A dictionary maps tool keys to python execution targets.
- **Authorization**: The Orchestrator relies on the tool execution boundary to safely run tools that were approved in the `ExecutionPlan`.
- **Predefined Tools**: Stubs for Google Search, Gmail, Google Calendar, Calculator, and memory access.
