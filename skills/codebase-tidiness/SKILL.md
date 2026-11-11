---
name: codebase-tidiness
description: >
  Scan Python codebases for obsolete code, stale comments, and outdated
  docstrings — the kind of cruft that accumulates during development but
  doesn't trigger linter errors. Run this before sprint reviews, after
  large refactors, or whenever the codebase needs a cleanup pass. If the
  user asks to "clean up", "tidy up", "find dead code", "check for stale
  comments", "review docstrings freshness", or mentions "code quality
  pass" or "spring cleaning", invoke this skill — don't assume they just
  mean formatting.
allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/scan_codebase.py *)
---

A codebase accumulates three kinds of invisible debt faster than most teams
realize: code that nothing calls anymore, comments that describe code that
no longer exists, and docstrings that were accurate once but drifted out of
sync. Linters catch style violations; they don't catch these.

This skill runs a **tiered scan**: mechanical checks first (tools that are
fast and precise), then a contextual pass (model judgment for issues no
tool can flag). The output is a single report with severity, file:line
references, and — where safe — suggested fixes.

---

## Depth control

Choose the scan scope upfront:

- **`quick` (default)** — Focused on the most actionable categories: dead code,
  stale fix-narratives, lying comments, zombie code, contextless TODOs.
  Tier 1 runs Vulture + Ruff F401/F841/ERA/FIX + docsig.
- **`deep`** — Full audit. Adds Ruff D (missing docstrings), docvet freshness
  (stale docs), and Coverage.py (untested code). Use when the user asks for a
  comprehensive sweep or before a major release.

Ask the user which depth they want if they don't specify. Default to `quick`
— deep produces too many findings to act on in one pass.

---

## How it works

### Tier 1 — Automated tooling (fast, deterministic)

**FIRST:** Run `scripts/scan_codebase.py` against the target directory. Do NOT
reach for ad-hoc ruff/vulture commands — the script handles all Tier 1 tools
in one call and outputs structured JSON. Only fall back to manual tool runs
if the script fails.

```
1. cd <project-root>
2. python3 "${CLAUDE_SKILL_DIR}/scripts/scan_codebase.py" <target> [--depth quick|deep]
3. Read the JSON output — findings are grouped by tool
4. Deduplicate overlapping findings (Vulture + Ruff F401 may flag the same import)
5. Proceed to Tier 2
```

Collect all findings from Tier 1 before proceeding to Tier 2 — the context
matters for dedup.

`${CLAUDE_SKILL_DIR}` is substituted by Claude Code with this skill's own
directory, so the command works for a global and a project install alike and no
path is hardcoded. The script shells out to `vulture`/`ruff`/`docsig` on `PATH` and reports any tool
that is missing as `{"error": true}` instead of failing the whole scan.

| What                                          | Tool / Approach                                                  | Depth | Why                                                              |
| --------------------------------------------- | ---------------------------------------------------------------- | ----- | ---------------------------------------------------------------- |
| Unused functions, classes, variables, imports | **Vulture** (`vulture <dir> --min-confidence 80`)                | quick | AST-based, fast, per-item confidence scores                      |
| Unused imports & dead variables               | **Ruff** (`ruff check --select F401,F841 <dir>`)                 | quick | Complements Vulture on the import/variable level                 |
| Commented-out code                            | **Ruff** (`ruff check --select ERA <dir>`)                       | quick | Catches `# def old_func():`, `# import x`, etc.                  |
| TODO/FIXME/HACK markers                       | **Ruff** (`ruff check --select FIX <dir>`)                       | quick | Collects all fixme markers for Tier 2 evaluation                 |
| Signature/docstring parameter mismatch        | **docsig** (`docsig --check-class --check-protected <dir>`)      | quick | Ensures `Args:` sections match actual function signatures        |
| Missing docstrings by style                   | **Ruff** (`ruff check --select D <dir>`)                         | deep  | Catches missing docs; does _not_ catch semantic staleness        |
| Stale docstrings (fast, changed files only)   | **docvet diff mode** (`docvet freshness --staged`)               | deep  | Detects code changes without docstring updates; runs on git diff |
| Stale docstrings (full blame sweep)           | **docvet drift mode** (`docvet freshness --all --mode drift`)    | deep  | Uses git blame to find docstrings that fell behind gradually     |
| Code unreachable by test coverage             | **Coverage.py** (if test suite is available)                     | deep  | Low-confidence but useful signal                                 |

**Key insight about docstring staleness tools:**

| Tool             | What it catches                                         | What it misses                                               |
| ---------------- | ------------------------------------------------------- | ------------------------------------------------------------ |
| **docsig**       | Parameter name/type drift, extra/missing params         | Changed logic/behavior without signature change              |
| **docvet diff**  | Docstrings not updated alongside code in recent commits | Docstrings that were already stale before the diff           |
| **docvet drift** | Gradual docstring rot across the full git history       | No false positives from squash merges or reformats           |
| **Ruff D**       | Missing docstrings entirely                             | Content correctness — it only checks _presence_ and _format_ |

These tools are **complementary**. docvet catches behavioral staleness (code
changed but docs didn't), and docsig catches structural staleness (signature
drifted from docs). Use both.

**Script flags:**

- `--depth quick` (default): Vulture, Ruff F401/F841/ERA/FIX, docsig
- `--depth deep`: everything above + Ruff D, docvet, coverage.py
- `--skip-*` flags override individual tools within any depth
- `--all` runs everything regardless of depth (same as `--depth deep`)

**Vulture tips:**

- `--min-confidence 80` avoids most false positives from dynamic dispatch
- Vulture tracks names, not call graphs — findings at 60-80% confidence are
  "suspect" rather than "dead"
