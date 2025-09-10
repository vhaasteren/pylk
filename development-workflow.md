# Development Workflow (Pylk)

This document provides the **human developer's workflow** for AI-assisted development in Pylk. You don't implement code directly—you craft prompts that guide the AI assistant to implement features correctly.

## Table of Contents
- [Quick Reference](#quick-reference)
- [The AI-Assisted Development Loop](#the-ai-assisted-development-loop)
- [Prompt Engineering Workflow](#prompt-engineering-workflow)
- [Feature Development Process](#feature-development-process)
- [Bug Fix Process](#bug-fix-process)
- [Refactoring Process](#refactoring-process)
- [Verification and Quality Gates](#verification-and-quality-gates)
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

# Generate AI planning context into Cursor-visible folder
make ai-plan GOAL="your feature goal" AI_OUT=.cursor/cursor_context.md

# Show shared rules
make show-rules
```

### Branch Naming
- `feat/<yourname>/<slug>` - New features
- `fix/<yourname>/<slug>` - Bug fixes  
- `chore/<yourname>/<slug>` - Maintenance tasks

### AI/LLM Workflow
> **🤖 For AI-assisted development, see [`prompts/`](prompts/) directory**  
> **📋 Role-based prompts in [`prompts/roles/`](prompts/roles/)**  
> **📝 Reusable templates in [`prompts/templates/`](prompts/templates/)**

---

## The AI-Assisted Development Loop

### Core Workflow
1. **Plan** → Define what you're building
2. **Research** → Use RAG if PINT integration needed  
3. **Prompt** → Craft the perfect prompt for the AI
4. **Iterate** → AI implements, you verify with `make fast` and interactive runs
5. **Review** → Use AI reviewer role for quality check
6. **Commit** → Use AI commit writer for conventional commits

### Key Principle
**You are the architect and quality gate. The AI is your implementation partner.**

---

## Prompt Engineering Workflow

### 1. Choose Your Role
Select the appropriate AI role from `prompts/roles/`:
- **`prompt_engineer.md`** - For crafting effective prompts (meta-role)
- **`feature_implementer.md`** - For new features
- **`code_reviewer.md`** - For quality review
- **`commit_writer.md`** - For commit messages
- **`rag_question.md`** - For PINT-specific questions
- **`postmortem_writer.md`** - For analyzing failures

### 2. Use Templates
Start with templates from `prompts/templates/`:
- **`feature_kickoff.md`** - For new features
- **`bug_fix.md`** - For bug fixes
- **`refactoring.md`** - For code refactoring

### 3. Craft Your Prompt

#### Option A: Use Prompt Engineer Role (Recommended)
```markdown
# Using prompts/roles/prompt_engineer.md

## Task
Add pre-fit residuals plotting functionality

## Requirements
- Load PAR+TIM files via PINT
- Compute pre-fit residuals
- Display in matplotlib widget
- Follow MVC pattern with Qt signals

## Context
- PINT integration needed
- New feature (not bug fix or refactoring)
- Medium complexity

## Success Criteria
- Feature works as expected
- All tests pass
- Code follows project standards
- No regressions
```

#### Option B: Direct Role Usage
```markdown
# Using prompts/roles/feature_implementer.md

## Goal
Add pre-fit residuals plotting functionality

## RAG Context
[Paste output from `make rag-dump QUERY="PINT residuals calculation"`]

## Constraints
- Follow MVC pattern (no PINT in widgets)
- Include tests for all new functionality
- Use Qt signals/slots for communication
- Maximum 300 LOC per milestone
```

### 4. Iterate and Refine
- **First prompt** → Get initial implementation
- **Verification** → Run `make fast` to check
- **Refinement** → Ask AI to fix issues or add features
- **Review** → Use reviewer role for quality check

---

## Feature Development Process

### Phase 1: Planning and Research

#### 1.1 Define the Feature
- [ ] Write a clear, specific feature description
- [ ] Identify affected components (UI, controllers, models)
- [ ] Determine if PINT integration is needed
- [ ] Estimate complexity and break into milestones

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

### Phase 2: Prompt Engineering

#### 2.1 Choose Your Approach
- **Simple features** → Use `prompts/roles/feature_implementer.md` directly
- **Complex features** → Use `prompts/templates/feature_kickoff.md` + role
- **PINT integration** → Include RAG context from step 1.2

#### 2.2 Craft Your Prompt
```markdown
# Example: Using feature_implementer.md

## Goal
Add pre-fit residuals plotting functionality that:
- Loads PAR+TIM files via PINT
- Computes pre-fit residuals
- Displays them in a matplotlib widget
- Follows MVC pattern with Qt signals

## RAG Context
[Paste your RAG output here]

## Milestone Structure
- Milestone 1: PulsarModel + ProjectController
- Milestone 2: PlkView widget
- Milestone 3: MainWindow integration
- Milestone 4: Polish and UX

## Constraints
- No PINT calls in widgets
- Include tests for all functionality
- Use Qt signals/slots
- Maximum 300 LOC per milestone
```

#### 2.3 Send to AI
- Paste your crafted prompt into Cursor
- Let the AI implement the first milestone
- **PAUSE** after each milestone for verification

### Phase 3: Verification and Iteration

#### 3.1 Verify Each Milestone
```bash
# After each AI milestone
make fast

# If issues found, ask AI to fix:
# "The tests are failing because of import errors. Please fix the imports and re-run make fast."
```

#### 3.2 Iterate and Refine
- **Fix issues** → Ask AI to address specific problems
- **Add features** → Request additional functionality
- **Improve UX** → Ask for UI/UX enhancements
- **Add tests** → Request more comprehensive test coverage

#### 3.3 Quality Review
```markdown
# Use prompts/roles/code_reviewer.md

## Review Target
Review these changes for Pylk:

[Paste the changes the AI made]

## Focus Areas
- MVC pattern compliance
- Test coverage
- Code quality
- Performance considerations
```

### Phase 4: Finalization

#### 4.1 Final Quality Gate
```bash
# Run full quality checks
make full

# If issues found, ask AI to fix them
```

#### 4.2 Generate Commit Message
```markdown
# Use prompts/roles/commit_writer.md

## Changes to Commit
[Describe what was implemented]

## Testing
- All tests pass
- Manual testing completed
- No regressions found
```

#### 4.3 Commit and Push
```bash
# Stage changes
git add .

# Commit with AI-generated message
git commit -m "feat(residuals): add pre-fit residuals plotting

- Add PulsarModel with PINT integration
- Add ProjectController for project lifecycle
- Add PlkView with matplotlib plotting
- Include comprehensive tests

Testing: All tests pass, manual testing completed"
```

---

## Bug Fix Process

### 1. Reproduce and Analyze
- [ ] Reproduce the bug consistently
- [ ] Identify root cause
- [ ] Determine affected components

### 2. Craft Bug Fix Prompt
```markdown
# Using prompts/templates/bug_fix.md

## Problem Description
Widget sizing issue: matplotlib widget is tiny on first load

## Root Cause Analysis
The widget doesn't have proper size policies set

## Solution Approach
- Files to modify: pylk/widgets/plk_view.py
- Tests to add: widget sizing tests
- Risk assessment: Low risk, UI-only change
```

### 3. AI Implementation
- Send prompt to AI
- Verify fix with `make fast`
- Iterate if needed

### 4. Quality Check
- Use reviewer role to check the fix
- Ensure regression test is added
- Verify no new bugs introduced

---

## Refactoring Process

### 1. Identify Refactoring Need
- [ ] Identify code smells or technical debt
- [ ] Plan the refactoring approach
- [ ] Ensure comprehensive test coverage exists

### 2. Craft Refactoring Prompt
```markdown
# Using prompts/templates/refactoring.md

## Refactoring Goal
Extract common signal handling into base class

## Current Issues
- Duplicate signal connection code
- Inconsistent error handling
- Hard to maintain

## Proposed Changes
- Files to modify: pylk/widgets/plk_view.py, pylk/widgets/par_editor.py
- New files to create: pylk/widgets/base_widget.py
- Files to delete: None
```

### 3. AI Implementation
- Send prompt to AI
- Verify with `make fast`
- Ensure all tests still pass

---

## Verification and Quality Gates

### Milestone Verification
After each AI milestone:
```bash
# Quick check
make fast

# If issues found, ask AI to fix:
# "The import is failing. Please fix the import statement and re-run make fast."
```

### Pre-commit Verification
Before committing:
```bash
# Full quality gate
make full

# If issues found, ask AI to fix:
# "The pre-commit hooks are failing. Please fix the formatting and linting issues."
```

### Manual Testing
- [ ] Run the application: `python run.py`
- [ ] Test the new functionality
- [ ] Verify no regressions
- [ ] Check UI responsiveness

---

## Troubleshooting

### Common Issues

#### 1. AI Implementation Issues
- **Problem**: AI didn't follow the prompt correctly
- **Solution**: Be more specific in your prompt, include examples
- **Prevention**: Use templates and be explicit about constraints

#### 2. Test Failures
- **Problem**: Tests fail after AI implementation
- **Solution**: Ask AI to fix the specific test failures
- **Example**: "The test is failing because of import errors. Please fix the imports."

#### 3. Pre-commit Failures
- **Problem**: Code doesn't pass pre-commit hooks
- **Solution**: Ask AI to fix formatting/linting issues
- **Example**: "Please fix the Black formatting and Ruff linting issues."

#### 4. Integration Issues
- **Problem**: Components don't work together
- **Solution**: Ask AI to fix the integration, be specific about the issue
- **Example**: "The signal connection isn't working. Please fix the signal/slot connections."

### Getting Help
1. **Check shared rules**: `make show-rules`
2. **Use RAG for PINT questions**: `make rag-dump QUERY="your question"`
3. **Use reviewer role**: For quality issues
4. **Use postmortem writer**: For analyzing failures

---

## Key Principles

### For Human Developers
- **You are the architect** - Define what to build
- **You are the quality gate** - Verify and approve changes
- **You are the prompt engineer** - Craft effective prompts
- **You are the integrator** - Ensure everything works together

### For AI Assistant
- **Follow the rules** - Always reference `prompts/shared/rules.md`
- **Implement incrementally** - One milestone at a time
- **Include tests** - For all new functionality
- **Be responsive** - Fix issues when asked

### Success Metrics
- **Prompt effectiveness** - AI implements correctly on first try
- **Iteration speed** - Quick fixes with `make fast`
- **Quality gates** - `make full` passes consistently
- **User experience** - Features work as expected

This workflow ensures you maintain control while leveraging AI for implementation, resulting in high-quality, well-tested code that follows project standards.