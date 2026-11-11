---
name: python-standards
description: Python coding standards for modern (3.11+) projects - strict typing, ruff/mypy config, uv packaging, pytest testing, async patterns, error handling, security, docstrings, Docker, and FastAPI/Pydantic/SQLAlchemy/Django/Flask conventions. Use this skill whenever the user writes, reviews, refactors, scaffolds or configures Python code or a Python project (pyproject.toml, ruff, mypy, uv, pytest, Dockerfile for Python, type hints, docstrings, asyncio, logging), or asks what the "standard" or "best practice" is for Python, even if they don't mention standards explicitly.
---

# Python Standards

House rules for writing Python. The rules are split into focused reference files so you load only what the task needs. Following them keeps new code consistent with the rest of the codebase and avoids re-deciding the same questions (typing strictness, tooling, error handling) on every task.

## How to use

1. Read `references/index.md` once: each topic has exactly one owning file, so it tells you where a rule lives.
2. Read only the reference file(s) matching the task (table below). For a review or broad refactor, start with `core/conventions.md`, then add the files for the areas the code touches.
3. Apply the rules. When existing project code conflicts with them, follow the project's established style unless the user asks for a migration, and mention the difference briefly.
4. For a one-off script or a legacy codebase (3.8-, untyped), use judgment instead of full strictness; the conventions file explains the tradeoff.

## Core defaults (always in force)

- Python 3.11+ floor, 3.12 target; type hints on every signature; `X | Y` unions.
- `uv` for environments and dependencies, `ruff` for lint and format, `mypy --strict`, `pytest`.
- Specific exceptions only, `raise ... from`, no bare `except`; no hardcoded secrets; `pathlib`, `subprocess.run`, lazy logging, no `print()` in libraries.

These defaults are what the code-quality passes enforce: `cleanup-code` prunes first, `modernize-python` applies the mechanical syntax and typing rules, and `review-code` is the final gate.

## Preferences (opt-in, owned by their own skills)

Not house rules. Apply them when the task calls for them:

- **Function-first / functional core** — plain functions over classes, pure logic separated from I/O: owned by `function-first-refactor`. The rationale, the scope where it is justified, and the refactoring process live there; the short form is in [`references/core/conventions.md#function-first-design`](references/core/conventions.md#function-first-design).

## Which reference to read

`references/index.md` is the **only** task → file map. Read it, then open only the
file(s) the task needs — do not scan this folder for the right file.

## Single sources of truth

- The `pyproject.toml` / `[tool.ruff]` configuration lives only in `references/core/conventions.md` (Canonical tool configuration). Copy it from there; do not invent a second config.
- Before/after code examples live only in `references/core/conventions-examples.md`. When asked to add or change an example, edit it there and keep the rule files linking to it.
- Keep `references/index.md` in sync when adding, moving or renaming a reference file.
