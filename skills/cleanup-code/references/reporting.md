# Cleanup Report Templates

## Exploration or review mode

Report findings before making any changes, unless the user asked to implement directly.

```
## Findings

### Pre-flight
- Git status: [clean / uncommitted changes - describe]
- Test coverage: [adequate / thin / unknown - describe risk]
- Project overrides from CLAUDE.md or README.md: [none / list any]

### Candidates (ordered by risk or payoff)
- [file:line] Description - category (safe / needs care / skip)
- ...

### Safe cleanup
Changes that can be made without public contract risk.

### Risky cleanup
Changes that need user confirmation before proceeding.

### Skipped candidates
Items evaluated but not actioned, with the reason for each.

### Verification plan
Lint and test commands to run. Doc sections to update.
```

## Implementation mode

Finish with:

```
## What changed
[summary of edits, scoped to module or layer]

## What was verified
[lint/test output or reason verification was skipped]

## Residual risks
[skipped candidates, thin coverage areas, public API concerns]
```
