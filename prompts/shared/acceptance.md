# Shared Acceptance Criteria

## Definition of Done

### Code Quality
- [ ] All code passes pre-commit hooks (black, ruff, mypy)
- [ ] All new code has appropriate type hints
- [ ] All public APIs have docstrings
- [ ] Code follows project style guidelines

### Testing
- [ ] All new functionality has tests
- [ ] Tests pass in headless environment (`QT_QPA_PLATFORM=offscreen`)
- [ ] Integration tests cover UI interactions
- [ ] Unit tests cover business logic
- [ ] Test coverage >80% for new code

### Documentation
- [ ] CHANGELOG.md updated for user-facing changes
- [ ] README.md updated if needed
- [ ] Code comments explain complex logic
- [ ] API documentation updated

### Integration
- [ ] All imports resolve correctly
- [ ] No circular dependencies
- [ ] Signal/slot connections work properly
- [ ] UI components render correctly
- [ ] File operations work in test environment

### Performance
- [ ] No memory leaks in UI components
- [ ] Reasonable response times for user interactions
- [ ] Efficient data loading and processing
- [ ] Proper cleanup of resources

## Quality Metrics

### Milestone Metrics
- **Size**: 200-300 LOC per milestone (target)
- **Duration**: <30 minutes per milestone (target)
- **Amendment rate**: <20% of milestones need fixes (target)
- **Time to green**: <5 minutes from PAUSE to `make fast` success (target)

### Code Quality Metrics
- **Pre-commit pass rate**: >90% on first try (target)
- **Test coverage**: >80% for new code (target)
- **Type coverage**: >70% for new code (target)
- **Linting errors**: 0 warnings (required)

### Process Health Metrics
- **Context switching**: Minimize role changes within milestone
- **Error recovery**: Quick resolution of `make fast` failures
- **Integration success**: Smooth handoff between milestones
- **Documentation completeness**: All user-facing changes documented

## Success Patterns

### What We've Learned Works
- **Rich initial context** with detailed requirements and constraints
- **Test-first approach** with integration tests for UI components
- **Idempotent set_model()** methods that render current state immediately
- **Dependency injection** for file operations and external dependencies
- **Signal/slot patterns** with early emission and late subscription
- **Widget sizing policies** with minimum width enforcement

### What We've Learned to Avoid
- **Blocking dialogs in tests** - use dependency injection instead
- **PINT imports in widgets** - use dependency injection instead
- **Late signal emission** - emit signals immediately when data changes
- **Hardcoded file paths** - use dependency injection instead
- **Missing error handling** - always provide user feedback

## Failure Modes

### Common Issues and Solutions
- **Import errors**: Check PYTHONPATH and virtual environment
- **Signal timing**: Ensure early emission and idempotent subscription
- **Widget sizing**: Use QSizePolicy.Expanding and minimum width enforcement
- **Test failures**: Use headless Qt and dependency injection
- **Pre-commit failures**: Fix formatting and linting issues

### Recovery Procedures
- **When `make fast` fails**: Fix immediate issue, re-run, continue only after green
- **When tests fail**: Read error message, fix root cause, add regression test
- **When pre-commit fails**: Fix formatting/linting, re-run hooks
- **When integration fails**: Check signal connections and widget sizing

## Measurement and Improvement

### Weekly Review Questions
- What patterns worked well this week?
- What failure modes did we encounter?
- How can we improve our process?
- What new patterns should we codify?

### Monthly Metrics Review
- Track milestone size, duration, and amendment rate
- Monitor code quality metrics and trends
- Identify process improvements and bottlenecks
- Update rules and patterns based on learnings
