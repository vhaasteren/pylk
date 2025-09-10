# Development Workflow (Pylk)

This document provides detailed, step-by-step workflows for common development tasks in Pylk. It's your practical blueprint for day-to-day development.

## Table of Contents
- [Quick Reference](#quick-reference)
- [Adding a New Feature](#adding-a-new-feature)
- [Fixing a Bug](#fixing-a-bug)
- [Refactoring Code](#refactoring-code)
- [Working with PINT Integration](#working-with-pint-integration)
- [Testing Workflows](#testing-workflows)
- [Code Review Process](#code-review-process)
- [Troubleshooting](#troubleshooting)

## Quick Reference

### Essential Commands
```bash
# Quick iteration (MVW mode)
make fast

# Full quality gate
make full

# Generate RAG context for complex features
make rag-dump QUERY="your question about PINT internals"

# Run specific tests
pytest tests/test_specific.py -v

# Format and lint
make lint
```

### Branch Naming
- `feat/<yourname>/<slug>` - New features
- `fix/<yourname>/<slug>` - Bug fixes  
- `chore/<yourname>/<slug>` - Maintenance tasks

---

## Adding a New Feature

### 1. Planning Phase

#### 1.1 Define the Feature
- [ ] Write a clear feature description
- [ ] Identify which components will be affected (UI, controllers, models)
- [ ] Determine if PINT integration is needed

#### 1.2 Research (if PINT integration needed)
```bash
# Generate RAG context for PINT internals
make rag-dump QUERY="PINT residuals calculation" OUT=.cursor/rag_context.md

# Or use the AI planning helper
make ai-plan GOAL="Add residuals calculation feature"
```

#### 1.3 Create Feature Branch
```bash
git checkout -b feat/yourname/residuals-calculation
```

### 2. Implementation Phase

#### 2.1 Set Up Development Environment
```bash
# Ensure you're in the devcontainer
# Virtual environment should auto-activate
source .venv/bin/activate  # if needed

# Run quick checks
make fast
```

#### 2.2 Follow MVC Pattern
- [ ] **Models**: Add data structures and PINT integration logic
- [ ] **Controllers**: Add business logic and signal handling
- [ ] **Views**: Add thin UI components that connect to controllers

#### 2.3 Implementation Steps
1. **Start with Models** (if data/PINT integration needed)
   ```python
   # pylk/models/residuals_model.py
   from qtpy.QtCore import QObject, Signal
   import pint
   
   class ResidualsModel(QObject):
       residuals_updated = Signal(list)
       
       def calculate_residuals(self, data):
           # PINT integration here
           pass
   ```

2. **Add Controllers** (business logic)
   ```python
   # pylk/controllers/residuals_controller.py
   from qtpy.QtCore import QObject
   from ..models.residuals_model import ResidualsModel
   
   class ResidualsController(QObject):
       def __init__(self):
           self.model = ResidualsModel()
           self.model.residuals_updated.connect(self._on_residuals_updated)
   ```

3. **Create Views** (thin UI)
   ```python
   # pylk/views/residuals_widget.py
   from qtpy.QtWidgets import QWidget, QVBoxLayout
   from ..controllers.residuals_controller import ResidualsController
   
   class ResidualsWidget(QWidget):
       def __init__(self):
           super().__init__()
           self.controller = ResidualsController()
           self._setup_ui()
   ```

#### 2.4 Iterative Development
```bash
# After each change, run quick checks
make fast

# Test specific functionality
pytest tests/test_residuals.py -v

# Check imports work
python -c "from pylk.views.residuals_widget import ResidualsWidget"
```

### 3. Testing Phase

#### 3.1 Add Unit Tests
```python
# tests/test_residuals_model.py
import pytest
from pylk.models.residuals_model import ResidualsModel

def test_residuals_calculation():
    model = ResidualsModel()
    # Test PINT integration
    pass

def test_signals():
    model = ResidualsModel()
    # Test signal emission
    pass
```

#### 3.2 Add Integration Tests
```python
# tests/test_residuals_integration.py
from pytestqt.qtbot import QtBot
from pylk.views.residuals_widget import ResidualsWidget

def test_residuals_widget_integration(qtbot):
    widget = ResidualsWidget()
    qtbot.addWidget(widget)
    # Test UI interactions
    pass
```

#### 3.3 Run All Tests
```bash
# Full test suite
make test

# Specific test file
pytest tests/test_residuals*.py -v
```

### 4. Pre-commit Phase

#### 4.1 Code Quality Checks
```bash
# Run full quality gate
make full

# If issues found, fix them:
# - Black formatting: black pylk/
# - Ruff linting: ruff check pylk --fix
# - MyPy type checking: mypy pylk/
```

#### 4.2 Commit Changes
```bash
# Stage changes
git add .

# Commit with conventional format
git commit -m "feat(residuals): add residuals calculation widget

- Add ResidualsModel with PINT integration
- Add ResidualsController for business logic  
- Add ResidualsWidget for UI
- Include unit and integration tests

Testing: pytest tests/test_residuals*.py passes"
```

### 5. Review and Merge

#### 5.1 Push and Create PR
```bash
git push origin feat/yourname/residuals-calculation
# Create PR on GitHub
```

#### 5.2 Self-Review Checklist
- [ ] Code follows MVC pattern (no PINT calls in widgets)
- [ ] All tests pass (`make full`)
- [ ] Code is properly formatted (Black/Ruff)
- [ ] Type hints are correct (MyPy)
- [ ] Documentation is updated if needed
- [ ] Commit message follows conventional format

---

## Fixing a Bug

### 1. Reproduce the Bug
- [ ] Create minimal reproduction case
- [ ] Document expected vs actual behavior
- [ ] Identify which component is affected

### 2. Debug and Fix
```bash
# Create bug fix branch
git checkout -b fix/yourname/bug-description

# Use debugging tools
python -m pdb run.py
# or add print statements/logging
```

### 3. Add Regression Test
```python
# tests/test_bug_fix.py
def test_bug_reproduction():
    # Test that reproduces the original bug
    pass

def test_bug_fix():
    # Test that verifies the fix works
    pass
```

### 4. Verify Fix
```bash
# Run tests
make test

# Manual testing
python run.py
# Test the specific functionality
```

---

## Refactoring Code

### 1. Plan the Refactoring
- [ ] Identify code smells (long methods, duplicated code, etc.)
- [ ] Plan the refactoring steps
- [ ] Ensure comprehensive test coverage exists

### 2. Refactor Incrementally
```bash
# Create refactoring branch
git checkout -b chore/yourname/refactor-description

# Make small, focused changes
# Run tests after each change
make fast
```

### 3. Maintain Functionality
- [ ] All existing tests continue to pass
- [ ] No new bugs introduced
- [ ] Code is cleaner and more maintainable

---

## Working with PINT Integration

### 1. When to Use RAG
Use RAG when you need to understand:
- PINT internal APIs
- Complex timing calculations
- Data structures and formats
- Integration patterns

### 2. RAG Workflow
```bash
# Generate context for specific PINT topic
make rag-dump QUERY="PINT timing model fitting" OUT=.cursor/rag_context.md

# Use in Cursor - the context file will be automatically loaded
# Ask questions like: "How do I integrate PINT timing model fitting?"
```

### 3. PINT Integration Patterns
- **Models**: Handle PINT data structures and calculations
- **Controllers**: Orchestrate PINT operations and emit signals
- **Views**: Display PINT results, never call PINT directly

---

## Testing Workflows

### 1. Unit Testing
```bash
# Test specific module
pytest tests/test_models.py -v

# Test with coverage
pytest tests/test_models.py --cov=pylk.models
```

### 2. Integration Testing
```bash
# Test Qt components
pytest tests/test_views.py -v

# Test full application
pytest tests/test_integration.py -v
```

### 3. Manual Testing
```bash
# Run the application
python run.py

# Test GUI functionality
# - Window opens correctly
# - Widgets respond to interactions
# - No console errors
```

---

## Code Review Process

### 1. Self-Review Before PR
```bash
# Run full quality gate
make full

# Check diff
git diff --cached

# Review checklist:
# - [ ] Code follows style guidelines
# - [ ] Tests are included
# - [ ] No PINT calls in widgets
# - [ ] Proper error handling
# - [ ] Documentation updated
```

### 2. PR Review
- [ ] Small, focused changes (< 300 LOC)
- [ ] Clear commit messages
- [ ] Tests included for new functionality
- [ ] No breaking changes without discussion

---

## Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Check if package is installed
pip list | grep pylk
```

#### 2. Qt/GUI Issues
```bash
# Check display forwarding (macOS)
echo $DISPLAY

# Test Qt import
python -c "from qtpy.QtWidgets import QApplication; print('Qt OK')"
```

#### 3. Test Failures
```bash
# Run with verbose output
pytest tests/test_specific.py -v -s

# Run with debugging
pytest tests/test_specific.py --pdb
```

#### 4. Pre-commit Failures
```bash
# Run specific hook
pre-commit run black --all-files

# Skip problematic hooks temporarily
SKIP=mypy make fast
```

### Getting Help
1. Check this document first
2. Look at existing code patterns
3. Use RAG for PINT-specific questions
4. Ask in team chat/issue tracker

---

## Workflow Summary

### Daily Development Loop
1. **Plan** → Define what you're building
2. **Research** → Use RAG if PINT integration needed  
3. **Code** → Follow MVC pattern, thin UI widgets
4. **Test** → Unit tests for logic, integration tests for UI
5. **Quality** → `make fast` for iteration, `make full` before commit
6. **Commit** → Conventional commit format
7. **Review** → Self-review checklist, then PR

### Key Principles
- **Thin UI**: Logic in controllers/models, not widgets
- **No PINT in widgets**: PINT calls only in models/controllers
- **Test-driven**: Add tests as you build
- **Iterative**: Small changes, frequent commits
- **Quality gates**: Use `make fast` and `make full` appropriately

This workflow ensures consistent, high-quality development while maintaining the project's architectural principles.
