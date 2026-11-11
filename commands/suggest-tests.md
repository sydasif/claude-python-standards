---
description: Suggest comprehensive unit tests for main functions and classes
---

1. **Identify test targets** — List all exported functions, public methods, and classes from the entry points and main modules.
2. **Analyze signatures** — For each function, document parameters, return types, and expected preconditions/postconditions.
3. **Map control flow** — Identify branches, loops, guards, and early returns that need coverage.
4. **Enumerate edge cases** — For each function, list: empty input, boundary values, type mismatches, `None`/`null` states, and overflow conditions.
5. **Surface error paths** — Identify all `raise`, `throw`, `return Err`, and error-returning calls; ensure each has a test.
6. **Check existing tests** — Review any test directory or test files to avoid duplication and fill coverage gaps.
7. **Output test plan** — For each target, produce: test function name, input values, expected output, and the edge case or scenario it covers.
