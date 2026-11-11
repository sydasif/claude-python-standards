# Code Review Checklist

## Section 1: Correctness & Contracts

- Logic changes preserve original behavior, or the deviation is intentional and documented.
- Edge cases handled: empty inputs, None/null, zero, out-of-range values.
- Error handling is specific - no bare `except:` / `catch (e) {}` blocks.
- Errors surface rather than being swallowed.
- No public function signatures changed without explicit user approval.
- No exported names renamed or removed.
- No config key or environment variable names changed.
- API response shapes preserved.

## Section 2: Hygiene & Documentation

- All tests pass at the same rate as the pre-change baseline.
- No tests deleted, weakened, or skipped to make the diff pass.
- New helpers or changed shared utilities have test coverage.
- Coverage matches baseline.
- No new unused imports.
- No debug `print` / `console.log` statements or commented-out code.
- No TODO/FIXME comments without a tracking reference.
- Inline comments reflect current behavior.
- Docstrings reflect updated public APIs.
- Cross-pass references (`cleanup-code` agent, `modernize-python` / `function-first-refactor` notes) are resolved or deferred.

## Section 3: Security & Risks

- No secrets, tokens, or credentials in the diff.
- No new shell injection vectors (unescaped user input in subprocess calls, etc.).
- No new file path traversal risks.
- Dependencies added or upgraded are from known, maintained sources.
