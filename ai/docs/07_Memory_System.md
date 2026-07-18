# 07. Memory System

The memory system extracts, retrieves, and persists user context.

## Memory Categories

1. **Facts**: Fixed items (e.g. "User lives in Seattle").
2. **Preferences**: Modifiers (e.g. "User prefers brief messages").
3. **Summaries**: Abstract summaries of previous turns.
4. **Tasks**: Work items tracked.
5. **Relationships**: Connections between topics.

## Pipeline Integration

Memory components do not connect to database pools. Instead, they expose interfaces (`MemoryRetriever` and `MemoryWriter`) that other developers implement as database adapters (e.g. Vector DB, SQL).

See [memory.mermaid](file:///Users/arunkumardhanasekaran/VS_code/Alfred/ai/docs/diagrams/memory.mermaid) for details.
