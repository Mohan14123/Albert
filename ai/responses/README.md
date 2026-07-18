# Response Builder Module

## Purpose

The Response Builder formats LLM generation results and streaming events into standardized, API-ready contracts consumed by integrating backends. It implements the `ResponseFormatter` contract.

## Responsibilities

- Translate complete model generations into normalized `AssistantResponse` objects.
- Append metadata such as execution metrics, active model types, or token consumption metrics.
- Translate real-time provider streaming chunks into transport-neutral payload mappings.

## Inputs

- `format(model_result, plan)`: Takes raw model results and intent execution plans.
- `format_stream_event(event)`: Takes raw streaming event chunks from the gateway.

## Outputs

- `format()` returns a populated `AssistantResponse` object.
- `format_stream_event()` yields standard dictionaries containing token deltas.

## Dependencies

- Implements `ResponseFormatter` interface defined in `ai/orchestrator/contracts.py`.

## Future Improvements

- Add response validators (e.g. PII scanning, toxic text classification, guardrails).
- Support automatic JSON validation of structured data against system response schemas.
