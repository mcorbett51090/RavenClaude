#!/usr/bin/env python3
"""check-covers-completeness.py — P3 §5.5. An honest PARTIAL check.

⛔ WHAT THIS CATCHES, AND WHAT IT PROVABLY CANNOT.

A `covers_digest` is only as complete as the author-declared `covers[]`. An
under-scoped list yields an entry whose drift tripwire silently never fires —
the entry looks gated, the gate is green, and the mechanism it describes can
change underneath it forever.

CATCHES: under-declaration that is TEXTUALLY VISIBLE. Every repo-relative path
mentioned in the entry `nuance` or `nuance_source` must also appear in `covers[]`
(or be exempted). If the prose names a file the digest does not watch, that is a
declared dependency with no tripwire, and it is mechanically findable.

CANNOT CATCH: a nuance that depends on HOST behaviour never named as a path — the
delivered-channel fact depends on which channel the host reads, and no path in
this repo expresses that. A complete check would require inferring which facts a
prose paragraph depends on, which is the same unsolved problem as verifying the
nuance is true. That residual is WAIVED, deliberately, in plan §21-W3, with its
TELL recorded: an entry whose nuance is later found false while its digest never
tripped. Three occurrences should reopen the design.

The right exemption for a host-dependent claim is to model it as its own
`kind: platform-fact` concept under the 90-day calendar gate, not to widen
covers[] with a path that does not exist.

⛔ THE TEETH-BIT EXIT IS 1. Declared, never assumed.

Usage:
    check-covers-completeness.py [--root DIR]
    check-covers-completeness.py --check            # gate (exit 1 on violation)
    check-covers-completeness.py --must-fail        # teeth
    check-covers-completeness.py --must-fail-convention
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from concepts import ENTRY_CLASS_INVENTORY, ConceptError, load_concepts  # noqa: E402

# A repo-relative path mention: at least one directory segment and a file
# extension, so ordinary prose ("the hooks directory") does not register.
_PATH_RE = re.compile(
    r"(?<![\w./-])((?:[A-Za-z0-9_.-]+/){1,8}[A-Za-z0-9_.-]+\.[A-Za-z0-9]{1,6})(?![\w/-])"
)

# Fields whose prose is scanned. nuance_source is a POINTER (file:line-range), so
# its path half is stripped of the line suffix before comparison.
SCANNED = ("nuance", "nuance_source")


def _mentioned_paths(c: dict) -> set[str]:
    found: set[str] = set()
    for field in SCANNED:
        val = c.get(field)
        if not val:
            continue
        text = val if isinstance(val, str) else str(val)
        for m in _PATH_RE.finditer(text):
            found.add(m.group(1).split(":")[0])
    return found


def violations(root: Path, concepts: list[dict]) -> list[str]:
    out: list[str] = []
    for c in concepts:
        if c.get("entry_class") != ENTRY_CLASS_INVENTORY:
            continue
        covers = set(c.get("covers") or [])
        exempt = set(c.get("covers_exempt") or [])
        for mention in sorted(_mentioned_paths(c) - covers - exempt):
            # Only a path that actually EXISTS is a dependency. A prose mention of
            # something absent is a typo or an example, and flagging it would make
            # the check noisy enough to get turned off.
            if not (root / mention).exists():
                continue
            out.append(
                f"  ✗ {c['id']}: nuance names '{mention}' but covers[] does not watch it "
                "— the drift tripwire would never fire for that dependency.\n"
                f"      add it to covers[], or record why it is exempt in covers_exempt[]."
            )
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=".")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--must-fail", action="store_true")
    ap.add_argument("--must-fail-convention", action="store_true")
    args = ap.parse_args()

    if args.must_fail_convention:
        print("must-fail-teeth-exit: 1")
        return 0

    root = Path(args.root).resolve()

    if args.must_fail:
        # TEETH on a synthetic entry, because the real corpus has no inventory
        # entries yet. A detector reporting 0 findings on an EMPTY population and
        # never proven to fire is indistinguishable from one that never ran.
        planted = [
            {
                "id": "planted",
                "entry_class": ENTRY_CLASS_INVENTORY,
                "covers": ["scripts/concepts.py"],
                "nuance": "The delivery decision is made in scripts/audit-gates.sh, not here.",
                "nuance_source": "scripts/audit-gates.sh:1-2",
            }
        ]
        # ⛔ THE EXIT DIRECTION IS INVERTED ON PURPOSE, AND IT IS THE CONTRACT.
        # --must-fail runs the planted canary and EXITS WITH THE DECLARED TEETH
        # CODE when the detector bites. audit-gates rc_mustfail reads the
        # declaration first and COMPARES, so a tool that bites but returns the
        # wrong code, or returns the right code without biting, both fail. A
        # "0 means success" reading here would make the comparison vacuous.
        found = violations(root, planted)
        if not found:
            print("✗ must-fail: the detector did not bite on a planted under-declaration.")
            print("  A clean report on the real corpus is therefore not evidence.")
            return 0
        # Control: adding the path to covers[] must CLEAR it, or the detector is
        # simply reporting every mention and covers[] means nothing.
        planted[0]["covers"].append("scripts/audit-gates.sh")
        if violations(root, planted):
            print("✗ must-fail: the finding survived adding the path to covers[] —")
            print("  the detector is not actually reading covers[].")
            return 0
        print("✓ must-fail: detector bites on under-declaration and clears when covered.")
        print("  exiting 1, the DECLARED teeth code, so the auditor can compare.")
        return 1

    try:
        concepts = load_concepts(root)
    except ConceptError as exc:
        print(f"covers-completeness: concepts do not parse — {exc}")
        return 2

    inventory = [c for c in concepts if c.get("entry_class") == ENTRY_CLASS_INVENTORY]
    found = violations(root, concepts)

    print("── covers[] completeness (textual, partial by construction) ──")
    print(f"  inventory entries scanned : {len(inventory)} of {len(concepts)} concept(s)")
    if not inventory:
        # ⛔ An empty population is reported as EMPTY, never as clean. "Nothing was
        # under-declared" and "there was nothing to check" are different facts, and
        # conflating them is the manufactured-clean shape.
        print("  ⚠ no entry_class: inventory entries exist yet — this is an EMPTY")
        print("    population, not a clean one. Run --must-fail to see the teeth bite.")
        return 0
    if found:
        print(f"  ⛔ {len(found)} under-declared dependenc(ies):")
        for f in found:
            print(f)
        return 1 if args.check else 0
    print("  ✓ every path named in a nuance is watched by its covers[].")
    print("  ⛔ Limit: this is TEXTUAL. A nuance depending on host behaviour never")
    print("    named as a path is invisible here — waived in plan §21-W3.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
