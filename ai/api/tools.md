# Tool Registry and Execution Contract

Defines schema for integrating tools with the pipeline.

## Tool Definition

Every tool must implement:
- `name`: dot-separated string namespace (e.g. `gmail.send_email`).
- `description`: parameters and usage details parsed by LLM.
- `parameters`: JSON Schema representation of arguments.

```json
{
  "name": "calculator.add",
  "description": "Adds two numbers together.",
  "parameters": {
    "type": "object",
    "properties": {
      "a": { "type": "number" },
      "b": { "type": "number" }
    },
    "required": ["a", "b"]
  }
}
```

## Tool Results
Represented as a JSON structure:
```json
{
  "tool_name": "calculator.add",
  "success": true,
  "result": 15,
  "error": null
}
```
