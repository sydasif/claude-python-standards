# Explicit Error Handling

Owns error-handling rules and the patterns unique to this topic (`raise ... from`,
`with` for resources). The no-bare-except and no-`print`/lazy-logging rules are kept in
[Conventions — Examples](../core/conventions-examples.md) (§11 and §9–10) so code isn't
duplicated.

**Forbidden:** Bare `except:`, `except Exception:` without re‑raise or logging, `pass` in except without comment.

**Required:** Catch specific exceptions, `try/finally` or `with` for resources, `raise ... from original_exc`, log with context.

## Logging (No `print` in Production)

Use `logging` module. `logger = logging.getLogger(__name__)`. Use `logger.info()`, `.warning()`, `.error()`, `.debug()`.

Use `%`-style positional args in logging calls (`logger.info("User %s logged in", username)`) for lazy formatting. Do not use f‑strings in logging.

See [Conventions — Examples §9–10](../core/conventions-examples.md#9-lazy-logging) for the before/after.

---

## Examples

### Catch specific exceptions

The no-bare-except before/after is in
[Conventions — Examples §11](../core/conventions-examples.md#11-no-bare-except).

### Preserve cause with `raise ... from`

**Before** (original cause is lost in the traceback):

```python
try:
    config = json.loads(raw)
except json.JSONDecodeError:
    raise ConfigError("bad config")
```

**After** (chain the original exception):

```python
try:
    config = json.loads(raw)
except json.JSONDecodeError as e:
    raise ConfigError("bad config") from e
```

### Resource cleanup with `try/finally` → use `with`

**Before:**

```python
f = open(path)
try:
    data = f.read()
finally:
    f.close()
```

**After** (context manager — always closes, even on error):

```python
with open(path) as f:
    data = f.read()
```
