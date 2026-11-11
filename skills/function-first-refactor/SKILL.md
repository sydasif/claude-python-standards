---
name: function-first-refactor
description: Refactor or write Python by separating pure business logic from side effects ("functional core, imperative shell"), using plain functions and plain data. Use when the user asks to make code testable, decouple, simplify, or clean up Python; shares a function mixing DB/API/file/network/email/device I/O with validation, calculations, formatting, or decisions; complains that tests need heavy mocking; or is writing new Python that touches both logic and I/O, even without saying "pure functions". For codebases, it triages first and refactors only the highest-value functions. Syntax modernization (type hints, pathlib, f-strings) belongs to modernize-python.
---

# Function-First Refactor

**Core rule: pure functions are the logic; side effects are the shell. Keep them apart.** Pure logic is unit-testable with plain inputs and outputs, reusable (API, CLI, preview, export), and untouched when storage or transport changes.

> Run `cleanup-code` first, and `modernize-python` for syntax modernization, so this pass isn't mixed with style noise.

## What counts as pure

Depends only on its arguments (no globals, clock, randomness, env vars, hidden state); has no side effects (no file writes, printing, logging, network, DB, device access, or mutating inputs); same input gives same output.

## Three layers

| Layer | Role | Examples |
|---|---|---|
| Core logic | Pure, reusable, testable without mocks | validation, business rules, message/report building, calculations, transforming API or device output |
| Orchestration | Fetches inputs, calls core, decides when effects fire | handlers, CLI entry points, `process_*` functions |
| Side effects | The actual I/O | DB, HTTP, SMTP, files, SSH/device sessions |

Dependencies point inward: orchestration calls core and effects; core never calls effects.

## Ground rules

- **Functions first, classes only when necessary.** Use module-level functions and plain data (dicts, tuples, `TypedDict`, `@dataclass(frozen=True)` as records). A class is justified only for real state with invariants, a resource lifecycle (connection/session context manager), or a framework/interface requirement (Pydantic, ORM, ABC/`Protocol`, driver subclasses). Even then, keep the logic in pure functions that the methods delegate to.
- **Preserve behavior.** Outputs, error types, and the order of effects stay the same unless the user asks. Report anything noticed but not changed.
- **Pragmatism over purity.** Move the core ~80% of logic, not 100%. Leave small single-purpose functions alone. No tiny wrappers, no one-line predicates extracted for their own sake, no exotic functional idioms.
- **Don't change behavior without tests.** If the target has no tests, offer characterization tests first.

## Process

### 1. Triage (always, and mandatory for codebases)

For a directory or codebase, do not start editing. Run the finder:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/find_candidates.py" <path> --top 15
```

It ranks functions that mix branching with I/O or hidden impurity (clock, random, env). Effects propagate through same-module calls, so a local wrapper around `subprocess`/`requests`/a DB helper marks its callers as I/O; entry points (`main`, `cli`, anything called from an `if __name__` guard) are skipped because effects belong in the shell. Treat the output as a lead list, not a verdict: read the top candidates and discard false positives. Present the ranked shortlist, then refactor **at most 3-5 functions per round**, highest value first, and stop for review. For a single function or file, skip the finder and read the code directly.

### 2. Classify

Mark each line of the target as logic (decision/transformation) or effect (I/O).

### 3. Baseline

Run the project's tests before changing anything. Defaults for a `uv` project: `uv run pytest --tb=short`, plus `uv run mypy` and `uv run ruff check .` if configured.

### 4. Refactor

1. **Extract logic** into small single-purpose functions taking plain data in and returning plain data out. Return a description of what to do (an email dict, a list of commands) rather than doing it.
2. **Isolate effects** into thin functions that only do I/O, with no branching business rules.
3. **Write orchestration** that sequences fetch, decide, build, send/save.
4. **Name by intent.** Pure: `is_`, `build_`, `calculate_`, `format_`, `parse_`. Effects say what they touch: `send_`, `save_`, `fetch_`.
5. Hidden impurity (`datetime.now()`, `random`, `os.environ`, mutable defaults, mutating arguments, logging in logic) becomes parameters (e.g. `now`) or moves to the shell.
6. Error handling, retries, fallbacks, and logging live at the edges. Pure functions may raise on invalid input; the caller logs. Use `%`-style args in `logger.*` calls.

Where to look first: validation, eligibility rules, message/notification generation, report formatting, calculations, normalizing API or device responses.

**Before:**

```python
def send_welcome_email(user_id):
    user = db.get_user(user_id)
    if user and not user.has_signed_in:
        email = generate_email(user)
        smtp.send(email)
```

**After:**

```python
def build_welcome_email(user):            # pure
    return {
        "to": user.email,
        "subject": "Welcome!",
        "body": f"Hello {user.name}, thanks for joining us!",
    }

def send_email(email):                    # effect
    smtp.send(email)

def process_new_user(user_id):            # orchestration
    user = db.get_user(user_id)
    if user and not user.has_signed_in:
        send_email(build_welcome_email(user))
```

Longer example (order submission, invoice, PDF) with tests: `references/example.md`.

### 5. Tests

- Pure functions: plain input/output tests, no mocks.
- Orchestration: one or two tests with only the effects mocked; assert effects fire in order and nothing fires on invalid input.
- Never patch a pure function to force a branch; that means the layers are tangled. Feed it real data.

### 6. Verify

Re-run the baseline. Pass: tests same or better, no new type or lint errors, behavior identical.

## Output format

1. The refactored code, layered as above.
2. A short list of which functions are pure, effect, and orchestration.
3. Tests for the new pure functions.
4. Baseline vs. after.
5. Remaining candidates not yet done (codebase work), and risks or behavior noticed but left unchanged.

## See also

`cleanup-code` (run first) - `modernize-python` (syntax modernization, run before this pass) - `review-code` (final gate)

## Source

Based on "The One Refactor That Cleaned Up 80% of My Python Code" by mata (The Pythonworld, Aug 2025). The "80%" figure is the author's own claim; the principle is the established "functional core, imperative shell" pattern.
