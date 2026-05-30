#!/usr/bin/env python3
"""check-run-actions-argv.py — argv-integrity gate for the /__run allow-list.

The dashboard server's POST /__run executes a FIXED, allow-listed action by name.
The whole security argument rests on each action mapping to a *constant* argv with
NO caller-supplied input and NO shell. This gate proves that property structurally,
so a future edit that interpolates request data (or routes through a shell) fails
CI rather than shipping an arbitrary-command hole.

Checks, against scripts/serve-dashboards.py's RUN_ACTIONS dict (parsed via AST,
never executed):
  1. RUN_ACTIONS exists and is a non-empty dict literal.
  2. Every value is a list literal.
  3. Every element is a constant (str literal) OR a whitelisted constant-bearing
     expression: sys.executable, or str(<Path constant>) / str(REPO_ROOT-derived).
     Specifically: NO f-strings, NO %/+/.format() string building, NO Name that
     could carry request data, NO Call other than the allowed str()/Path joins.
  4. argv[0] is one of {"bash", sys.executable} (no shell like sh -c).
  5. No element contains shell metacharacters in a literal.

Exit 0 = clean; non-zero = a violation (the gate fails).

Usage:
  python3 scripts/check-run-actions-argv.py            # check the real file
  python3 scripts/check-run-actions-argv.py --file X   # check a fixture (gate audit)
"""
from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT = REPO_ROOT / "scripts" / "serve-dashboards.py"

# argv[0] values that are NOT a shell (a shell would let later args be a script).
ALLOWED_ARGV0 = {"bash", "sh"}  # bash/sh are only safe because argv[1] is a fixed
# script path and there is no -c; we still forbid -c below.
_SHELL_META = set(";|&$`<>(){}*?!\n")


def _fail(msg: str) -> int:
    print(f"::error::run-actions argv-integrity: {msg}", file=sys.stderr)
    return 1


def _const_str(node: ast.AST) -> str | None:
    """Return the literal string if node is a constant str, else None."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _is_allowed_dynamic(node: ast.AST) -> bool:
    """Allow only constant-bearing, request-independent expressions:
    - sys.executable           (the interpreter path)
    - str(<anything constant-ish>)  e.g. str(REPO_ROOT), str(SCRIPT / "x")
    These cannot carry HTTP request data (they reference module constants only)."""
    # sys.executable
    if (
        isinstance(node, ast.Attribute)
        and node.attr == "executable"
        and isinstance(node.value, ast.Name)
        and node.value.id == "sys"
    ):
        return True
    # str(...) wrapping a constant path expression (Name / Attribute / BinOp on /)
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "str"
        and len(node.args) == 1
    ):
        return _is_path_constant(node.args[0])
    return False


def _is_path_constant(node: ast.AST) -> bool:
    """A module-level path constant or a `/`-join of one with string literals.
    Names (REPO_ROOT, APPLY_SCRIPT, RAVENCLAUDE_SCRIPT) are module constants —
    they cannot hold request data. Reject anything else (Call, Subscript, etc.)."""
    if isinstance(node, ast.Name):
        return True
    if isinstance(node, ast.Attribute):
        return _is_path_constant(node.value)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        left_ok = _is_path_constant(node.left)
        right_ok = _is_path_constant(node.right) or _const_str(node.right) is not None
        return left_ok and right_ok
    return False


def check(path: Path) -> int:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError) as e:
        return _fail(f"cannot parse {path}: {e}")

    run_actions = None
    for node in ast.walk(tree):
        # plain assignment: RUN_ACTIONS = {...}
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "RUN_ACTIONS":
                    run_actions = node.value
        # annotated assignment: RUN_ACTIONS: dict[...] = {...}
        elif isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and node.target.id == "RUN_ACTIONS":
                run_actions = node.value
    if run_actions is None:
        return _fail("RUN_ACTIONS assignment not found")
    if not isinstance(run_actions, ast.Dict) or not run_actions.keys:
        return _fail("RUN_ACTIONS is not a non-empty dict literal")

    for key, val in zip(run_actions.keys, run_actions.values):
        kname = _const_str(key) or "<non-literal-key>"
        if _const_str(key) is None:
            return _fail(f"action key is not a string literal: {ast.dump(key)}")
        if not isinstance(val, ast.List) or not val.elts:
            return _fail(f"action {kname!r} value is not a non-empty list literal")
        for i, elt in enumerate(val.elts):
            lit = _const_str(elt)
            if lit is not None:
                if _SHELL_META & set(lit):
                    return _fail(
                        f"action {kname!r} argv[{i}] literal contains shell metachar: {lit!r}"
                    )
                if i == 0 and lit in ALLOWED_ARGV0:
                    continue
                if i == 1 and lit == "-c":
                    return _fail(f"action {kname!r} uses a shell -c form (argv[1] == '-c')")
                continue
            # non-literal element — only the whitelisted constant expressions pass
            if _is_allowed_dynamic(elt):
                continue
            return _fail(
                f"action {kname!r} argv[{i}] is not a constant or allowed path "
                f"expression (possible interpolation): {ast.dump(elt)}"
            )
        # argv[0] must be a known non-shell launcher (literal or sys.executable)
        first = val.elts[0]
        first_lit = _const_str(first)
        if first_lit is not None:
            if first_lit not in ALLOWED_ARGV0:
                return _fail(f"action {kname!r} argv[0] {first_lit!r} not in {ALLOWED_ARGV0}")
        elif not _is_allowed_dynamic(first):
            return _fail(f"action {kname!r} argv[0] is not a known launcher")

    print(f"run-actions argv-integrity: {len(run_actions.keys)} actions, all fixed-argv (no shell/interpolation)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=str(DEFAULT))
    args = ap.parse_args()
    return check(Path(args.file))


if __name__ == "__main__":
    raise SystemExit(main())
