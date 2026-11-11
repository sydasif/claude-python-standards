# Python Standards

A Claude Code plugin carrying Python house rules and the code-quality workflow
that applies them: prune with `cleanup-code`, modernize with `modernize-python`,
separate logic from I/O with `function-first-refactor`, then gate on
`review-code`. Every skill is written to the Agent Skills open standard, so the
`SKILL.md` files also load in other skills-compatible agents.

## Components

| Type | Name | Purpose |
| --- | --- | --- |
| Skill | `python-standards` | House rules (3.11+ floor, ruff, mypy, pytest) with references for typing, docstrings, security, async, frameworks, uv, Docker |
| Skill | `cleanup-code` | KISS → YAGNI → DRY: dead code, duplication, over-abstraction |
| Skill | `modernize-python` | Mechanical modernization: type hints, dataclasses, `pathlib`, f-strings, `match` |
| Skill | `function-first-refactor` | Pure logic vs. I/O ("functional core, imperative shell") |
| Skill | `review-code` | Read-only final gate: correctness, contracts, security |
| Skill | `codebase-tidiness` | Tiered scan for dead code, stale comments, drifted docstrings |
| Agent | `cleanup-code`, `refactor-code`, `review-code` | Subagents that run the matching skill with restricted tools |
| Command | `/codebase-pipeline`, `/generate-readme`, `/suggest-tests` | Orchestrated workflows |

## Install

Register this repository as a marketplace, then install the plugin:

```
/plugin marketplace add sydasif/claude-python-standards
/plugin install python-standards@python-standards-market
```

From a local checkout, use the path instead: `/plugin marketplace add /path/to/this/repo`.

The plugin declares one `PostToolUse` hook. On Python files it runs `ruff format`
and `ruff check --fix`, preferring the project's pinned ruff through `uv run`
when the file sits in a uv project; on `.js`, `.ts`, `.json`, `.md`, `.html`,
`.yaml` and `.yml` it runs prettier. It exits silently when a tool is missing or
the payload is unusable, so it never blocks an edit.

The plugin ships ~770 tokens of always-on context (one description per skill);
skill bodies load only when invoked.

## Usage

In a Claude Code session, either invoke a skill by name (`/cleanup-code`) or
describe the task and let the description match. The `codebase-pipeline`
command is the entry point for the full sequence:

```
/codebase-pipeline
```

Skills load their bodies only when triggered; the always-loaded cost is one
description each.

## Setup

- Python 3.11+ for the bundled scan scripts.
- `ruff` on `PATH` for lint/format steps.
- Optional: `vulture`, `docsig`, `docvet` (Python ≥3.12) for the deeper
  `codebase-tidiness` tiers; missing tools are reported, never fatal.

## Development

```
uvx --from skills-ref agentskills validate skills/<name>
claude plugin validate . --strict
python3 -m pytest skills/codebase-tidiness/tests
```

`evals/` holds behaviour cases for `claude plugin eval`: each case is a
`prompt.md` plus graders, one of which asserts the intended skill fired. Runs
call the model and count against your usage plan, so they are opt-in.
`evals/results/` is generated and gitignored.

## License

MIT — see [LICENSE](LICENSE).
