# Python Core Style & Toolchain

Owns the **day-to-day tooling workflow**: required toolchain, `uv run …` commands,
security-scan gates, naming conventions, import organization, project layout, CI/CD,
dependency management, and pre-commit.

> **Rule source of truth:** the coding rules themselves (stdlib preferences, async,
> logging, anti-patterns) live in [Conventions](./conventions.md); every before/after
> code block in [Conventions — Examples](./conventions-examples.md). The **single
> canonical `[tool.ruff]` config** is in
> [Conventions → Canonical tool configuration](./conventions.md#canonical-tool-configuration).
> Do not redefine it here.

## Required Toolchain

| Tool        | Purpose                               |
| ----------- | ------------------------------------- |
| `uv`        | Environment management + dependencies |
| `ruff`      | Linting + formatting                  |
| `mypy`      | Static type checking                  |
| `pytest`    | Test runner                           |
| `bandit`    | Security linting                      |
| `safety`    | Dependency vulnerability scanning     |
| `uv-secure` | Project dependency security scanning  |

## Standard Workflow

Ruff linting and formatting apply automatically to edited Python files via a `PostToolUse` hook.

```bash
uv sync                        # Install dependencies
uv run ruff check --fix .      # Lint and auto-fix
uv run ruff format .           # Format code
uv run mypy src/               # Type check (strict)
uv run pytest                  # Run tests
uv run bandit -r src/          # Security analysis
uv run safety scan             # Dependency security
uv run uv-secure               # Project security scanning
```

## Security Scans

- `safety`: Medium+ severity = blocking. Halt until user confirms.
- `bandit`: HIGH severity or HIGH confidence = blocking. Report others.
- `uv-secure`: Any vulnerability = blocking. Halt until user confirms.

## Naming Conventions (PEP 8)

| Element                       | Convention            |
| ----------------------------- | --------------------- |
| Functions, variables, modules | `snake_case`          |
| Classes, exceptions           | `PascalCase`          |
| Constants                     | `UPPER_CASE`          |
| Private attributes            | `_leading_underscore` |

## Import Organization

1. Standard library
2. Third-party
3. Local application

Blank lines between groups. Absolute imports preferred. Prefer `from module import name` over `import module.name`.

### Detailed example

```python
# Standard library
import os
import sys
from pathlib import Path
from typing import Any

# Third-party
import httpx
from pydantic import BaseModel

# Local application
from app.config import settings
from app.models import User
```

Within each group, alphabetize. ruff's `I` rule enforces this.

`__init__.py` re-export example (used sparingly — explicit imports are usually clearer):

```python
# app/__init__.py
from .models import User, Order  # noqa: F401
```

### `__all__` for public API

```python
# app/parsers.py
__all__ = ["parse_yaml", "parse_toml"]

def parse_yaml(...): ...
def parse_toml(...): ...
def _internal_helper(): ...  # private; not in __all__
```

`__all__` documents intent and helps `ruff` enforce unused-export rules.

## Project layout

```
project/
  src/
    app/
      __init__.py
      main.py
      routers/
      services/
      models/
  tests/
    conftest.py
    test_main.py
  pyproject.toml
  uv.lock
  README.md
```

The `src/` layout (rather than flat) prevents accidental imports of in-tree
code without `uv sync` — a common debugging time-sink.

## Dependency Management

Use `uv`. No direct `pip install`. Use `pyproject.toml` and `uv.lock`. Update via `uv lock --upgrade`. Remove unused dependencies.

## CI/CD Integration

Canonical sources, one copy each — do not create a second version:

- `pyproject.toml` / `[tool.ruff]` — [Canonical tool configuration](conventions.md#canonical-tool-configuration); copy to the project root
- CI workflow — [GitHub Actions recipe](../tooling/package-management.md#31-github-actions); copy to `.github/workflows/test.yml`
- `Dockerfile` — [multistage Dockerfile with uv](../tooling/docker-management.md); adapt `ENTRYPOINT`
- `pre-commit` — no template file; install with `uv run pre-commit install` (below)

### Pre-commit

Install hooks once per clone:

```bash
uv run pre-commit install
```

Run hooks on all files:

```bash
uv run pre-commit run --all-files
```

---

## Examples

### Naming (PEP 8)

**Before:**

```python
class userAccount:          # should be PascalCase
    MAX_RETRIES = 3
    def GetName(self):      # methods are snake_case
        ...
def calc_total(List):       # variables/args are snake_case
    ...
```

**After:**

```python
class UserAccount:
    MAX_RETRIES = 3

    def get_name(self) -> str:
        ...

def calc_total(items: list[Item]) -> int:
    ...
```

### Import grouping

**Before** (stdlib/third-party/local interleaved, wrong order):

```python
from app.models import User
import httpx
import os
from pydantic import BaseModel
import sys
```

**After** (std → third-party → local, alphabetized within groups):

```python
import os
import sys

import httpx
from pydantic import BaseModel

from app.models import User
```

### Walrus `:=` — assign and test in one expression

**Before:**

```python
line = f.readline()
while line:
    process(line)
    line = f.readline()
```

**After:**

```python
while (line := f.readline()):
    process(line)
```
