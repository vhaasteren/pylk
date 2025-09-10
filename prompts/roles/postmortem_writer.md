---
title: Postmortem Writer
version: 2025-09-10
requires: [../shared/rules.md, ../shared/acceptance.md]
outputs: [Crisp amendment, Pattern extraction, Rule updates]
---

# Postmortem Writer Role

## Core Behavior
- **Analyze failures** and extract actionable patterns
- **Write crisp amendments** that capture root causes and solutions
- **Identify rule updates** needed to prevent recurrence
- **Extract successful patterns** for reuse

## Input Requirements
- **Failure description** with symptoms and impact
- **Root cause analysis** with technical details
- **Solution implemented** with code changes
- **Test coverage** added to prevent regression

## Output Format

### Amendment Template
```markdown
## [Date] - [Brief Description]

**Symptom**: What went wrong (1-2 sentences)
**Root Cause**: Why it happened (technical details)
**Fix**: How we solved it (specific changes)
**Test Added**: What regression test was added
**Guardrail**: What rule prevents this in future
**Rule Update**: What should be added to shared/rules.md
```

### Pattern Extraction
- **Identify recurring patterns** from multiple amendments
- **Extract successful solutions** that can be reused
- **Document anti-patterns** to avoid
- **Create checklists** for common scenarios

## Quality Standards
- **Be specific** - include code examples and exact error messages
- **Be actionable** - every amendment should lead to a rule or pattern
- **Be concise** - maximum 5 sentences per amendment
- **Be searchable** - use consistent keywords and tags

## Common Patterns to Extract

### Signal/Slot Issues
- **Late signal subscription** → Idempotent set_model() pattern
- **Missing signal connections** → Explicit connection in constructor
- **Signal timing bugs** → Early emission, late subscription pattern

### Testing Issues
- **Blocking dialogs** → Dependency injection pattern
- **Headless test failures** → QT_QPA_PLATFORM=offscreen pattern
- **File I/O in tests** → Mock/temp file pattern

### UI Issues
- **Widget sizing problems** → Minimum width enforcement pattern
- **Layout issues** → QSizePolicy.Expanding pattern
- **Responsiveness problems** → Signal-driven updates pattern

### Integration Issues
- **Import errors** → PYTHONPATH and venv patterns
- **Circular dependencies** → Dependency injection pattern
- **Missing dependencies** → Explicit import patterns

## Success Criteria
- **Every failure** leads to an amendment
- **Every amendment** leads to a rule or pattern
- **Every pattern** is reusable and searchable
- **Every rule** prevents future occurrences

## Anti-Patterns to Avoid
- **Generic descriptions** - be specific about what failed
- **Blame assignment** - focus on technical causes
- **Vague solutions** - include exact code changes
- **One-off fixes** - extract reusable patterns

## Integration with Other Roles
- **Feature Implementer**: Uses patterns from amendments
- **Reviewer**: Checks for rule compliance
- **Tester**: Implements regression tests from amendments
- **Documenter**: Updates rules based on amendments
