---
name: budget-cli-tdd
description: TDD workflow for developing a Python CSV-based budget CLI application. Use when implementing or refactoring budget app features such as transaction creation, CSV loading, balance calculations, category filtering, monthly summaries, CLI behavior, tests, radon complexity checks, or commit-ready QA for this repository.
---

# Budget CLI TDD

## Overview

Use this skill to develop the CSV budget CLI app in small, test-first slices.
Keep the implementation simple, typed, and easy to review.

## Workflow

1. Inspect the relevant sample CSV under `data/` before designing tests.
2. Add or update tests first. Prefer realistic rows from the sample CSV files.
3. Run the targeted tests and confirm they fail for the intended behavior when
   practical.
4. Implement the smallest production change that satisfies the tests.
5. Run `pytest`.
6. Run `radon cc .` and keep every function at complexity 10 or below.
7. Refactor only after tests pass.
8. Before committing, invoke or emulate the `qa_engineer` review checklist from
   `.codex/agents/qa_engineer.yaml`.

## Project Rules

- Use type hints on every function.
- Keep each function at 50 lines or fewer.
- Keep cyclomatic complexity at 10 or below.
- Keep CSV I/O separate from pure calculation logic where possible.
- Treat `amount` signs consistently: positive values are income and negative
  values are expenses.
- Preserve CSV compatibility with UTF-8 BOM files by using `utf-8-sig` when
  loading project CSV data.

## Test Design

Cover normal behavior and edge cases for each feature:

- Empty transaction lists.
- Positive income and negative expense amounts.
- Empty descriptions and optional memo-like fields.
- Case-insensitive category matching.
- Missing or unknown categories.
- CSV numeric conversion for `amount`.
- Large file behavior with `data/step4_large_transactions.csv` when relevant.

## Commands

Run the project checks before commit:

```bash
pytest
radon cc .
```

## Commit Readiness

Commit after one complete feature is implemented, tested, and reviewed. Push the
feature commit after committing.
