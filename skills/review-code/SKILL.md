---
name: review-code
description: Use when the user asks to "review my code", "check my changes", or after a cleanup, refactor, feature, or fix. Final gate before submitting.
---

# Code Review - Final Gate

> Surface problems only. Do **not** modify code. Report issues clearly and stop.

## Review Process

### 1. Orient to the Work

- What task was completed? (cleanup, refactor, feature, fix)
- Which files changed? Run `git diff --name-only HEAD` or ask for the diff.
- Review residual risk notes from prior `cleanup-code` or `modernize-python` passes.
- Flag changes outside stated scope.

### 2. Structural Verification

- All expected files/directories present.
- No accidental deletions or placeholder content.
- No unintended new files outside scope.
- Import paths and cross-references still resolve.

### 3. Code Review

For each item in the checklist, record pass/issue found. Read `references/checklist.md` for the full checklist (correctness, hygiene, security).

### 4. Fresh-Perspective Questions

Answer based on evidence: Does this solve the problem completely? Is anything surprising in the diff? Could a new team member follow this? Did the change stay within scope? Are there unresolved residual risks?

## Output

Always produce a structured report. Read `references/output-format.md` for the template.

## Notes

- This skill does not modify code.
- Stop and surface blocking issues immediately.
- Flag scope drift explicitly.
- Report all security flags regardless of severity.
- If git is unavailable and no diff provided, ask for it.
