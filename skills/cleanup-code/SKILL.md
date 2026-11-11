---
name: cleanup-code
description: Use when asked to review, simplify, refactor, or clean up a project for unnecessary code, duplicated logic, over-abstraction, excessive complexity, stale tests, or docs that no longer match implementation.
---

# Cleanup Principles

Apply YAGNI, DRY, and KISS in priority order when they conflict:

1. **KISS** - keep the code easiest to understand and change.
2. **YAGNI** - remove unsupported future-proofing.
3. **DRY** - reduce duplication only when it lowers real maintenance cost.

Treat these as engineering judgment, not slogans. Preserve public contracts unless the user explicitly wants breaking cleanup.

**Tie-breakers:** Prefer simple duplication over vague abstraction. Prefer deletion over generalization when code has no call sites. Use a shared helper for real policies (error shape, security, serialization). Preserve public APIs unless user accepts breaking changes.

> **YAGNI guardrail**: Remove speculative complexity, not the seams that make future change possible.

## Pre-Flight Gates

Run before any analysis or editing. Stop and confirm if any gate fails.

1. **Git cleanliness** - `git status`. If uncommitted changes exist, confirm scope before proceeding.
2. **Test coverage baseline** - If tests are absent or thin (<1 per exported function/class), escalate all findings to "needs care."
3. **Project overrides** - Read `CLAUDE.md`, `README.md`, contribution docs. Project guidance takes precedence over this skill.

## Workflow

1. **Inspect project shape** - Read repo guidance, map source/tests/docs, confirm git status, assess coverage, note overrides. For large repos (~20+ modules), confirm scope with user.
2. **Identify candidates** - Search call sites with `rg`, compare implementation against docs/tests, separate internal from public API removal. Use concrete file:line references.
3. **Rank findings** - Safe (unused imports, dead helpers, stale docs), Needs care (public tools, thin coverage), Usually skip (tiny duplication, domain abstractions, compat shims).
4. **Make narrow, batched changes** - One module per pass. Separate formatting from semantic changes into distinct commits.
5. **Verify behavior** - Run lint/tests after each batch. Add/update tests when touching shared helpers or public contracts.
6. **Update docs** - When files move, helpers change, coverage shifts, or public behavior changes.

For detailed pass criteria, read `references/passes.md`. For report templates, read `references/reporting.md`.

## Agentic Operation Notes

- Track progress in conversation, not in files (unless user requests `cleanup-progress.md`).
- Batch by module. Never weaken a failing test to make cleanup pass.
- If a change introduces a regression you can't fix, revert and report.

## See Also

- `modernize-python` skill - For modernizing Python code after cleanup
- `function-first-refactor` skill - For separating pure logic from side effects after modernization
