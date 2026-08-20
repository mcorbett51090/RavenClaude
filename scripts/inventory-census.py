#!/usr/bin/env python3
"""inventory-census.py — the INDEPENDENT artifact census. Plan P4.4 (⛔ R8).

⛔ WHY THIS FILE EXISTS SEPARATELY FROM THE SWEEP.

A sweep that counts itself cannot detect its own blindness. If a concept file
fails validation and silently drops out of the registry, both the "registered"
and "executed" counts shrink together and the check stays green. That is the
`2>/dev/null` manufactured-clean shape, one layer up.

So the denominator comes from a source the sweep does not write and does not
derive from: **`git ls-files`** over the artifact roots. Not `concepts.json`.
Not `concepts.py` in-memory registry. Not a filesystem walk (which would also
count untracked scratch files and build output).

⛔ THE COUNTING RULE IS STATED, NOT INHERITED. claims-table row 5 said 48 hooks;
two independent in-session measures returned 47. That is a counting-rule
difference, not a defect — and the fix is to WRITE THE RULE DOWN so it cannot
drift again. Every rule below is explicit, and --explain prints them.

Usage:
    inventory-census.py                 # human report
    inventory-census.py --json          # machine envelope (the sweep reads this)
    inventory-census.py --explain       # print the counting rules verbatim
    inventory-census.py --check         # gate: the census must be non-empty and
                                        #        every declared root must resolve
    inventory-census.py --must-fail     # teeth
    inventory-census.py --must-fail-convention
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

PLUGIN = "plugins/ravenclaude-core"

# ── THE COUNTING RULES. Change one and you change the denominator of every
# ratchet in this initiative, so each carries its reason. ──────────────────
RULES = {
    "hook": (
        f"{PLUGIN}/hooks/*.sh at depth 1 ONLY. Excludes hooks/tests/** (a test is "
        "not a shipped hook) and excludes hooks.json (a manifest, not a hook). "
        "INCLUDES underscore-prefixed files such as _advise.sh: they are sourced "
        "helpers that ship, execute, and can break, so excluding them would hide "
        "exactly the class this initiative exists to surface. This inclusion is "
        "the 47-vs-48 discrepancy in claims-table row 5."
    ),
    "skill": (
        f"{PLUGIN}/skills/*/SKILL.md — one per skill directory. Reference files "
        "under a skill (references/*.md) are NOT separate artifacts; they are "
        "counted by the reference-resolution probe as targets, not as skills."
    ),
    "agent": f"{PLUGIN}/agents/*.md at depth 1.",
    "command": f"{PLUGIN}/commands/*.md at depth 1.",
    "plugin-script": (
        f"{PLUGIN}/scripts/* at depth 1, any extension. These SHIP to consumers."
    ),
    "root-script": (
        "scripts/* at depth 1, any extension. These are marketplace-dev tooling "
        "and do NOT ship, but they gate the build, so they are inventoried."
    ),
}

ROOTS = {
    "hook": (f"{PLUGIN}/hooks/", (".sh",), 1),
    "skill": (f"{PLUGIN}/skills/", ("SKILL.md",), 2),
    "agent": (f"{PLUGIN}/agents/", (".md",), 1),
    "command": (f"{PLUGIN}/commands/", (".md",), 1),
    "plugin-script": (f"{PLUGIN}/scripts/", ("*",), 1),
    "root-script": ("scripts/", ("*",), 1),
}


def _tracked(root: Path) -> list[str]:
    """Every git-tracked path. ⛔ Not a filesystem walk: an untracked scratch file
    is not an artifact, and counting it would make the denominator depend on
    whatever the last run happened to leave behind."""
    r = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"], capture_output=True, timeout=60
    )
    if r.returncode != 0:
        raise RuntimeError(
            "git ls-files failed — the census has NO independent source. "
            "This is UNKNOWN, never zero."
        )
    return [p for p in r.stdout.decode("utf-8", "replace").split("\0") if p]


def census(root: Path) -> dict:
    files = _tracked(root)
    out: dict[str, list[str]] = {k: [] for k in ROOTS}
    for path in files:
        for kind, (prefix, pats, depth) in ROOTS.items():
            if not path.startswith(prefix):
                continue
            rest = path[len(prefix) :]
            if rest.count("/") != depth - 1:
                continue
            name = rest.rsplit("/", 1)[-1]
            if pats == ("*",):
                out[kind].append(path)
            elif any(name == p or (p.startswith(".") and name.endswith(p)) for p in pats):
                out[kind].append(path)
            break
    for k in out:
        out[k].sort()
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=".")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--explain", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--must-fail", action="store_true")
    ap.add_argument("--must-fail-convention", action="store_true")
    args = ap.parse_args()

    if args.must_fail_convention:
        print("must-fail-teeth-exit: 1")
        return 0

    if args.explain:
        print("── Census counting rules (the denominator of every ratchet) ──")
        for kind, rule in RULES.items():
            print(f"\n  {kind}:")
            for line in rule.split(". "):
                if line.strip():
                    print(f"    {line.strip().rstrip('.')}.")
        return 0

    root = Path(args.root).resolve()

    if args.must_fail:
        # TEETH. The census must be derived from git, not from the filesystem.
        # Plant an UNTRACKED file in an artifact root and require the census NOT
        # to count it — a filesystem walk would, and a filesystem walk is exactly
        # the dependency this file exists to avoid.
        probe = root / PLUGIN / "hooks" / "_census-teeth-probe.sh"
        try:
            before = len(census(root)["hook"])
            probe.write_text("#!/usr/bin/env bash\n:\n", encoding="utf-8")
            after = len(census(root)["hook"])
        finally:
            if probe.exists():
                probe.unlink()
        if after != before:
            print(f"✗ must-fail: an UNTRACKED file changed the census ({before} -> {after}).")
            print("  The census is reading the filesystem, not git. The independence")
            print("  claim that the whole sweep-of-the-sweep rests on is false.")
            return 0
        print(f"✓ must-fail: an untracked artifact did not move the census (stayed {before}).")
        print("  The denominator really is git-derived. Exiting 1, the DECLARED teeth code.")
        return 1

    try:
        c = census(root)
    except RuntimeError as exc:
        print(f"census: {exc}")
        return 2

    total = sum(len(v) for v in c.values())

    if args.json:
        print(json.dumps({"total": total, "counts": {k: len(v) for k, v in c.items()},
                          "paths": c, "rules": RULES}, indent=2, sort_keys=True))
        return 0

    print("── Independent artifact census (source: git ls-files) ──")
    for kind in ROOTS:
        print(f"  {kind:<15} {len(c[kind]):>4}")
    print(f"  {'TOTAL':<15} {total:>4}")
    print()
    print("  ⛔ This is NOT derived from concepts.json, concepts.py, or anything")
    print("     the sweep writes. That independence is what lets a divergence")
    print("     between this number and the sweep enumeration mean something.")
    print("     Counting rules: inventory-census.py --explain")

    if args.check:
        if total == 0:
            print("  ✗ census is EMPTY — a broken census, not an empty repo.")
            return 1
        missing = [k for k, v in c.items() if not v]
        if missing:
            print(f"  ✗ declared root(s) resolved to nothing: {', '.join(missing)}")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
