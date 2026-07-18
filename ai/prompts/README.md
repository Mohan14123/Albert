# Prompt Manager Module

## Purpose

The Prompt Manager centralizes prompt text templates, preventing them from being hardcoded inside python code files. This makes them easier to inspect, version-control, and tune.

## Responsibilities

- Load prompt templates from external flat files (located under `ai/prompts/templates/`).
- Cache templates in memory for faster lookups.
- Render parameters and variable placeholders safely.

## Inputs

- `get_template(key)`: Fetches a template by name (e.g. `system_instruction`).
- `render(key, **kwargs)`: Fetches the template and replaces placeholders with variables.

## Outputs

- A compiled prompt string suitable for LLM context construction or classification tasks.

## Dependencies

- Pure python standard library (`os`, `pathlib`).

## Future Improvements

- Support Jinja2 or similar advanced templating engines for conditional prompt logic.
- Implement prompt localization and user persona routing.
- Integrate automatic prompt versioning and dynamic A/B test splits.
