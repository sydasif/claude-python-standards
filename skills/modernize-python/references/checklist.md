# Modernization Checklist

Items marked **[behavior change]** alter runtime behavior or file formats. Apply only when the user wants them, otherwise list them as suggestions.

## Section 1: Type System

- [ ] Add type hints to function signatures (inputs and return values)
- [ ] Use keyword-only arguments where callers should not rely on positional order
- [ ] Replace structured dicts passed between functions with `TypedDict` or dataclasses

## Section 2: Syntax Modernization

- [ ] Replace `%` and `.format()` string formatting with f-strings (but not inside `logger.*` calls - see Section 3)
- [ ] Replace `os.path.*` path operations with `pathlib`
- [ ] Replace `configparser` with `tomllib` (3.11+) or `tomli` **[behavior change: changes the config file format; only on request]**
- [ ] Replace long `if/elif` chains over a single variable with `match` statements (Python 3.10+ only)

## Section 3: Structural Improvements

- [ ] Replace simple attribute-only classes with `@dataclass` (prefer `frozen=True` for values passed between pure functions)
- [ ] Replace classes that only group static methods, or that have one method besides `__init__`, with plain module-level functions — **only on request**: this is the `function-first-refactor` preference, not a mechanical modernization. List it as a suggestion unless the user asked for that pass.
- [ ] Remove boilerplate methods (`__init__`, `__repr__`, `__eq__`) where dataclass covers them
- [ ] Add `__slots__` (or `@dataclass(slots=True)` on 3.10+) to hot-path dataclasses where memory efficiency matters
- [ ] Move complex lambda functions to named functions
- [ ] Use appropriate iteration patterns: `enumerate`, list/dict/set comprehensions, `zip`
- [ ] Use context managers for all file, socket, and connection resources
- [ ] Replace bare `except:` or `except Exception:` without re-raise with specific exception types **[behavior change: can let previously swallowed errors propagate]**
- [ ] Replace diagnostic `print` statements with `logging` calls at appropriate levels **[behavior change: output moves from stdout to the logging config; leave CLI user-facing output as `print`]**. Place the calls in orchestration or effect code, not in pure functions.

## Section 4: Async (if applicable)

- [ ] Use consistent `asyncio` patterns - no sync blocking calls (e.g., `time.sleep`, `open()`) inside async functions
- [ ] Use `async with` and `async for` where available on async-capable resources
- [ ] Await all coroutines - unawaited coroutines do nothing
- [ ] Use `asyncio.gather()` for concurrent independent tasks instead of sequential `await` calls
- [ ] Replace `asyncio.sleep(0)` busy-loops with proper event-driven patterns

## Section 5: Imports

- [ ] Organize imports in standard groups: stdlib -> third-party -> local
- [ ] Remove unused imports

## Section 6: Purity smells (hand off to function-first-refactor)

Spot these while inventorying; list them in the report, do not fix them here.

- [ ] Functions that both decide and do I/O (DB/HTTP/SMTP/file/device calls next to validation, calculations, formatting)
- [ ] `datetime.now()`, `random`, `os.environ` read inside logic
- [ ] Mutable default arguments; in-place mutation of arguments
- [ ] Logging inside business-rule functions
- [ ] Tests that need heavy mocking to exercise simple logic
