# AI Module API Contracts

This directory contains the API contracts defining the boundary between the AI module and the external backend and frontend systems.

## Purpose

The AI module is decoupled from transport, authentication, persistence, and HTTP servers. To enable other developers to build backend adapters and frontend integrations, these files declare exact schemas, endpoints, and event structures.

## Contents

- [openapi.yaml](file:///Users/arunkumardhanasekaran/VS_code/Alfred/ai/api/openapi.yaml): OpenAPI 3.0 specification for the chat, streaming, and tool execution endpoints.
- [chat.md](file:///Users/arunkumardhanasekaran/VS_code/Alfred/ai/api/chat.md): Message formats, history preservation, and conversation context conventions.
- [planner.md](file:///Users/arunkumardhanasekaran/VS_code/Alfred/ai/api/planner.md): Schema for plans, intent payload mappings, and step definitions.
- [memory.md](file:///Users/arunkumardhanasekaran/VS_code/Alfred/ai/api/memory.md): Schema for fact, preference, summary, task, and relationship entities.
- [tools.md](file:///Users/arunkumardhanasekaran/VS_code/Alfred/ai/api/tools.md): Tool declaration format and execution payload/response structures.
- [streaming.md](file:///Users/arunkumardhanasekaran/VS_code/Alfred/ai/api/streaming.md): SSE (Server-Sent Events) and WebSocket transport mapping rules.
- [events.md](file:///Users/arunkumardhanasekaran/VS_code/Alfred/ai/api/events.md): Event payload schemas emitted during orchestration.
