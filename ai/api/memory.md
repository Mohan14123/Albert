# Memory Retrieval and Storage Contract

Defines schema rules for memory nodes.

## Memory Schema

### `MemoryRecord`
* `id` (string): Unique identifier.
* `type` (string): One of `fact`, `preference`, `summary`, `task`, `relationship`.
* `content` (string): The text content representing the memory.
* `created_at` (string): ISO timestamp.
* `metadata` (object): Additional fields like associations, weight, decay rate.

```json
{
  "id": "mem_12345",
  "type": "preference",
  "content": "User prefers concise summaries instead of long bulleted lists.",
  "created_at": "2026-07-18T12:00:00Z",
  "metadata": {
    "confidence": 0.98,
    "last_accessed": "2026-07-18T12:20:00Z"
  }
}
```
