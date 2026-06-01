# Copilot Instructions for osmgeojson-python

Always-on baseline for this repository.

MapLark is a self-hosted GeoJSON API over OpenStreetMap data, backed by PostGIS and served via FastAPI.

- Keep changes minimal and backward compatible unless a task explicitly asks for breaking changes.
- Prefer strong typing and mypy-compatible changes.
- Keep sync and async client behavior aligned for equivalent features.
- Prefer deterministic tests with mocked HTTP over live network calls.
- Treat `.github/instructions/*.instructions.md` as the source of detailed, file-specific rules.
