# Code Review Report Template

Always produce this structured report. Do not replace it with prose-only summaries.

```markdown
## Code Review Report

### Orientation

- Task type: [cleanup / refactor / feature / fix / other]
- Files changed: [count and list, or reference to git diff]
- Prior pass residual risks reviewed: [yes / no / none present]

### Checklist Results

- Correctness: [pass / issues found]
- Public contracts: [pass / issues found]
- Tests: [pass / issues found]
- Dead code and hygiene: [pass / issues found]
- Documentation: [pass / issues found]
- Security flags: [none / list any]

### Issues Found

(Repeat for each issue:)

- **File and line**: e.g., `src/auth.py:42`
- **Description**: What the problem is and why it matters.
- **Severity**: blocking / should fix / minor
- **Recommended action**: What to do about it.

### Residual Risks Not Resolved

Items flagged in prior passes that remain open. If none, write "None."

### Verdict

- Ready to submit - no blocking issues found
- Needs fixes - blocking issues listed above
- Needs discussion - questions requiring user input before proceeding
```

## Example - clean review

```markdown
## Code Review Report

### Orientation

- Task type: refactor
- Files changed: 4 (auth.py, utils.py, tests/test_auth.py, README.md)
- Prior pass residual risks reviewed: yes (2 items from modernize-python pass, both resolved)

### Checklist Results

- Correctness: pass
- Public contracts: pass - no signatures changed
- Tests: pass - coverage unchanged at 87%
- Dead code and hygiene: pass
- Documentation: pass
- Security flags: none

### Issues Found

None.

### Residual Risks Not Resolved

None.

### Verdict

Ready to submit - no blocking issues found.
```
