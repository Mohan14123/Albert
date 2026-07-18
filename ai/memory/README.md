# Memory System Module

## Purpose

The Memory System module manages the retrieval of relevant context and the serialization/persistence of learned user details (facts, preferences, summaries, tasks, and relationships). It implements only the contracts, avoiding raw database attachments.

## Responsibilities

- Define schemas for memory records.
- Retrieve context nodes based on active user requests and execution plans.
- Save conversation outputs and extract candidate memories to update database records.

## Inputs

- `retrieve(request, plan)` takes the user query request and intent plan.
- `save(request, response, plan)` takes the query, response, and intent plan.

## Outputs

- `retrieve` yields a sequence of `MemoryRecord` elements.
- `save` writes new context entries back to the storage adapter.

## Dependencies

- Extends interfaces in `ai/orchestrator/contracts.py`.

## Future Improvements

- Add a semantic search vector index adapter.
- Implement an LLM-based Memory Extractor to automatically extract new facts/preferences during `save`.
- Create a memory consolidation scheduler that runs offline to merge matching facts.
