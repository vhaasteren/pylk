.PHONY: rag-dump ai-plan lint test fast full pick-snapshot pylk-snapshot tests-snapshot full-snapshot api-snapshot status-snapshot meta-snapshot

# Default values for RAG targets
PROFILE ?= pint
K ?= 12
OUT ?= .cursor/rag_context.md
AI_OUT ?= .cursor/ai_context.md

rag-dump:
	@tools/rag/dump_for_cursor.sh "$(QUERY)" K=$(K) OUT=$(OUT) PROFILE=$(PROFILE)

ai-plan:  # quick block to paste into prompts/roles/feature_implementer.md
	@echo "Goal: $(GOAL)"
	@echo ""
	@echo "RAG context:"
	@ragcode dump -q "$(GOAL)" --k $(K) --profile $(PROFILE) --out $(AI_OUT)
	@echo "Wrote AI context to $(AI_OUT)"

# Quality gates
lint:
	ruff check pylk
	black --check pylk

lint-no-pint-in-widgets:
	@if grep -R -nE "^\s*(from|import)\s+pint\b" pylk/widgets 2>/dev/null; then \
		echo "ERROR: PINT import found in pylk/widgets"; exit 1; \
	fi

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
	$(MAKE) lint-no-pint-in-widgets
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

# Snapshot entire codebase
full-snapshot:
	@tools/repo_view/snapshot.sh > full-snapshot.txt
	@echo "[rv] wrote full-snapshot.txt"

# API surface snapshot (Python signatures)
api-snapshot:
	@python3 tools/repo_view/api_outline.py > api-snapshot.txt
	@echo "[rv] wrote api-snapshot.txt"

# Project status snapshot
status-snapshot:
	@echo "===== PROJECT STATUS =====" > status-snapshot.txt
	@echo "Last Updated: $$(date)" >> status-snapshot.txt
	@echo "" >> status-snapshot.txt
	@echo "===== WORKING FEATURES =====" >> status-snapshot.txt
	@echo "- Pre-fit residuals plotting (PAR+TIM → matplotlib)" >> status-snapshot.txt
	@echo "- Save plot functionality (menu + button)" >> status-snapshot.txt
	@echo "- Dock widget synchronization" >> status-snapshot.txt
	@echo "- Real-time status bar updates" >> status-snapshot.txt
	@echo "- Proper widget sizing (80% minimum width)" >> status-snapshot.txt
	@echo "" >> status-snapshot.txt
	@echo "===== KNOWN ISSUES =====" >> status-snapshot.txt
	@echo "- None currently" >> status-snapshot.txt
	@echo "" >> status-snapshot.txt
	@echo "===== NEXT PRIORITIES =====" >> status-snapshot.txt
	@echo "- [Add your next features here]" >> status-snapshot.txt
	@echo "" >> status-snapshot.txt
	@echo "===== ARCHITECTURE =====" >> status-snapshot.txt
	@echo "MVC Pattern:" >> status-snapshot.txt
	@echo "- Models: PulsarModel (PINT integration)" >> status-snapshot.txt
	@echo "- Controllers: ProjectController (lifecycle)" >> status-snapshot.txt
	@echo "- Views: PlkView (matplotlib), MainWindow (Qt)" >> status-snapshot.txt
	@echo "" >> status-snapshot.txt
	@echo "===== TEST STATUS =====" >> status-snapshot.txt
	@make fast 2>&1 | tail -1 >> status-snapshot.txt
	@echo "[rv] wrote status-snapshot.txt"

# Meta snapshot (documentation without code)
meta-snapshot:
	@SNAPSHOT_EXCLUDES="pylk tests .devcontainer" \
		tools/repo_view/snapshot.sh > meta-snapshot.txt
	@echo "[rv] wrote meta-snapshot.txt"

log-prompt:
	@PROMPT="$(PROMPT)" RESPONSE="$(RESPONSE)" tools/log_prompt.sh

# Show shared rules
show-rules:
	@echo "----- prompts/shared/rules.md -----"
	@cat prompts/shared/rules.md
	@echo
	@echo "----- prompts/shared/acceptance.md -----"
	@cat prompts/shared/acceptance.md

# --- Help -------------------------------------------------------------------
help:
	@echo "Available targets:"
	@echo "  rag-dump          - dump RAG data for cursor (OUT=.cursor/rag_context.md)"
	@echo "  ai-plan           - quick block for prompts/roles/feature_implementer.md with RAG context (AI_OUT=.cursor/ai_context.md)"
	@echo "  lint              - run ruff + black check"
	@echo "  lint-no-pint-in-widgets - check no PINT imports in widgets"
	@echo "  test              - run pytest"
	@echo "  coverage          - run pytest with coverage report"
	@echo "  fast              - minimal checks for quick iteration"
	@echo "  full              - full quality gate (pre-commit + pytest + PINT check)"
	@echo ""
	@echo "RAG Variables (defaults):"
	@echo "  PROFILE=pint      - RAG profile to use"
	@echo "  K=12              - Number of context chunks"
	@echo "  OUT=.cursor/rag_context.md - Output file for rag-dump"
	@echo "  AI_OUT=.cursor/ai_context.md - Output file for ai-plan"
	@echo ""
	@echo "Snapshots:"
	@echo "  pick-snapshot     - snapshot explicit file(s) into snapshot-pick.txt"
	@echo "  pylk-snapshot     - snapshot pylk/ into snapshot-pylk.txt"
	@echo "  tests-snapshot    - snapshot tests/ into snapshot-tests.txt"
	@echo "  full-snapshot     - snapshot entire codebase into full-snapshot.txt"
	@echo "  api-snapshot      - snapshot Python API signatures into api-snapshot.txt"
	@echo "  status-snapshot   - snapshot project status and architecture into status-snapshot.txt"
	@echo "  meta-snapshot     - snapshot documentation (no code) into meta-snapshot.txt"
	@echo "  log-prompt        - log a manual prompt/response to prompts/log/"
	@echo "  show-rules        - display shared rules from prompts/shared/rules.md"