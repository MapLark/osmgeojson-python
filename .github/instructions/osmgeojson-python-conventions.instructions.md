---
description: "Use when editing Python code in osmgeojson (SDK, tests, or examples). Prefer strict typing, sync/async parity, and deterministic tests unless the task requires an exception."
name: "OSMGeoJSON Python Conventions"
applyTo: "**/*.py"
---
# OSMGeoJSON Python Conventions

- Prefer complete type hints that remain compatible with strict mypy checks.
- Prefer preserving public API compatibility unless the task explicitly requests a breaking change.
- When adding or changing request parameters in the sync client, prefer mirroring the behavior in the async client unless there is a documented reason not to.
- Prefer routing HTTP retries and rate-limit handling through shared retry/http helpers instead of duplicating retry logic in client methods.
- For pagination or chunking changes, preserve deduplication-by-id behavior and existing guardrails against stale offsets.
- For tests that exercise HTTP flows, prefer mocked HTTP requests (for example with `responses`) and avoid live network calls.
- Add or update tests for behavioral changes, including both success and error paths when practical.
- Keep docstrings user-focused: include parameter semantics and API-specific constraints rather than generic restatements.
