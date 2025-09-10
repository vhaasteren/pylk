# Pylk – LLM-Assisted Workflow

> Legend: **(MVW)** must have for the smallest smooth loop. **(Full)** recommended once we’re comfy.

## 0) One-time setup (MVW)

```bash
# dev deps
pip install pre-commit ruff black mypy commitizen detect-secrets pytest pytest-qt

# install git hooks
pre-commit install --hook-type pre-commit --hook-type pre-push --hook-type commit-msg
```

---

## 1) Repo hygiene & config

### 1.1 .editorconfig (MVW)

```ini
# .editorconfig
root = true

[*]
charset = utf-8
end_of_line = lf
indent_style = space
indent_size = 4
insert_final_newline = true
trim_trailing_whitespace = true
max_line_length = 100

[*.{md,rst}]
max_line_length = off
trim_trailing_whitespace = false
```

### 1.2 pyproject.toml tool sections (MVW)

*(Merge into the existing pyproject)*

```toml
[tool.black]
line-length = 100
target-version = ["py311"]

[tool.ruff]
line-length = 100
target-version = "py311"
extend-select = ["I"]  # import sort
ignore = ["E501"]      # E501 handled by Black

[tool.mypy]
python_version = "3.11"
warn_unused_ignores = true
warn_redundant_casts = true
strict_optional = true
no_implicit_optional = true
exclude = ["build", "dist", "\\.venv", "state"]

[tool.commitizen]
name = "cz_conventional_commits"
tag_format = "v$version"
update_changelog_on_bump = true
version_provider = "scm"
```

### 1.3 .pre-commit-config.yaml (MVW + Full)

* **MVW hooks**: black, ruff, detect-secrets, commitizen (commit-msg), basic mypy.
* **Pre-push** runs `pytest -q` (Full, but you can toggle “fast mode”—see §7).

```yaml
# .pre-commit-config.yaml
default_install_hook_types: [pre-commit, pre-push, commit-msg]
minimum_pre_commit_version: "3.6.0"

repos:
  - repo: https://github.com/psf/black
    rev: 24.8.0
    hooks: [{ id: black }]

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.9
    hooks:
      - id: ruff
        args: ["--fix"]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.10.0
    hooks:
      - id: mypy
        additional_dependencies: []

  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.5.0
    hooks:
      - id: detect-secrets
        args: ["--baseline", ".secrets.baseline"]
        stages: [pre-commit]

  - repo: https://github.com/commitizen-tools/commitizen
    rev: v3.27.0
    hooks:
      - id: commitizen
        stages: [commit-msg]
        args: ["--retry", "false"]
```

> **Fast mode** tip: temporarily skip heavy hooks with
> `SKIP=mypy,detect-secrets pre-commit run --all-files` or set `PRE_COMMIT_ALLOW_NO_CONFIG=1` for quick spikes. See §7.

---

## 2) Coding style & contributor docs

### 2.1 CODE\_STYLE.md (MVW)

