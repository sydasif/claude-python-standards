# Python Version Policy

> Version policy backing [Conventions](./conventions.md). The canonical ruff config's `target-version` is `py312` (see [Conventions → Canonical tool configuration](./conventions.md#canonical-tool-configuration)).

- **Minimum**: Python 3.11+ (`requires-python = ">=3.11"`)
- **Target**: Python 3.12+ for new projects
- **CI matrix**: Test against >=3.11, <=3.13
- **Version pin**: `.python-version` file at project root
- **EOL policy**: Drop support when upstream reaches end‑of‑life

## Version‑Specific Features

| Python | Key features to leverage                                                                  |
| ------ | ----------------------------------------------------------------------------------------- |
| 3.10   | `match`/`case`, `X \| Y` union syntax, `TypeGuard`, `kw_only` & `slots=True` dataclasses  |
| 3.11   | `Self` type, `Never`, `typing.Unpack`, `asyncio.TaskGroup`                               |
| 3.12   | `@override`, `type` statement, perf improvements                                         |
| 3.13   | Free‑threaded mode (experimental), JIT compiler, improved `locals()`                      |

---

## Examples — leverage the version features

### 3.10 — `match`/`case` and `X | Y`

```python
def describe(status: str) -> str:
    match status:
        case "ok":
            return "succeeded"
        case "err":
            return "failed"
        case _:
            return "unknown"


def first(items: list[int]) -> int | None:  # PEP 604 union
    return items[0] if items else None
```

### 3.11 — `Self` and `asyncio.TaskGroup`

`Self` is for the rare case where a class is justified (see [Function-first design](./conventions.md#function-first-design)); `TaskGroup` is the part you will use most.

```python
from typing import Self


class Builder:
    def with_name(self, name: str) -> Self:  # returns the concrete subclass
        self.name = name
        return self


# structured concurrency — siblings are cancelled on first failure
async with asyncio.TaskGroup() as tg:
    for url in urls:
        tg.create_task(fetch(url))
```

### 3.12 — `@override` and `type` statement

```python
from typing import override


class Service(BaseService):
    @override
    def handle(self, req: Request) -> Response:  # fails at type-check if base signature changed
        ...

type Point = tuple[float, float]  # reusable type alias
```

### 3.13 — free‑threaded experimental note

```python
# Run with: python3.13t  (no GIL)
# CPU-bound work can use threads without the GIL; keep shared state lock-free or guarded.
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor() as ex:
    results = list(ex.map(cpu_bound, chunks))
```
