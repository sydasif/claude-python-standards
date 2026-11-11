#!/usr/bin/env bash
# PostToolUse hook for Write|Edit: format and autofix the file just written.
#
# Python: ruff format + ruff check --fix, preferring the project's pinned ruff
# (`uv run ruff`) when the file sits in a uv project, else ruff on PATH.
# Web/markup: prettier via npx, matching the global format-code hook.
#
# Every failure path exits 0, so a missing tool or an unreadable payload never
# blocks an edit. `ruff check --fix` applies only the fixes ruff offers; unused
# imports (F401) are not autofixable in ruff 0.16 and are left in place.

set -uo pipefail

payload=$(cat)
[ -n "$payload" ] || exit 0

file=$(
  printf '%s' "$payload" |
    /usr/bin/env python3 -c 'import json,sys; print(json.load(sys.stdin).get("tool_input", {}).get("file_path", ""))' 2>/dev/null
) || exit 0
[ -n "$file" ] || exit 0
[ -f "$file" ] || exit 0

# Prefer the project's ruff when the file lives in a uv project.
ruff_cmd() {
  local dir
  dir=$(dirname "$file")
  while [ "$dir" != "/" ]; do
    if [ -f "$dir/pyproject.toml" ] || [ -f "$dir/uv.lock" ]; then
      if command -v uv >/dev/null 2>&1 && (cd "$dir" && uv run --quiet ruff --version >/dev/null 2>&1); then
        printf 'uv run --quiet ruff'
        return 0
      fi
      break
    fi
    dir=$(dirname "$dir")
  done
  command -v ruff >/dev/null 2>&1 || return 1
  printf 'ruff'
}

case "$file" in
  *.py)
    cmd=$(ruff_cmd) || exit 0
    # shellcheck disable=SC2086  # cmd is a deliberate two-word command
    $cmd format --quiet "$file" >/dev/null 2>&1 || true
    # shellcheck disable=SC2086
    $cmd check --fix --quiet "$file" >/dev/null 2>&1 || true
    ;;
  *.js | *.ts | *.json | *.md | *.html | *.yaml | *.yml)
    command -v npx >/dev/null 2>&1 || exit 0
    npx --yes prettier --write "$file" >/dev/null 2>&1 || true
    ;;
esac

exit 0
