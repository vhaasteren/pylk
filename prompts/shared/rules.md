# Shared Rules - Single Source of Truth

## Core Behavioral Rules

### PAUSE Line (Non-Negotiable)
**Every milestone MUST end with this exact line:**
```
PAUSE: Milestone complete. Run `make fast` to verify, then continue.
```

**At PAUSE checkpoint:**
- **AI runs `make fast`** automatically to verify changes
- **Human runs the actual app** to test functionality
- **Human may run additional tests** as needed
- **Human decides** whether to continue or request amendments
- **Only after human approval** does AI continue to next milestone

### Milestone Size Limit
- **Maximum 300 LOC per milestone**
- Count includes all changes: new code, modifications, tests
- If approaching limit, split into smaller milestones

### Command Execution Policy

- If the environment can run commands, the AI MAY run:
  - `make fast`, `make test`, `make lint`, `make show-rules`
  - `pytest`, `black --check`, `ruff check`
  - Read-only shell ops (`ls`, `cat`, `grep`, `find`)

- If the environment CANNOT run commands (no shell access), the AI MUST:
  - Ask the human to run the commands
  - Wait for the result before proceeding

- Commands requiring explicit permission (ask first):
  - File system modifications (create/move/delete files/dirs)
  - Directory structure changes
  - Package install or env changes
  - Any command that writes files (unless explicitly requested)

- Git operations are **prohibited** unless the human explicitly instructs:
  - No `git add/commit/push/branch` initiated by the AI

## Architecture Rules

### MVC Separation
- **Models**: Data and business logic only
- **Views**: UI components only, no business logic
- **Controllers**: Coordinate between models and views
- **No PINT imports in widgets** - use dependency injection

### Coding Style
- **Python 3.11+** with Qt via `qtpy`
- **UI thin**: Put logic in `controllers/` and `models/`, not in widgets
- **No direct PINT in widgets**: PINT calls live in `models/` or `controllers/`
- **Signals/slots over polling**: Views subscribe, controllers emit
- **Short synchronous ops** on UI thread are OK; long ops → worker thread (future)
- **LLM changes**: Made **directly to files**; add/update tests when logic changes
- **Formatting**: Black (100 cols), Ruff (incl. import sort), mypy for `pylk/*`
- **Conventional Commits**: Required for all commits

### Signal/Slot Patterns
- **Early signal emission**: Emit signals immediately when data changes
- **Late signal subscription**: Views must handle signals idempotently
- **Idempotent set_model()**: Views must render current state immediately when model is set

## Testing Rules

### Test-First Approach
- **Every milestone must include tests**
- **Integration tests for UI components** using pytest-qt
- **Unit tests for business logic** using standard pytest

### Testability Policies
- **No blocking dialogs in tests** - use dependency injection
- **QFileDialog → injectable save_path_provider**
- **Headless Qt testing**: `QT_QPA_PLATFORM=offscreen`
- **Prefer monkeypatch over environment checks**

### Test Data Patterns
- **Synthetic data for unit tests** (no real PINT files)
- **Real data for integration tests** (when PINT is available)
- **Mock external dependencies** (file I/O, network calls)

## Quality Gates

### Pre-commit Requirements
- **All code must pass pre-commit hooks**
- **Black formatting** (100 char line length)
- **Ruff linting** (no warnings)
- **Type hints** where appropriate

### Code Review Standards
- **Every change must be reviewable**
- **Clear commit messages** following conventional commits
- **Documentation updates** for user-facing changes

## Error Recovery Patterns

### When `make fast` Fails
1. **Fix the immediate issue** (usually import or syntax error)
2. **Re-run `make fast`** to verify fix
3. **Continue with next milestone** only after green

### When Tests Fail
1. **Read the error message carefully**
2. **Fix the root cause** (don't just make tests pass)
3. **Add regression test** if it's a bug fix
4. **Re-run tests** to verify fix

## Integration Patterns

### Widget Sizing
- **Minimum width enforcement**: 80% of parent width
- **QSizePolicy.Expanding** for flexible layouts
- **Minimum canvas size** for matplotlib widgets

### Signal Timing
- **Emit signals immediately** when data changes
- **Subscribe to signals in set_model()** method
- **Render current state** immediately after signal subscription

### File Operations
- **Use dependency injection** for file paths
- **Provide fallback values** for missing files
- **Handle errors gracefully** with user feedback

## Documentation Requirements

### CHANGELOG.md
- **Update for every user-facing change**
- **Follow "Keep a Changelog" format**
- **Include breaking changes** and migration notes

### Code Comments
- **Explain complex logic** and business rules
- **Document signal/slot connections**
- **Include examples** for public APIs

## Success Metrics

### Milestone Quality
- **Median milestone size**: Target 200-300 LOC
- **Amendment rate**: Target <20% of milestones
- **Time to green**: Target <5 minutes from PAUSE to `make fast` success

### Code Quality
- **Pre-commit pass rate**: Target >90% on first try
- **Test coverage**: Target >80% for new code
- **Type coverage**: Target >70% for new code

### Process Health
- **Context switching**: Minimize role changes within milestone
- **Error recovery**: Quick resolution of `make fast` failures
- **Integration success**: Smooth handoff between milestones
