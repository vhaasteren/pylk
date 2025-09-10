# Style Constraints (Pylk)

- Qt via `qtpy`; widgets thin; logic in controllers/models.
- No PINT calls in widgets; only in controllers/models.
- Keep patches small, reviewable; include tests on logic changes.
- Avoid blocking the UI thread (long tasks → plan QThread future).
- Follow Black/Ruff/mypy; Conventional Commits.
