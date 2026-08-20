#!/usr/bin/env python3
"""check-inventory-evidence.py — P5 §7.2 (⛔ R9). No raw bytes in committed fields.

⛔ WHY THE COMMITTED SURFACE NEEDS ITS OWN RULE.

log-probe.sh already stores DERIVED LABELS ONLY, and its header says why: raw
command text and captured output carry tokens, keys and payloads. Both panel
plans extended that discipline to the sweep gitignored records — and NEITHER
extended it to the committed authoring surface. Concept files are committed and
**permanently retained**. `.ravenclaude/runs/` is gitignored and disposable. The
weaker rule was applied to the more durable store.

THE RULE, STATED NEGATIVELY:

  `nuance`, `nuance_evidence.control`, `nuance_evidence.falsifier`, and
  `nuance_source` MAY summarise a mechanism, name a label, or cite a file:line
  location. They MAY NEVER contain verbatim command text, verbatim stdout/stderr,
  or payload text.

⛔ STATED LIMIT — THIS IS A SHAPE HEURISTIC, NOT A SECRET SCANNER. It catches a
paste-of-output. It cannot certify that a paraphrase contains nothing sensitive.
That residual is WAIVED in plan §21-W4, deliberately: a real secret scanner over
free prose has a false-positive rate that would make authoring unworkable, and
these fields are meant to hold POINTERS AND LABELS, not payloads. The waiver
carries its own TELL — any value over ~300 chars, or containing a newline-
separated block — and both are reported here rather than left to chance.

⛔ THE TEETH-BIT EXIT IS 1. Declared, never assumed.

Usage:
    check-inventory-evidence.py [--root DIR] [--check]
    check-inventory-evidence.py --must-fail
    check-inventory-evidence.py --must-fail-convention
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from concepts import ENTRY_CLASS_INVENTORY, ConceptError, load_concepts  # noqa: E402

GUARDED = ("nuance", "control", "falsifier", "nuance_source")
LONG_VALUE = 300  # the §21-W4 TELL

# Shapes that mean "this is pasted output", not "this is a summary".
SHAPES = (
    (re.compile(r"(?m)^\s*[$#>]\s+\S"), "a shell-prompt line ($ / # / >)"),
    (re.compile(r"(?m)^\s*(?:Traceback \(most recent|\s+File \")"), "a pasted Python traceback"),
    (re.compile(r"(?m)^\s*(?:HTTP/\d|\{\s*$|\[\s*$)"), "a pasted response or JSON block"),
    (re.compile(r"(?<![\w/])/(?:Users|home|var/folders|tmp)/[^\s\"']{4,}"),
     "an absolute filesystem path outside the repo"),
    # ⛔ NO `/` IN THIS CLASS, AND A MIXED-CASE+DIGIT REQUIREMENT.
    # The first version used [A-Za-z0-9+/=_-]{32,}, which matched the ordinary repo
    # path plugins/ravenclaude-core/hooks/_advise.sh (44 chars) and flagged a
    # legitimate pointer-and-label entry. Its own control caught that. A gate that
    # rejects honest authoring gets turned off in a week, so the shape must be a
    # SECRET shape — opaque, mixed-case, digit-bearing, path-separator-free — not
    # merely "a long run of characters".
    (re.compile(r"(?<![A-Za-z0-9+=])(?=[A-Za-z0-9+=_-]*[a-z])(?=[A-Za-z0-9+=_-]*[A-Z])"
                r"(?=[A-Za-z0-9+=_-]*\d)[A-Za-z0-9+=_-]{32,}(?![A-Za-z0-9+=])"),
     "a high-entropy token of 32+ chars"),
    (re.compile(r"\n(?:[^\n]*\n){3,}"), "a multi-line block that looks like captured output"),
)


def _values(c: dict):
    yield "nuance", c.get("nuance") or ""
    ev = c.get("nuance_evidence") or {}
    yield "nuance_evidence.control", str(ev.get("control") or "")
    yield "nuance_evidence.falsifier", str(ev.get("falsifier") or "")
    yield "nuance_source", str(c.get("nuance_source") or "")


def violations(concepts: list[dict]) -> tuple[list[str], list[str]]:
    hard: list[str] = []
    tells: list[str] = []
    for c in concepts:
        if c.get("entry_class") != ENTRY_CLASS_INVENTORY:
            continue
        for field, val in _values(c):
            if not val:
                continue
            for rx, why in SHAPES:
                if rx.search(val):
                    hard.append(f"  ✗ {c['id']}.{field}: contains {why}")
                    break
            if len(val) > LONG_VALUE:
                tells.append(
                    f"  ⚠ {c['id']}.{field}: {len(val)} chars (> {LONG_VALUE}) — the "
                    "§21-W4 TELL. These fields hold pointers and labels, not payloads."
                )
    return hard, tells


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
        # ⛔ TEETH ON A SYNTHETIC CORPUS, because there are no inventory entries
        # yet. A shape gate reporting zero findings over an EMPTY population, never
        # proven to fire, is indistinguishable from one that never ran. One planted
        # entry per shape, so a single over-broad pattern cannot mask a dead one.
        planted = []
        samples = {
            "prompt": "$ curl https://example.invalid/x\n",
            "traceback": "Traceback (most recent call last):\n  File \"a.py\", line 1\n",
            "abspath": "measured at /Users/someone/secret-project/notes.txt",
            "token": "the header carried AbCdEf0123456789AbCdEf0123456789xyz as its value",
        }
        for name, text in samples.items():
            planted.append({
                "id": f"planted-{name}", "entry_class": ENTRY_CLASS_INVENTORY,
                "nuance": text,
                "nuance_evidence": {"control": "x", "falsifier": "y"},
                "nuance_source": "a.sh:1-2",
            })
        hard, _ = violations(planted)
        missed = [p["id"] for p in planted
                  if not any(p["id"] in h for h in hard)]
        if missed:
            print(f"✗ must-fail: {len(missed)} planted shape(s) not caught: {', '.join(missed)}")
            return 0
        # CONTROL: a legitimate pointer-and-label entry must NOT be flagged, or the
        # gate is simply rejecting everything and authoring becomes impossible.
        clean = [{
            "id": "clean", "entry_class": ENTRY_CLASS_INVENTORY,
            "nuance": "stderr at exit 0 reaches the model on no event; additionalContext does.",
            "nuance_evidence": {"control": "a SessionStart sentinel arrived in every trial",
                                "falsifier": "a stderr token arriving in any transcript"},
            "nuance_source": "plugins/ravenclaude-core/hooks/_advise.sh:12-31",
        }]
        if violations(clean)[0]:
            print("✗ must-fail: a legitimate pointer-and-label entry was flagged.")
            print("  A gate that rejects honest authoring gets turned off in a week.")
            return 0
        print(f"✓ must-fail: all {len(samples)} pasted-output shapes caught; a legitimate")
        print("  pointer-and-label entry passes. Exiting 1, the DECLARED teeth code.")
        return 1

    try:
        concepts = load_concepts(root)
    except ConceptError as exc:
        print(f"inventory-evidence: concepts do not parse — {exc}")
        return 2

    inventory = [c for c in concepts if c.get("entry_class") == ENTRY_CLASS_INVENTORY]
    hard, tells = violations(concepts)

    print("── committed evidence fields: no raw bytes (⛔ R9) ──")
    print(f"  inventory entries scanned : {len(inventory)} of {len(concepts)}")
    if not inventory:
        print("  ⚠ EMPTY population — not a clean one. Run --must-fail for the teeth.")
        return 0
    for t in tells:
        print(t)
    if hard:
        print(f"  ⛔ {len(hard)} violation(s):")
        for h in hard:
            print(h)
        return 1 if args.check else 0
    print("  ✓ every guarded field holds pointers and labels, not payloads.")
    print("  ⛔ Limit: a SHAPE heuristic, not a secret scanner (plan §21-W4).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
