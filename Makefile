.PHONY: rag-dump ai-plan lint test fast full pick-snapshot pylk-snapshot tests-snapshot

rag-dump:
	@tools/rag/dump_for_cursor.sh "$(QUERY)" K=$(K) OUT=$(OUT) PROFILE=$(PROFILE)

ai-plan:  # quick block to paste into 01_planner.md
	@echo "Goal: $(GOAL)"
	@echo ""
	@echo "RAG context:"
	@ragcode dump -q "$(GOAL)" --k 12 --profile pint | sed -e 's/^/    /'

# Quality gates
lint:
	ruff check pylk
	black --check pylk

test:
	pytest -q

coverage:
	pytest --cov=pylk --cov-report=term-missing

# Modes
fast:  ## MVW: minimal checks for quick iteration
	SKIP=mypy,detect-secrets pre-commit run --all-files || true
	pytest -q || true

full:  ## Full: everything green or fail
	pre-commit run --all-files
	pytest -q

# --- Repo snapshots (for LLM workflows) -------------------------------------
# Write curated file listings to text files. Excludes heavy/irrelevant paths by default.

# Partial (explicit selection)
# Usage:
#   make pick-snapshot FILES="a b c"
#   make pick-snapshot FILELIST=paths.txt
#   echo -e "a\nb\nc" | make pick-snapshot
pick-snapshot:
	@tools/repo_view/partial_snapshot.sh ${FILES} > snapshot-pick.txt || true
	@echo "[rv] wrote snapshot-pick.txt"

# Snapshot just pylk/
pylk-snapshot:
	@SNAPSHOT_PATHS="pylk" SNAPSHOT_EXCLUDES="node_modules .venv dist out *.patch" \
		tools/repo_view/snapshot.sh > snapshot-pylk.txt
	@echo "[rv] wrote snapshot-pylk.txt"

# Snapshot just tests/
tests-snapshot:
	@SNAPSHOT_PATHS="tests" SNAPSHOT_EXCLUDES="node_modules .venv dist out *.patch" \
		tools/repo_view/snapshot.sh > snapshot-tests.txt
	@echo "[rv] wrote snapshot-tests.txt"

log-prompt:
	@PROMPT="$(PROMPT)" RESPONSE="$(RESPONSE)" tools/log_prompt.sh

# --- Help -------------------------------------------------------------------
help:
	@echo "Available targets:"
	@echo "  rag-dump          - dump RAG data for cursor"
	@echo "  ai-plan           - quick block for 01_planner.md with RAG context"
	@echo "  lint              - run ruff + black check"
	@echo "  test              - run pytest"
	@echo "  coverage          - run pytest with coverage report"
	@echo "  fast              - minimal checks for quick iteration"
	@echo "  full              - full quality gate (pre-commit + pytest)"
	@echo ""
	@echo "Snapshots:"
	@echo "  pick-snapshot     - snapshot explicit file(s) into snapshot-pick.txt"
	@echo "  pylk-snapshot     - snapshot pylk/ into snapshot-pylk.txt"
	@echo "  tests-snapshot    - snapshot tests/ into snapshot-tests.txt"
	@echo "  log-prompt        - log a manual prompt/response to prompts/log/"