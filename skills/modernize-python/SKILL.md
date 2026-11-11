---
name: modernize-python
description: Modernize a Python codebase to current standards with type hints, dataclasses, pathlib, f-strings, match statements, context managers, logging, and async hygiene, one package at a time. Use when the user asks to modernize, update, standardize, or apply Python best practices to a file, package, or codebase, or asks for "type hints everywhere", "move to pathlib", "use dataclasses". This is the mechanical, low-risk pass. It does NOT restructure code or separate I/O from logic - use function-first-refactor for that. Run cleanup-code first to prune dead code.
---

# Modernize Python

> Prune with `cleanup-code` first. Modernize code that _should exist_, not code that should be deleted.
> Restructuring logic vs. I/O is a different job: use `function-first-refactor` afterwards.

## Ground rules

- **Preserve behavior.** Outputs, error types, and side-effect order stay identical unless the user asks otherwise.
- **Types and syntax, not structure.** Dataclasses are fine as plain records (prefer `frozen=True`). Converting classes to functions, or splitting logic from I/O, is structural — that is `function-first-refactor`'s job, not this pass (checklist Section 6).
- **Skip when** the code is already clear and short, the feature is gated above the project's minimum Python, the file is generated or one-off, or the new construct is heavier than what it replaces.
- **Stay in the user's style** and test framework (pytest by default).

## Process

### 1. Scope (codebase-sized work)

Never modernize a whole codebase in one sweep. Pick a unit (one package or directory), say which in one line, and finish it before the next. After each unit, stop and summarize so the user can review and commit. If the user said "the whole codebase", do it unit by unit, starting with the most-imported modules.

### 2. Assess

1. **Minimum Python version**: check `pyproject.toml`, `setup.cfg`, `.python-version`, CI config. Use only features at or below that floor.
2. **Inventory** against `references/checklist.md`: _applies and safe_, _needs version check_, _changes behavior - confirm first_, or _not present_.

### 3. Baseline

Record results before touching anything. Defaults for a `uv` project (adapt to actual tooling and layout):

```bash
uv run mypy src/
uv run ruff check .
uv run pytest --tb=short
uv run pytest --cov=src --cov-report=term-missing
```

Flag pre-existing failures so they aren't mistaken for regressions. If the unit has no tests, say so; behavior-preservation can't be verified, so keep changes to the safest mechanical ones.

### 4. Apply

1. Run `pyupgrade` / `ruff --fix` first for bulk mechanical changes. Reserve manual work for structural ones.
2. Apply one pattern at a time across the unit, run tests after each.
3. Checklist items marked **[behavior change]** (print to logging, configparser to tomllib, narrowing broad `except`) are applied only if the user wants them; otherwise list them as suggestions.

Examples for each pattern: `references/scenarios.md`.

### 5. Verify

Re-run the baseline. Pass: no new mypy errors, no new lint violations, test pass rate same or better, coverage at or above baseline.

## Report

1. What was changed, per pattern, and in which files.
2. Baseline vs. after for tests, types, lint.
3. Behavior-changing modernizations held back for approval.
4. Purity smells spotted (functions mixing I/O and logic) - list them, don't fix them; suggest `function-first-refactor`.

## See also

`cleanup-code` (run first) - `function-first-refactor` (structure) - `review-code` (final gate)
