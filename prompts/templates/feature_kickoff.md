# Feature Kickoff Template

## Goal
{goal}

## Context
- **RAG Context**: {rag_dump}
- **Constraints**: Follow prompts/shared/rules.md
- **Architecture**: MVC pattern with Qt signals/slots

## Deliverables
1. **Short plan** (steps + risks)
2. **Direct file modifications** (no diffs)
3. **Tests** (unit for models/controllers, integration for UI)
4. **Post-merge follow-ups** (bullets)

## Milestone Structure
- **Maximum 300 LOC per milestone**
- **End each milestone with PAUSE line**
- **Run `make fast` after each milestone**

## Success Criteria
- Code follows MVC pattern (no PINT in widgets)
- All tests pass (`make full`)
- Pre-commit hooks pass
- CHANGELOG.md updated for user-facing changes
