# Contributing

> **📋 For detailed development workflows, see [`development-workflow.md`](development-workflow.md)**

## Getting Started (MVW)
1. Python 3.11 (virtualenv recommended)
2. `python -m venv .venv && source .venv/bin/activate`
3. `pip install -r requirements.txt` (or `pip install -e .` + dev deps listed in README)
4. `pre-commit install --hook-type pre-commit --hook-type pre-push --hook-type commit-msg`
5. Run:
   - `pre-commit run --all-files`
   - `pytest -q` (will run smoke/style tests)
   - `python run.py`

## Branching & Commits (MVW)
- Branch names: `feat/<yourname>/<slug>`, `fix/<yourname>/<slug>`, `chore/<yourname>/<slug>`
- Conventional Commits required (enforced by Commitizen on commit-msg).
  - Example: `feat(kernel): add restart action for out-of-process IPython`

## Workflow (MVW)
- Keep PRs small (< ~300 LOC changes).
- Include tests for non-UI logic (controllers/models).
- Pass `pre-commit` + `pytest` before pushing.
- Update CHANGELOG.md for user-facing changes.

## Resolving Merge Conflicts with AI (Full)
When conflicts happen, you can prompt your LLM:

> Resolve merge conflicts in these files:
> ```
> {conflicted_files}
> ```
> Provide the **resolved files** with a brief explanation of each change.

See `GLOSSARY.md` for key terms.