```markdown
# Coding Style (Pylk)

- Python 3.11+, Qt via `qtpy`.
- **UI thin**: put logic in `controllers/` and `models/`, not in widgets.
- **No direct PINT in widgets**; PINT calls live in `models/` or `controllers/`.
- Prefer signals/slots over polling; views subscribe, controllers emit.
- Short synchronous ops on UI thread are OK; long ops → worker thread (future).
- LLM changes should land as **diffs**; add/update tests when logic changes.

Formatting: Black (100 cols). Lint: Ruff (incl. import sort). Types: mypy for `pylk/*`.
```

### 2.2 CONTRIBUTING.md (MVW + Full)

````markdown
# Contributing

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

## Resolving Merge Conflicts with AI (Full)
When conflicts happen, you can prompt your LLM:

> Resolve merge conflicts in this patch:
> ```
> {conflicted_patch}
> ```
> Provide a **unified diff** with resolved conflicts and a brief explanation of each hunk.

See `GLOSSARY.md` for key terms.
````

### 2.3 GLOSSARY.md (MVW)

```markdown
# Glossary

**Signals/Slots** — Qt’s event system: objects emit *signals*, other objects *connect* slots (callbacks).
**PINT** — Pulsar timing library; Pylk is a GUI layered on PINT.
**MVC-ish** — Pylk uses models (state), controllers (logic), and views/widgets (UI).
**RAG** — Retrieval-Augmented Generation; use external indexed code/docs to ground LLM outputs.
**MVW** — Minimal Viable Workflow: smallest set of tools to iterate fast.
```

---

## 3) Prompt kit (consolidated & non-redundant)

> We keep multiple prompts but **centralize** constraints in one file and mark which are MVW.

### 3.1 prompts/style\_constraints.md (MVW – shared)

```markdown
# Style Constraints (Pylk)

- Qt via `qtpy`; widgets thin; logic in controllers/models.
- No PINT calls in widgets; only in controllers/models.
- Keep patches small, reviewable; include tests on logic changes.
- Avoid blocking the UI thread (long tasks → plan QThread future).
- Follow Black/Ruff/mypy; Conventional Commits.
```

### 3.2 prompts/01\_planner.md (MVW)

```md
You are the Pylk project planner and implementer.

Goal: {goal}

Follow `prompts/style_constraints.md`.

Deliverables:
1) Short plan (steps + risks)
2) **Unified diff** patch
3) Tests (if logic changed)
4) Post-merge follow-ups (bullets)

RAG context (optional; paste if relevant to goal):
{rag_dump}
```

### 3.3 prompts/02\_reviewer.md (Full – focused review)

```md
You are a reviewer.

Review this patch for Pylk:

{patch}

Use `prompts/style_constraints.md`. Output:
- BLOCKING issues
- Non-blocking suggestions
- Test coverage gaps
```

### 3.4 prompts/03\_commit.md (MVW)

```md
Write a Conventional Commit message (scope: pylk). Include short body and testing notes.

Changes:
{changes}
```

### 3.5 prompts/04\_rag\_question.md (Full)

```md
Answer strictly from the RAG context. If missing, say what's missing.

Question: {question}

RAG context:
{rag_dump}

Output:
- Short answer
- Bullet citations (file:lines)
- If code change requested: unified diff
```

---

## 4) Cursor workflow (primary) + non-Cursor fallbacks

### 4.1 Cursor (primary) (MVW)

* Keep **`.cursorrules`**:

```text
# .cursorrules
- Produce UNIFIED DIFFS unless I ask for prose.
- Keep widgets thin; push logic to controllers/models.
- No PINT usage in widgets.
- When logic changes, add/update tests in `tests/`.
- Assume RAG dumps I paste are authoritative context.
- Ask before adding heavy deps; justify in PR note.
```

* **Model**: GPT-4.1 or Claude 3.5 Sonnet if available; otherwise GPT-4o mini/Haiku for quick edits.
* **Composer**: Use repo context; enable “diffs only,” “ask before multi-file edits,” “generate tests”.

### 4.2 Non-Cursor options (Full)

* **VS Code + Copilot Chat**: keep a `CONTEXT.md` buffer you paste `ragcode dump` into; ask for diffs.
* **Aider** CLI: `aider --model gpt-4o "Implement KernelController restart"`; it applies diffs automatically.
* **Jupyter** for design: run prompts from `/prompts` with `{rag_dump}` blocks.

---

## 5) RAG usage (e.g. `ragcode`) — clarify value & automate

* **When to use (MVW guidance)**: Use RAG primarily for **complex external deps** (PINT internals) or when you need citations. For small local changes, skip it.
* **Automation (Full)**: write the latest context straight into a file Cursor sees.

### 5.1 tools/rag/dump\_for\_cursor.sh (Full)

```bash
#!/usr/bin/env bash
set -euo pipefail
QUERY="${1:-}"
K="${K:-12}"
OUT="${OUT:-.cursor/rag_context.md}"
PROFILE="${PROFILE:-pint}"

if [[ -z "$QUERY" ]]; then
  echo "Usage: $0 'your query' [K=12 OUT=.cursor/rag_context.md PROFILE=pint]" >&2
  exit 1
fi

mkdir -p .cursor
ragcode dump -q "$QUERY" --k "$K" --out "$OUT" --profile "$PROFILE"
echo "Wrote RAG context to $OUT"
```

### 5.2 Makefile helpers (MVW + Full)

```make
.PHONY: rag-dump ai-plan lint test fast full

rag-dump:
	@tools/rag/dump_for_cursor.sh "$(QUERY)" K=$(K) OUT=$(OUT) PROFILE=$(PROFILE)

ai-plan:  # quick block to paste into 01_planner.md
	@echo "Goal: $(GOAL)"
	@echo ""
	@echo "RAG context:"
	@ragcode dump -q "$(GOAL)" --k 12 --out - | sed -e 's/^/    /'

# Quality gates
lint:
	ruff check pylk
	black --check pylk

test:
	pytest -q

# Modes
fast:  ## MVW: minimal checks for quick iteration
	SKIP=mypy,detect-secrets pre-commit run --all-files || true
	pytest -q || true

full:  ## Full: everything green or fail
	pre-commit run --all-files
	pytest -q
```

---

## 6) Testing: add real coverage (incl. pytest-qt)

### 6.1 tests/conftest.py (Full)

```python
import pytest

@pytest.fixture(scope="session")
def qapp():
    from qtpy.QtWidgets import QApplication
    import sys
    app = QApplication.instance() or QApplication(sys.argv)
    return app
```

### 6.2 tests/test\_boot.py (MVW)

```python
def test_imports_smoke():
    import pylk.app as _  # noqa
    import pylk.main_window as _  # noqa
```

### 6.3 tests/test\_main\_window\_qt.py (Full)

```python
from pytestqt.qtbot import QtBot
from pylk.main_window import MainWindow

def test_main_window_init(qtbot: QtBot):
    win = MainWindow()
    qtbot.addWidget(win)
    win.show()
    assert win.windowTitle() == "Pylk"
```

### 6.4 tests/test\_style.py (Full but quick)

```python
import subprocess, sys

def test_ruff():
    subprocess.check_call([sys.executable, "-m", "ruff", "check", "pylk"])

def test_black():
    subprocess.check_call([sys.executable, "-m", "black", "--check", "pylk"])
```

> As controllers/models land, add **unit tests** for their methods (no Qt needed). For plotting/GUI behaviors, keep to smoke/UI-tests via `pytest-qt`.

---

## 7) Fast mode vs Full mode (performance)

* **Fast mode (MVW)**: during prototyping

  * `make fast` → formats/lints lightly and runs tests leniently.
  * Skip heavy hooks via `SKIP=mypy,detect-secrets`.
  * Combine planner + reviewer prompts in one LLM call for tiny changes.

* **Full mode (pre-PR) (Full)**:

  * `make full` → all hooks + tests must pass.
  * Separate planner/reviewer prompts; attach RAG citations when touching PINT coupling.

In the presentation: show a slide contrasting **Fast** vs **Full** loops and explain when to use each.

---

## 8) Day-to-day practical workflow

> **📋 For detailed step-by-step workflows, see [`development-workflow.md`](development-workflow.md)**

1. **Plan (web – Grok/ChatGPT)** (MVW)

   * `make ai-plan GOAL="Out-of-process IPython kernel + Restart"`
   * Paste into `prompts/01_planner.md` with `{goal}` and optional `{rag_dump}`.
   * Get plan → diff → tests → follow-ups.

2. **Code (Cursor)** (MVW)

   * Ensure `.cursorrules` is loaded.
   * If PINT internals needed:
     `tools/rag/dump_for_cursor.sh "residuals calc in PINT" OUT=.cursor/rag_context.md`
     (the agent will see the file).
   * Apply diff; run `make fast` → iterate.

3. **Before PR** (Full)

   * `make full`
   * Use `prompts/02_reviewer.md` for a second LLM review.
   * Generate commit message via `prompts/03_commit.md`.
   * Push with branch `feat/<yourname>/<slug>` and PR template.

---

## 9) Non-Cursor notes (in case of non-Cursor workflow)

* **VS Code + Copilot Chat**: keep a `CONTEXT.md` tab; paste `ragcode dump` there and instruct Copilot to propose a **unified diff** only.
* **Aider**: first-class agentic coding with built-in repo RAG; nice to demo as an alternative.

---

## 10) RAG positioning notes

* **Use RAG when**: integrating external libs, tracking symbol relationships, needing citations.
* **Skip RAG when**: local refactors/UI tweaks where repo context suffices.
* **Trade-off**: precision & grounding vs. setup steps; show your automated `.cursor/rag_context.md` to reduce friction.

