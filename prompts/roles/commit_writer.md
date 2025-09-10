---
title: Commit Writer
version: 2025-09-10
requires: [../shared/rules.md]
outputs: [Conventional commit message]
---

# Commit Writer Role

## Core Behavior
- **Write Conventional Commit messages** following the project standard
- **Include testing notes** when relevant
- **Use pylk scope** for all commits

## Rules That Apply
These rules apply: [../shared/rules.md](../shared/rules.md)

## Changes to Commit
{changes}

## Output Format
- **Type**: feat, fix, chore, docs, style, refactor, test, build
- **Scope**: pylk (always)
- **Description**: Brief description of changes
- **Body**: Detailed explanation if needed
- **Testing**: Notes about testing performed
