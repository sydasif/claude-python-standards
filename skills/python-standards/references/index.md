# Python Standards — Index

Topic map for the Python standards docs. Each topic has **one owning file**; code
examples live in exactly one place. This index is the entry point — read it before
editing any file so you don't re-duplicate.

## Topic → owning file

| Topic | Owner | Notes |
| --- | --- | --- |
| Coding conventions (rules) | [core/conventions.md](core/conventions.md) | Canonical rules, ruff config, bootstrap; function-first is marked there as a preference |
| Before/after code library | [core/conventions-examples.md](core/conventions-examples.md) | **Sole** home for all code examples |
| Tooling workflow, naming, imports, layout, CI/CD | [core/style-toolchain.md](core/style-toolchain.md) | `uv run …` commands, pre-commit |
| Python version policy | [core/version.md](core/version.md) | floor 3.11, target 3.12 |
| Type hints | [core/typing.md](core/typing.md) | strict mode, `mypy` selection |
| Docstrings | [core/docstrings.md](core/docstrings.md) | Google style (PEP 257) |
| Security rules | [safety/security.md](safety/security.md) | secrets, SQL, password hashing |
| Error handling | [safety/error-handling.md](safety/error-handling.md) | `raise … from`, `with` |
| Testing | [safety/testing.md](safety/testing.md) | pytest, AAA, coverage |
| Async patterns | [concurrency/async.md](concurrency/async.md) | `TaskGroup`, `gather`, anti-patterns |
| Performance | [concurrency/performance.md](concurrency/performance.md) | generators, `itertools`, caches |
| Frameworks | [frameworks/frameworks.md](frameworks/frameworks.md) | FastAPI, Pydantic, SQLAlchemy, Django, Flask |
| `uv` command reference | [tooling/package-management.md](tooling/package-management.md) | install, versions, CI recipes |
| Docker + `uv` | [tooling/docker-management.md](tooling/docker-management.md) | multistage Dockerfiles |

## Canonical configuration

The single `[tool.ruff]` config and `pyproject.toml` live in
[core/conventions.md → Canonical tool configuration](core/conventions.md#canonical-tool-configuration).
No other file may define `[tool.ruff]`.
