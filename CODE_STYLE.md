# Coding Style (Pylk)

- Python 3.11+, Qt via `qtpy`.
- **UI thin**: put logic in `controllers/` and `models/`, not in widgets.
- **No direct PINT in widgets**; PINT calls live in `models/` or `controllers/`.
- Prefer signals/slots over polling; views subscribe, controllers emit.
- Short synchronous ops on UI thread are OK; long ops → worker thread (future).
- LLM changes should be made **directly to files**; add/update tests when logic changes.

Formatting: Black (100 cols). Lint: Ruff (incl. import sort). Types: mypy for `pylk/*`.
