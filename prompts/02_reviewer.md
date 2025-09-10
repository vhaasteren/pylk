You are a reviewer.

Review these changes for Pylk:

{changes}

Use `prompts/style_constraints.md` and the following Definition of Done:

- Implements the requested feature (per `01_planner.md` goal).
- Follows MVC pattern (no PINT in widgets, logic in controllers/models).
- Includes tests for new logic (unit tests for models/controllers, integration tests for UI).
- Passes `make full` (pre-commit, pytest).
- Includes a Conventional Commit message.
- Updates CHANGELOG.md for user-facing changes.

Output:
- BLOCKING issues (violations of DoD or style constraints)
- Non-blocking suggestions
- Test coverage gaps
