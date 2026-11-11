#!/usr/bin/env python3
"""Rank Python functions that mix decisions with I/O or hidden impurity.

Heuristic lead list for function-first-refactor triage: read the top hits,
discard false positives.

Effects propagate through local calls: a wrapper defined in the same module,
such as ``_run_cmd`` around ``subprocess.run``, marks its callers as I/O.
Entry points (``main``, ``cli``, anything called from an ``if __name__`` guard)
are skipped - effects belong in the imperative shell, so ranking them is noise.

Usage:
    python3 find_candidates.py <path> [--top N] [--min-score S]
"""

import argparse
import ast
import sys
from collections.abc import Iterator
from pathlib import Path

IO_BUILTINS = {"open", "print", "input"}
IO_PREFIXES = (
    "requests.",
    "httpx.",
    "urllib.",
    "smtplib.",
    "subprocess.",
    "shutil.",
    "socket.",
    "paramiko.",
    "netmiko.",
    "napalm.",
    "os.system",
    "os.remove",
    "os.makedirs",
    "db.",
    "cursor.",
    "conn.",
    "session.",
    "smtp.",
    "client.",
)
IO_METHODS = {
    "send",
    "sendall",
    "sendmail",
    "send_command",
    "send_config_set",
    "commit",
    "execute",
    "executemany",
    "write_text",
    "read_text",
    "write_bytes",
    "read_bytes",
    "post",
    "put",
    "patch",
    "urlopen",
    "connect",
    "recv",
}
IMPURE = {
    "datetime.now",
    "datetime.datetime.now",
    "datetime.utcnow",
    "datetime.datetime.utcnow",
    "date.today",
    "time.time",
    "random.random",
    "random.choice",
    "random.randint",
    "uuid.uuid4",
    "os.getenv",
    "os.environ.get",
}
ENTRY_POINT_NAMES = {"main", "cli", "entrypoint"}
BRANCHES = (ast.If, ast.For, ast.While, ast.Match, ast.IfExp, ast.BoolOp)

EffectKinds = set[str]


def dotted(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = dotted(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    return ""


def static_kind(name: str) -> str:
    """Effect kind for a call known by name alone, empty when unknown."""
    if name in IMPURE:
        return "impure"
    if (
        name in IO_BUILTINS
        or name.startswith(IO_PREFIXES)
        or name.rsplit(".", 1)[-1] in IO_METHODS
    ):
        return "io"
    if name.startswith(("logger.", "logging.", "log.")):
        return "log"
    return ""


def function_defs(
    tree: ast.Module,
) -> dict[str, ast.FunctionDef | ast.AsyncFunctionDef]:
    return {
        node.name: node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def local_effects(tree: ast.Module) -> dict[str, EffectKinds]:
    """Effect kinds per module-level function, inherited through local calls."""
    funcs = function_defs(tree)
    effects: dict[str, EffectKinds] = {name: set() for name in funcs}

    changed = True
    while changed:  # fixpoint: sets only grow, so this terminates
        changed = False
        for name, func in funcs.items():
            kinds: EffectKinds = set()
            for node in ast.walk(func):
                if isinstance(node, ast.Call):
                    callee = dotted(node.func)
                    kind = static_kind(callee)
                    if kind:
                        kinds.add(kind)
                    else:
                        kinds |= effects.get(callee, set())
                elif isinstance(node, ast.Attribute) and dotted(node) == "os.environ":
                    kinds.add("impure")
            if not kinds <= effects[name]:
                effects[name] |= kinds
                changed = True
    return effects


def is_main_guard(test: ast.AST) -> bool:
    return (
        isinstance(test, ast.Compare)
        and isinstance(test.left, ast.Name)
        and test.left.id == "__name__"
    )


def entry_points(tree: ast.Module) -> set[str]:
    """The imperative shell: main/cli, plus anything run from a __main__ guard."""
    names = set(ENTRY_POINT_NAMES)
    for node in ast.walk(tree):
        if isinstance(node, ast.If) and is_main_guard(node.test):
            for inner in ast.walk(node):
                if isinstance(inner, ast.Call):
                    names.add(dotted(inner.func))
    return names


def analyze(
    func: ast.FunctionDef | ast.AsyncFunctionDef, effects: dict[str, EffectKinds]
) -> dict[str, int | bool]:
    io = impure = log = branches = 0
    for node in ast.walk(func):
        if isinstance(node, ast.Call):
            callee = dotted(node.func)
            kind = static_kind(callee)
            kinds = {kind} if kind else effects.get(callee, set())
            io += "io" in kinds
            impure += "impure" in kinds
            log += "log" in kinds
        elif isinstance(node, BRANCHES):
            branches += 1
        elif isinstance(node, ast.Attribute) and dotted(node) == "os.environ":
            impure += 1
    mutable_default = any(
        isinstance(d, (ast.List, ast.Dict, ast.Set))
        for d in func.args.defaults + [d for d in func.args.kw_defaults if d]
    )
    length = (func.end_lineno or func.lineno) - func.lineno + 1
    score = 0
    if branches and (io or impure):
        score = io * 3 + impure * 2 + branches + log + (2 if mutable_default else 0)
        score += min(length // 10, 5)
    return {
        "io": io,
        "impure": impure,
        "log": log,
        "branches": branches,
        "length": length,
        "score": score,
        "mutable_default": mutable_default,
    }


def scan(
    path: Path,
) -> Iterator[
    tuple[Path, ast.FunctionDef | ast.AsyncFunctionDef, dict[str, int | bool]]
]:
    files = [path] if path.is_file() else sorted(path.rglob("*.py"))
    for f in files:
        if any(
            p in f.parts
            for p in (".venv", "venv", "node_modules", ".git", "__pycache__")
        ):
            continue
        try:
            tree = ast.parse(f.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError) as exc:
            print(f"skip {f}: {exc}", file=sys.stderr)
            continue
        effects = local_effects(tree)
        shell = entry_points(tree)
        for node in ast.walk(tree):
            if (
                isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and node.name not in shell
            ):
                yield f, node, analyze(node, effects)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("path", type=Path)
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument("--min-score", type=int, default=1)
    args = ap.parse_args()

    rows = [r for r in scan(args.path) if r[2]["score"] >= args.min_score]
    rows.sort(key=lambda r: r[2]["score"], reverse=True)
    if not rows:
        print("No mixed logic/I-O candidates found.")
        return
    print(
        f"{'score':>5}  {'io':>2} {'imp':>3} {'log':>3} {'br':>3} {'lines':>5}  location"
    )
    for f, node, m in rows[: args.top]:
        flag = " mutable-default" if m["mutable_default"] else ""
        print(
            f"{m['score']:>5}  {m['io']:>2} {m['impure']:>3} {m['log']:>3} "
            f"{m['branches']:>3} {m['length']:>5}  {f}:{node.lineno} {node.name}(){flag}"
        )
    print(f"\n{len(rows)} candidate(s); showing top {min(args.top, len(rows))}.")


if __name__ == "__main__":
    main()
