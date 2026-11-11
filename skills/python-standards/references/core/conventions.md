# Conventions

Python conventions for modern (3.11+) projects. Apply to every `.py`, `pyproject.toml`, and `requirements*.txt`.

**Tradeoff**: bias toward strict-but-modern defaults. For one-off scripts or legacy codebases (3.8-, untyped, old Django), use judgment.

> **Before/after code lives in one place.** Every code example below has its implementation in [Conventions — Examples](./conventions-examples.md). Edit examples there, not here. For the tooling workflow, naming tables, import organization, project layout, CI/CD, and dependency management, see [Python Core Style & Toolchain](./style-toolchain.md).

## Function-first design

> **Preference, not a house rule.** This is the default posture of the `function-first-refactor` skill, applied when you want logic testable without mocks. It is not a blanket requirement on every Python project — flag it as a suggestion, not a violation.

- **Plain functions and modules by default.** Reach for a class only when it earns its place: it owns mutable state with an invariant, a framework requires it (Pydantic, SQLAlchemy, Django), it implements a `Protocol`/ABC, or it is a pure data container (`dataclass`)
- Keep logic in small, typed, pure functions that take inputs and return outputs; push I/O to the edges and pass dependencies in as arguments
- No classes that only group static methods or hold a single method — use a module and a function → [examples §16](./conventions-examples.md#16-functions-over-classes)
- Tests are plain `test_*` functions with fixtures, not `Test*` classes (see [testing.md](../safety/testing.md))

## Type discipline

- **Type hints required** on every function signature, public attribute, and return value (see [typing.md](./typing.md))
- `from __future__ import annotations` at top of files — gives forward-reference types and PEP 604 union (`A | B`) on older runtimes
- **Pydantic v2** for any external/IO model — never plain `dict[str, Any]` at API boundaries (see [frameworks.md](../frameworks/frameworks.md#pydantic-v2))
- `TypedDict` for internal dict shapes that don't need validation
- `Literal["a", "b"]` for string-literal enums (lighter than `enum.Enum`)

## Stdlib preferences

- `pathlib.Path` over `os.path` — composable, type-safe → [examples §3](./conventions-examples.md#3-pathlib-over-ospath)
- `dataclasses` (or Pydantic) over manually-written `__init__` for data containers → [examples §4](./conventions-examples.md#4-dataclasses-for-data-containers)
- `subprocess.run()` over `os.system` — actual return-code handling, list args, no shell → [examples §5](./conventions-examples.md#5-subprocessrun-over-ossystem)
- `f-strings` over `%` or `.format()` — except for logging, where lazy formatting matters
- `match` statements (3.10+) for tagged-union dispatch — cleaner than chained `isinstance` → [examples §6](./conventions-examples.md#6-match-for-tagged-union-dispatch)

## Async

- `async def` end-to-end — don't mix sync `requests` into an async stack; use `httpx` → [examples §7](./conventions-examples.md#7-asyncawait-end-to-end)
- `asyncio.gather` for parallel; `asyncio.TaskGroup` (3.11+) for structured concurrency with proper cancellation → [examples §8](./conventions-examples.md#8-taskgroup-for-structured-concurrency) and [async patterns](../concurrency/async.md)
- Never `time.sleep()` in async code — `await asyncio.sleep()` only

## Logging

- `structlog` if available in the project; else stdlib `logging` with structured extras
- **Never `print()`** in library code — only allowed in CLIs / scripts where stdout is the deliverable → [examples §10](./conventions-examples.md#10-no-print-in-libraries)
- Lazy formatting: `logger.info("user %s logged in", user_id)` not `logger.info(f"user {user_id}...")` — avoids string interpolation when log level is filtered → [examples §9](./conventions-examples.md#9-lazy-logging)

## Security

- No hardcoded secrets — environment variables only (see [security.md](../safety/security.md))
- Parameterized SQL, `subprocess.run([...], shell=False)`, no `eval`/`exec` on user input
- Passwords via bcrypt / Argon2 — see [security.md](../safety/security.md)

## Error handling

- No bare `except:` — catch specific exceptions (see [error-handling.md](../safety/error-handling.md))
- Preserve cause with `raise ... from`; log with context

## Tooling defaults

- **`uv`** over `pip` for new projects (faster, lockfile by default)
- **`ruff`** for lint + format (replaces `black` + `flake8` + `isort`)
- **`mypy --strict`** for type checking when the codebase tolerates it (see [typing.md](./typing.md) for checker selection)
- **`pytest`** with fixtures over class-based setup/teardown (see [testing.md](../safety/testing.md))
- **`bandit`** for static security linting
- **`safety`** for dependency vulnerability scanning
- **`uv-secure`** for project dependency security scanning

> The canonical run-commands for all of the above live in [style-toolchain.md → Standard Workflow](./style-toolchain.md#standard-workflow).

## Anti-patterns

- Bare `except:` clauses (catches `KeyboardInterrupt`, `SystemExit` — almost never what you want) → [error-handling.md](../safety/error-handling.md)
- Mutable default arguments (`def f(x=[]):` — use `None` and assign inside) → [examples §12](./conventions-examples.md#12-no-mutable-default-arguments)
- Catching exception just to re-raise (`except Exception: raise` — pointless)
- Stringly-typed return contracts (return enum/Literal/dataclass, not arbitrary strings) → [examples §14](./conventions-examples.md#14-stringly-typed-return--typed-return)
- `eval()` / `exec()` on user input
- `from foo import *`
- Mixing `Union[A, B]` and `A | B` — pick `A | B` (3.10+) → [typing.md](./typing.md)

## Canonical tool configuration

The single source of truth for `pyproject.toml`. Other docs must not redefine `[tool.ruff]`.

```toml
# pyproject.toml
[project]
name = "your-project"
version = "0.1.0"
requires-python = ">=3.11"   # floor; target 3.12 for new projects (see version.md)

[tool.ruff]
target-version = "py311"     # matches the 3.11 floor; raise requires-python to >=3.12 to opt into 3.12-only syntax
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B", "C4", "SIM", "RET", "ASYNC", "RUF"]
ignore = ["E501"]  # line length — ruff format handles it


[tool.mypy]
strict = true
python_version = "3.11"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

```bash
# Initialize (one-off bootstrap — full daily workflow in style-toolchain.md)
uv init
uv add ruff mypy pytest
uv add --dev pytest-cov
```

---

## Examples

The before/after code examples for every convention above live in a separate file:
[Conventions — Examples](./conventions-examples.md)
