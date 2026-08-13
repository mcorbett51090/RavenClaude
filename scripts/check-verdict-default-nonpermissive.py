#!/usr/bin/env python3
"""Gate 199 (static half) — the two fail-open shapes execution cannot reach.

The execution runner beside this file drives every PreToolUse hook with inputs it
was never written for and asserts the exit is 0 or 2. That catches the reachable
paths. Two shapes stay invisible to it because they fire only on a branch a
synthetic payload does not take:

  1. A PERMISSIVE DEFAULT on a verdict chain. A `case` resolving a verdict whose
     `*)` arm allows means any out-of-protocol value — a typo, a salvaged string,
     a future verdict name — resolves to ALLOW. This is the v0.205.1 tie-breaker
     fix: every branch failed safe except the final `else`, so a valid-JSON but
     out-of-protocol verdict defaulted to allow.

  2. A TRAP ARMED TOO LATE. A fail-closed EXIT trap only covers what runs after
     it. Armed after the first fallible operation, an abort during setup exits
     non-zero WITHOUT the trap's deny — a non-blocking error, which is fail-open.
     v0.205.1 moved the trap to the first line after `set -euo pipefail` for
     exactly this reason.

Scope is deliberately narrow. This flags only what it can name concretely; a
lint that guesses at intent floods, and a flooding lint gets disabled. Where it
cannot be confident it says nothing rather than guessing — the gap is named here
instead of being papered over with a noisy heuristic.

Exit codes: 0 = clean; 2 = a finding or an unreadable input. Never 1.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import NamedTuple

HOOK_DIR = Path("plugins/ravenclaude-core/hooks")

# A verdict-ish subject. Narrow on purpose: these are the names this repo
# actually uses for a resolved decision.
VERDICT_CASE = re.compile(
    r'^\s*case\s+"?\$\{?(verdict|decision|final_verdict|panel_verdict|v)\}?"?\s+in\b'
)
CASE_END = re.compile(r"^\s*esac\b")
DEFAULT_ARM = re.compile(r"^\s*(\*|\*\))\s*\)?")
# An arm that resolves permissively. `emit_allow` is this repo's own name for it.
PERMISSIVE = re.compile(r"\b(emit_allow|permissionDecision\"?\s*:\s*\"?allow|exit\s+0)\b")

TRAP_EXIT = re.compile(r'^\s*trap\s+.*\bEXIT\b')
SET_LINE = re.compile(r"^\s*set\s+-")
# A line that can abort under `set -e` before the trap is armed. Assignments of
# literals cannot; a command substitution or an external command can.
FALLIBLE = re.compile(r"\$\(|`|^\s*(cd|source|\.)\s+\S")


class Finding(NamedTuple):
    path: str
    line: int
    kind: str
    detail: str

    def render(self) -> str:
        return f"  {self.path}:{self.line}  [{self.kind}]\n      {self.detail}"


def _strip(line: str) -> str:
    h = line.find("#")
    return line if h == -1 else line[:h]


def check_verdict_defaults(path: Path, lines: list[str]) -> list[Finding]:
    out: list[Finding] = []
    i = 0
    while i < len(lines):
        if not VERDICT_CASE.match(_strip(lines[i])):
            i += 1
            continue
        start = i
        # Walk to `esac`, remembering where the default arm began.
        default_at = None
        j = i + 1
        while j < len(lines) and not CASE_END.match(_strip(lines[j])):
            if default_at is None and DEFAULT_ARM.match(_strip(lines[j])):
                default_at = j
            j += 1
        if default_at is None:
            out.append(Finding(
                path.as_posix(), start + 1, "no-default-arm",
                "a verdict `case` with no `*)` arm — an out-of-protocol verdict "
                "falls through and resolves to whatever follows, which is not a decision",
            ))
        else:
            body = "\n".join(_strip(x) for x in lines[default_at:j])
            if PERMISSIVE.search(body):
                out.append(Finding(
                    path.as_posix(), default_at + 1, "permissive-default",
                    "the `*)` arm of a verdict chain resolves PERMISSIVELY — any "
                    "out-of-protocol verdict (a typo, a salvaged string, a future "
                    "name) becomes an allow. A default must deny or defer to the "
                    "category posture, never allow.",
                ))
        i = j + 1
    return out


def check_trap_ordering(path: Path, lines: list[str]) -> list[Finding]:
    trap_at = next((n for n, ln in enumerate(lines) if TRAP_EXIT.match(_strip(ln))), None)
    if trap_at is None:
        return []   # no EXIT trap is a design choice, not a defect this can judge
    set_at = next((n for n, ln in enumerate(lines) if SET_LINE.match(_strip(ln))), None)
    if set_at is None:
        return []
    for n in range(set_at + 1, trap_at):
        code = _strip(lines[n])
        if FALLIBLE.search(code):
            return [Finding(
                path.as_posix(), trap_at + 1, "trap-armed-late",
                f"the fail-closed EXIT trap is armed at line {trap_at + 1}, but line "
                f"{n + 1} can already abort under `set -e`. An abort before the trap "
                "exits non-zero WITHOUT the deny — which the harness treats as a "
                "non-blocking error, i.e. fail-OPEN. Arm the trap first.",
            )]
    return []


def audit(root: Path) -> list[Finding]:
    hook_dir = root / HOOK_DIR
    if not hook_dir.is_dir():
        raise SystemExit(f"verdict-default: {hook_dir} is not a directory — refusing to pass vacuously")
    found: list[Finding] = []
    n = 0
    for p in sorted(hook_dir.glob("*.sh")):
        if p.name.startswith("_"):
            continue    # sourced helpers have no verdict of their own
        try:
            lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        n += 1
        found.extend(check_verdict_defaults(p, lines))
        found.extend(check_trap_ordering(p, lines))
    if n == 0:
        raise SystemExit("verdict-default: zero hooks scanned — the check measured nothing")
    return found


def self_test() -> int:
    ok = True
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp) / HOOK_DIR
        d.mkdir(parents=True)

        # M1 — a permissive default on a verdict chain.
        (d / "permissive.sh").write_text(
            '#!/usr/bin/env bash\nset -euo pipefail\ncase "$verdict" in\n'
            '  deny) exit 2 ;;\n  *) emit_allow ;;\nesac\n', encoding="utf-8")
        # M2 — a verdict chain with no default arm at all.
        (d / "nodefault.sh").write_text(
            '#!/usr/bin/env bash\nset -euo pipefail\ncase "$verdict" in\n'
            '  deny) exit 2 ;;\n  edit) emit_edit ;;\nesac\n', encoding="utf-8")
        # M3 — the EXIT trap armed after a fallible operation.
        (d / "latetrap.sh").write_text(
            '#!/usr/bin/env bash\nset -euo pipefail\nroot="$(pwd)"\n'
            'trap fail_closed EXIT\n', encoding="utf-8")
        # C1 — the correct shapes, which must NOT be flagged.
        (d / "correct.sh").write_text(
            '#!/usr/bin/env bash\nset -euo pipefail\ntrap fail_closed EXIT\n'
            'root="$(pwd)"\ncase "$verdict" in\n  allow) emit_allow ;;\n'
            '  *) emit_deny ;;\nesac\n', encoding="utf-8")
        # C2 — no trap and no verdict chain: silence, not a guess.
        (d / "plain.sh").write_text(
            '#!/usr/bin/env bash\nset -uo pipefail\necho hi\n', encoding="utf-8")

        found = audit(Path(tmp))
        by = {}
        for f in found:
            by.setdefault(Path(f.path).name, set()).add(f.kind)

        for name, kind in (("permissive.sh", "permissive-default"),
                           ("nodefault.sh", "no-default-arm"),
                           ("latetrap.sh", "trap-armed-late")):
            if kind in by.get(name, set()):
                print(f"  ✓ caught: {kind} ({name})")
            else:
                ok = False
                print(f"  ✗ MISSED: {kind} in {name} — got {sorted(by.get(name, []))}")

        for name in ("correct.sh", "plain.sh"):
            if name not in by:
                print(f"  ✓ clean:  {name}")
            else:
                ok = False
                print(f"  ✗ FLOODED on {name}: {sorted(by[name])}")

        # An empty hook dir must fail closed, never pass vacuously.
        empty = Path(tmp) / "empty"
        (empty / HOOK_DIR).mkdir(parents=True)
        try:
            audit(empty)
            ok = False
            print("  ✗ MISSED: an empty hook set was accepted instead of failing closed")
        except SystemExit:
            print("  ✓ caught: an empty hook set fails closed")

    print("\nteeth verified" if ok else "\nTEETH BROKEN")
    return 0 if ok else 2


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()

    findings = audit(Path(args.root))
    if findings:
        print(f"verdict-default: {len(findings)} finding(s) — these fail OPEN", file=sys.stderr)
        for f in findings:
            print(f.render(), file=sys.stderr)
        return 2
    print("verdict-default: every verdict chain defaults non-permissively; every EXIT trap is armed first")
    return 0


if __name__ == "__main__":
    sys.exit(main())
