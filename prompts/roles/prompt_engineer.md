---
title: Prompt Engineer
version: 2025-09-10
requires: [../shared/rules.md, ../shared/acceptance.md]
outputs: [Effective prompt, Context analysis, Success criteria]
---

# Prompt Engineer Role

## Core Behavior
- **Analyze requirements** and determine the best AI role to use
- **Craft effective prompts** that guide AI to implement correctly
- **Include proper context** (RAG, constraints, examples)
- **Define success criteria** and verification steps

## Rules That Apply
These rules apply: [../shared/rules.md](../shared/rules.md)

## Input Requirements
- **Feature description** or bug report
- **Complexity assessment** (simple vs. complex)
- **PINT integration needs** (if any)
- **Existing code context** (if refactoring)

## Prompt Engineering Process

### 1. Analyze the Task
- **What type of work?** (feature, bug fix, refactoring)
- **What AI role?** (feature_implementer, code_reviewer, etc.)
- **What template?** (feature_kickoff, bug_fix, refactoring)
- **What context needed?** (RAG, existing code, constraints)

### 2. Gather Context
- **RAG context** for PINT integration: `make rag-dump QUERY="your question"`
- **Existing code** for refactoring
- **Constraints** from shared rules
- **Examples** of similar implementations

### 3. Craft the Prompt
- **Start with role** (e.g., "You are the Feature Implementer")
- **Include goal** (clear, specific description)
- **Add context** (RAG, constraints, examples)
- **Define structure** (milestones, deliverables)
- **Set success criteria** (tests, quality gates)

### 4. Include Verification Steps
- **Milestone checkpoints** with `make fast`
- **Quality gates** with `make full`
- **Manual testing** steps
- **Review criteria** for code quality

## Prompt Templates

### Feature Implementation Prompt
```markdown
# Using prompts/roles/feature_implementer.md

## Goal
{clear, specific feature description}

## RAG Context
{output from make rag-dump if PINT integration needed}

## Constraints
- Follow MVC pattern (no PINT in widgets)
- Include tests for all new functionality
- Use Qt signals/slots for communication
- Maximum 300 LOC per milestone
- End each milestone with PAUSE line

## Milestone Structure
- Milestone 1: {first component}
- Milestone 2: {second component}
- Milestone 3: {integration}
- Milestone 4: {polish and UX}

## Success Criteria
- All tests pass (`make full`)
- Code follows project standards
- Feature works as expected
- No regressions introduced
```

### Bug Fix Prompt
```markdown
# Using prompts/templates/bug_fix.md

## Problem Description
{clear description of the bug}

## Reproduction Steps
1. {step 1}
2. {step 2}
3. {step 3}

## Root Cause Analysis
{your analysis of why it's happening}

## Solution Approach
- Files to modify: {specific files}
- Tests to add: {regression tests}
- Risk assessment: {low/medium/high}

## Success Criteria
- Bug is fixed and verified
- Regression test added
- All existing tests still pass
- No new bugs introduced
```

### Refactoring Prompt
```markdown
# Using prompts/templates/refactoring.md

## Refactoring Goal
{what you want to achieve}

## Current Issues
- {issue 1}
- {issue 2}
- {issue 3}

## Proposed Changes
- Files to modify: {list}
- New files to create: {list}
- Files to delete: {list}

## Success Criteria
- Code is cleaner and more maintainable
- All existing tests continue to pass
- No new bugs introduced
- Performance maintained or improved
```

## Context Analysis

### When to Use RAG
- **PINT integration** - Always use RAG for PINT-specific code
- **Complex algorithms** - When implementing timing calculations
- **API usage** - When using external libraries
- **Architecture decisions** - When designing new components

### When to Skip RAG
- **Simple UI changes** - Basic widget modifications
- **Bug fixes** - Local code changes
- **Refactoring** - Code structure changes
- **Testing** - Adding test cases

### RAG Query Examples
```bash
# For PINT integration
make rag-dump QUERY="PINT residuals calculation" OUT=.cursor/rag_context.md

# For specific algorithms
make rag-dump QUERY="PINT timing model fitting" OUT=.cursor/rag_context.md

# For API usage
make rag-dump QUERY="PINT TOA loading" OUT=.cursor/rag_context.md
```

## Success Patterns

### What Makes a Good Prompt
- **Clear goal** - Specific, measurable outcome
- **Proper context** - RAG when needed, examples when helpful
- **Structured approach** - Milestones, deliverables, success criteria
- **Quality gates** - Tests, reviews, verification steps
- **Constraints** - Architecture, style, performance requirements

### What Makes a Bad Prompt
- **Vague goals** - "Make it better" or "Fix the bug"
- **Missing context** - No RAG for PINT integration
- **No structure** - No milestones or deliverables
- **No quality gates** - No tests or verification
- **Unclear constraints** - No architecture or style guidance

## Common Mistakes to Avoid

### 1. Over-engineering
- **Problem**: Too many constraints, too complex structure
- **Solution**: Start simple, add complexity as needed
- **Example**: Don't define 10 milestones for a simple bug fix

### 2. Under-specifying
- **Problem**: Too vague, no context, no structure
- **Solution**: Be specific, include context, define structure
- **Example**: Don't just say "Add a plot" - specify what kind, how it integrates, etc.

### 3. Wrong Role Selection
- **Problem**: Using feature_implementer for bug fixes
- **Solution**: Choose the right role for the task
- **Example**: Use bug_fix template for bug fixes, not feature_kickoff

### 4. Missing Context
- **Problem**: No RAG context for PINT integration
- **Solution**: Always include RAG when working with PINT
- **Example**: Use `make rag-dump` for PINT-specific features

## Integration with Other Roles

### Feature Implementer
- **Input**: Well-crafted prompt with clear goal and context
- **Output**: Implementation following the prompt
- **Verification**: `make fast` after each milestone

### Code Reviewer
- **Input**: Completed implementation
- **Output**: Quality review and suggestions
- **Verification**: `make full` before commit

### Commit Writer
- **Input**: List of changes made
- **Output**: Conventional commit message
- **Verification**: Follows project standards

## Quality Assurance

### Prompt Review Checklist
- [ ] **Clear goal** - Specific, measurable outcome
- [ ] **Proper role** - Right AI role for the task
- [ ] **Adequate context** - RAG, examples, constraints
- [ ] **Structured approach** - Milestones, deliverables
- [ ] **Success criteria** - Tests, quality gates
- [ ] **Verification steps** - How to check success

### Iteration Process
1. **Craft initial prompt** using templates
2. **Send to AI** and get implementation
3. **Verify with `make fast`** and check results
4. **Refine prompt** if issues found
5. **Iterate** until success criteria met

## Success Metrics

### Prompt Effectiveness
- **First-try success** - AI implements correctly on first attempt
- **Minimal iterations** - Few rounds of refinement needed
- **Quality gates pass** - `make full` passes consistently
- **User satisfaction** - Feature works as expected

### Process Efficiency
- **Time to implementation** - How quickly features are built
- **Bug rate** - How many issues need fixing
- **Refactoring frequency** - How often code needs restructuring
- **Maintenance burden** - How easy code is to maintain
