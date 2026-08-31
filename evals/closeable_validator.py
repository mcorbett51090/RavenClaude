#!/usr/bin/env python3
"""Closeable-register validator (analog-repos-gap-fill P0 / F2).

A row is closeable iff C1–C5 hold. Analog prose may attest; it may not mint
a closeable row (no `because_analog` as sole evidence; acceptance_test must
judge transferred behavior, not only this schema).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

SHIP_PREFIXES = (
    "plugins/",
    ".github/workflows/",
    "scripts/ravenclaude",
    "scripts/check-",
    "scripts/audit-gates.sh",
    "evals/",
    "tests/fixtures/",
)

FORBIDDEN_TEST_TOKENS = ("register schema", "schema fixture", "looks better")


def classify(row: dict) -> tuple[str, str]:
    """Return (tag, reason). tag is closeable | rejected."""
    if row.get("because_analog") and not row.get("local_known_bad"):
        return "rejected", "C4: analog-only generator (because_analog without local_known_bad)"
    ships = str(row.get("ships_in") or "")
    if not any(ships.startswith(p) or p in ships for p in SHIP_PREFIXES):
        return "rejected", "C1: ships_in is not a marketplace/plugin/CI locus"
    test = str(row.get("acceptance_test") or "").strip()
    if not test:
        return "rejected", "C2: missing acceptance_test"
    low = test.lower()
    if any(tok in low for tok in FORBIDDEN_TEST_TOKENS):
        return "rejected", "C2: acceptance_test only names the register schema"
    if not row.get("local_known_bad"):
        return "rejected", "C4: no local known-bad"
    if not row.get("lattice_id"):
        return "rejected", "C5: missing lattice_id"
    return "closeable", "C1–C5 hold"


def self_test() -> int:
    here = Path(__file__).resolve().parent.parent
    fx = here / "tests" / "fixtures" / "closeable-register"
    cases = [
        ("pass.json", "closeable"),
        ("fail-c1.json", "rejected"),
        ("fail-c4.json", "rejected"),
    ]
    errors = 0
    for name, want in cases:
        row = json.loads((fx / name).read_text())
        got, why = classify(row)
        ok = got == want
        print(f"{'OK' if ok else 'FAIL'}  {name}: {got} ({why})")
        if not ok:
            errors += 1
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    print("usage: closeable_validator.py --self-test", file=sys.stderr)
    sys.exit(2)
