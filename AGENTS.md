# AGENTS.md

## Project

This repository is a Python CLI budget application. It manages household budget
transactions using CSV files as the primary data source.

## Coding Rules

- Use Python type hints for every function signature.
- Keep each function at 50 lines or fewer.
- Prefer small, pure functions for CSV parsing, filtering, calculation, and
  formatting logic.
- Keep user-facing CLI code separate from core budget calculation logic.

## TDD Rules

- Write or update tests before implementing production code.
- Confirm the new test fails for the expected reason before adding the
  implementation when practical.
- Implement only enough code to satisfy the current tests, then refactor.

## Quality Rules

- Keep cyclomatic complexity at 10 or below for every function.
- Use simple control flow and helper functions when branching starts to grow.
- Avoid hidden I/O in core calculation functions; pass data in and return data
  out where possible.

## QA Review Rules

- Before every commit, run the `qa_engineer` subagent for quality review.
- The `qa_engineer` review must check tests, type hints, function length,
  cyclomatic complexity, edge cases, and CSV data handling.
- Fix any blocking QA findings before committing.

## Test And Quality Commands

Run these before committing:

```bash
pytest
radon cc .
```

## Commit Rules

- Commit after one complete feature is developed and verified.
- Push the feature commit after committing.
- Keep commits focused on a single feature or quality fix.