- If the project uses `__init__.py` re-exports, Vulture may flag them —
  check against actual import usage

**Ruff ERA tip:**

- ERA can false-positive on comments that _look_ like code but aren't
  (examples, pseudo-code, config-like lines). Ruff has a
  `lint.task-tags` config setting that can exclude TODO/FIXME/HACK
  lines from ERA detection — recommend adding it to `pyproject.toml` if
  false positives are frequent.
- See `references/stale-patterns.md` for the "when to flag vs ignore" table.

#### Optional: pre-commit / CI integration

For teams that want to **prevent** stale docs rather than just find them,
recommend these additions to the repo's config:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.17.4
    hooks:
      - id: ruff
        args: [--select, F401, F841, ERA, FIX]
  - repo: https://github.com/jshwi/docsig
    rev: v0.97.0
    hooks:
      - id: docsig
        args: [--check-class, --check-protected, --check-overridden]
  # Optional — docvet's own hook runs the diff-mode checks on changed files:
  - repo: https://github.com/Alberto-Codes/docvet
    rev: v3.0.1
    hooks:
      - id: docvet
```

This catches the two most actionable categories before they ever hit the
repo: unused code (Ruff) and signature/docstring drift (docsig). docvet in
diff mode catches behavioral staleness on changed files.

---

### Tier 2 — Contextual analysis (model judgment)

These are the issues no linter catches. They require understanding what
the code does and what the docs say.

**Reference:** Read `references/stale-patterns.md` for before/after examples
of each pattern. It includes a severity table to help classify findings.

#### 0. Working-tree awareness (prerequisite)

Before scanning docstrings, check for uncommitted changes:

```bash
git diff HEAD --stat       # unstaged changes
git diff --cached --stat   # staged changes
```

For files with uncommitted changes: check **both** the committed version
(`git show HEAD:<file>`) and the working tree version for stale docs. A
function may have been cleaned up in the working tree while the committed
version still has the issue — report findings from committed code too.

For unchanged files: check only the working tree version.

**Why:** If a cleanup was already applied in uncommitted changes, the
findings still exist in the committed code for other developers. Flag them
but note "(already fixed in working tree)".

#### A–F. Patterns to check

Each pattern below is invisible to linters. Open the matching section of
`references/stale-patterns.md` only when you meet that pattern in the code.

| # | Pattern | How to check |
| --- | ------- | ------------ |
| A | Fix-narrative docstrings | Search for "Fix:", "original", "previously", "changed from", "blueprint" |
| B | Signature-docstring drift beyond docsig | Compare `Returns:`/`Raises:` against annotations and body |
| C | Comments that lie | Read the 3–5 lines after each non-obvious comment |
| D | Zombie code beyond ERA | Scan for commented-out functions and entire `if`/`for` blocks |
| E | TODO/FIXME/HACK | Triage against the "When to flag vs ignore" table |
| F | Unused Pydantic/dataclass models | Search imports outside the defining module |

---

## Output format

Present findings grouped by severity, then by file:

```markdown
## Codebase Tidiness Report — src/

### 🔴 High (certain issues, safe to act on)

| File         | Line | Issue                                                     | Suggestion                   |
| ------------ | ---- | --------------------------------------------------------- | ---------------------------- |
| src/utils.py | 38   | `epoch_ms_to_datetime()` defined but never called         | Remove function              |
| src/cache.py | 13   | Docstring calls this "Full-text search" but uses SQL LIKE | Change to "Substring search" |

### 🟡 Medium (likely issues, verify first)

| File          | Line | Issue                                           | Suggestion                        |
| ------------- | ---- | ----------------------------------------------- | --------------------------------- |
| src/cache.py  | 131  | Fix-narrative docstring ("original blueprint…") | Trim to present-tense             |
| src/models.py | 73   | Vulture: `SILENT_SKIP_TYPES` — 60% confidence   | Verify not dynamically referenced |

### 🟢 Info (minor / tracking items)

| File          | Line | Issue                                                    | Suggestion            |
| ------------- | ---- | -------------------------------------------------------- | --------------------- |
| src/server.py | 100  | `# TODO: handle pagination` — no context                 | Add details or remove |
| src/loader.py | 1    | docsig: `load_jsonl_file` has undocumented param `cache` | Add to docstring      |
```

If the user asked for **fixing** as well as finding, append a second section:

```markdown
### Applied Fixes

- `src/utils.py:38` — Removed `epoch_ms_to_datetime()` (dead code)
- `src/cache.py:131` — Trimmed docstring to present tense
- `src/server.py:100` — Removed contextless TODO
```

---

## Report structure

1. **Summary** — how many files scanned, total findings, breakdown by tier
2. **High severity** — dead code, signature-docstring drifts, mislabeled docs
3. **Medium severity** — likely-stale narratives, possible dead code, stale docstrings without signature changes
4. **Info** — TODOs without context, minor nits, formatting nits
5. **Applied fixes** (only if user asked for fixes)

---

## Compatibility

- **Python codebases only** (Tier 1 tools are Python-specific)
- **Git repository** required for docvet freshness checks and Tier 2B drift detection
- **ruff**, **vulture**, **docsig** should be installed (the skill will attempt
  `uv add --dev <tool>` if missing, but defaults to running only available tools)
- **docvet** (optional) — adds git-aware stale docstring detection at two
  depth levels (fast diff mode for CI, slow drift mode for periodic sweeps).
  It requires Python ≥3.12, so skip it on projects whose floor is 3.11. It
  takes `--all`, `--staged`, `--files` or individual `.py` files — never a
  directory.
- Existing Ruff configuration in `pyproject.toml` is respected — the skill
  appends `--select` flags rather than replacing config
