#!/usr/bin/env python3
"""check-artifact-budgets.py — P6 §8.1 (⛔ R5). The budgets nothing was enforcing.

⛔ R5 — PLAN B PREMISE WAS FALSE; THE UNDERLYING RISK IS REAL.

Plan B built a per-batch Gate-132 ratchet-raise process around `panel-learn`
tripping the DOM budget. It cannot: `panel-learn` is ALREADY DOM-islanded
(check-dom-budget.py:104,128) — its markup lives in a
`<script type="application/json">` payload the parser reads as CDATA, and an
islanded panel costs a flat `ISLANDED_PANEL_COST = 2` elements. `check()` compares
only the LIVE element total against its ratchet. That whole process was built for
a gate that cannot fire, and it is deleted.

control: verified in this tree before writing a line of this file — `check()` at
check-dom-budget.py:876 compares `measure(path)["total"]` against `budget_for()`
and nothing else, and no payload or byte constant exists anywhere in its 1,032
lines. The docstring MENTIONS a per-panel island payload budget; the code does not
implement one. A grep satisfied by the thing being described is exactly the shape
this initiative exists to catch, so the code was read, not the docstring.

THE REAL, MEASURED RISK, which nothing gates:

  1. PAYLOAD. ~24k elements for 58 concepts is ~411 elements/concept. 162 more
     entries is ~90,000 elements injected into the DOM on one tab click, against
     a Lighthouse threshold of 1,400. The figure is printed by `--report` and
     gated by nothing.
  2. BYTES. dashboard.html and index.html are ~10 MB and ~9 MB, with ZERO byte
     gates among 336 gate headers. 58 concepts already carry 220 SVGs / 4.4 MB;
     2.8x the count plausibly adds 8-12 MB to EACH surface, and nothing warns.

⛔ BOTH RATCHETS ARE SEEDED BEFORE ANY BULK AUTHORING, so the first batch measures
against a real baseline instead of establishing one retroactively.

⛔ THE TWO TABLES CARRY DIFFERENT INVARIANTS. PAYLOAD is a REDUCTION ratchet and
may only ever go DOWN — a phase that could raise its own bar would dodge the very
reduction work the budget forces, which is the rule check-dom-budget.py applies to
its own. BYTES is a CEILING WITH A REVIEWED RAISE: a file that may only shrink
forbids all legitimate growth, so a raise must APPEND a row carrying a real cause,
and cumulative growth since the seed is reported every run so creep cannot hide
inside a series of individually-reasonable raises. See the note above
_monotonic() for the measurement that forced the distinction.

⛔ THE TEETH-BIT EXIT IS 1. Declared, never assumed.

Usage:
    check-artifact-budgets.py                 # report measured vs budget
    check-artifact-budgets.py --check         # gate
    check-artifact-budgets.py --seed          # print rows to paste after a legit growth
    check-artifact-budgets.py --must-fail
    check-artifact-budgets.py --must-fail-convention
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DASHBOARD = "plugins/ravenclaude-core/dashboard.html"
INDEX = "index.html"
SURFACES = (DASHBOARD, INDEX)

# An islanded payload is a <script type="application/json"> block. Inside it every
# `<` survives verbatim (the HTML parser reads it as CDATA), so a tag-open counter
# measures what activate() will inject into the live DOM.
_ISLAND = re.compile(
    r'<script[^>]*type=["\']application/json["\'][^>]*\bid=["\']([^"\']+)["\'][^>]*>(.*?)</script>',
    re.DOTALL | re.IGNORECASE,
)
_TAG_OPEN = re.compile(r"<[A-Za-z][A-Za-z0-9-]*[\s/>]")

# ══ THE RATCHET TABLES ═════════════════════════════════════════════════════
# Each row: (label, value, why). The budget in force is the LAST row. Append a
# row to raise a budget, never edit one — the append is the reviewable artifact.
# ⛔ Seeded 2026-08-19 from a measurement of this tree, BEFORE any inventory
# authoring, which is the whole point: a budget established retroactively after a
# batch lands is a description of what happened, not a constraint on it.
PAYLOAD_RATCHET: dict[str, list[tuple[str, int, str]]] = {}
BYTE_RATCHET: dict[str, list[tuple[str, int, str]]] = {}


def _load_seed() -> None:
    """Seed rows live in a sibling JSON so a re-seed is a data diff, not a code
    diff — a code diff invites 'while I am here' edits to the gate itself."""
    seed = Path(__file__).resolve().parent / "artifact-budgets.seed.json"
    if not seed.is_file():
        return
    import json

    data = json.loads(seed.read_text(encoding="utf-8"))
    for surface, rows in data.get("payload", {}).items():
        PAYLOAD_RATCHET[surface] = [tuple(r) for r in rows]
    for surface, rows in data.get("bytes", {}).items():
        BYTE_RATCHET[surface] = [tuple(r) for r in rows]


def payload_counts(root: Path, surface: str) -> dict[str, int]:
    fp = root / surface
    if not fp.is_file():
        return {}
    text = fp.read_text(encoding="utf-8", errors="replace")
    out = {}
    for pid, body in _ISLAND.findall(text):
        out[pid] = len(_TAG_OPEN.findall(body))
    return out


def byte_size(root: Path, surface: str) -> int:
    fp = root / surface
    return fp.stat().st_size if fp.is_file() else 0


# ⛔ THE TWO TABLES HAVE DIFFERENT INVARIANTS, AND CONFLATING THEM IS A BUG.
#
# PAYLOAD is a REDUCTION ratchet, exactly like check-dom-budget.py own: the danger
# is ~90,000 elements injected on one tab click against a Lighthouse threshold of
# 1,400, so the budget may only ever go DOWN. A phase that could raise its own bar
# would dodge the very reduction work the budget exists to force.
#
# BYTES is a CEILING WITH A REVIEWED RAISE. A file that may only ever shrink
# forbids all legitimate growth — and this was measured, not theorised: the R12
# badge CSS added 1,776 bytes and the first version of this gate rejected it with
# no path forward except deleting the feature. The invariant that actually matters
# for bytes is that growth is DELIBERATE AND VISIBLE, so a raise must append a row
# carrying a real cause, and the cumulative growth since the seed is reported every
# run so creep cannot hide inside a series of individually-reasonable raises.
RAISE_CAUSE_MIN = 30


def _monotonic(rows: list[tuple[str, int, str]]) -> bool:
    """Reduction-ratchet invariant: values may never increase."""
    vals = [v for _, v, _ in rows]
    return vals == sorted(vals, reverse=True) or len(vals) <= 1


def _reviewed_raises(rows: list[tuple[str, int, str]]) -> list[str]:
    """Ceiling invariant: any raise must carry a real cause, not a shrug."""
    problems = []
    for i in range(1, len(rows)):
        prev, cur = rows[i - 1][1], rows[i][1]
        if cur > prev and len(str(rows[i][2]).strip()) < RAISE_CAUSE_MIN:
            problems.append(
                f"row '{rows[i][0]}' raises the ceiling {prev:,} -> {cur:,} with under "
                f"{RAISE_CAUSE_MIN} chars of cause. A raise with no reason is not a review."
            )
    return problems


def evaluate(root: Path) -> tuple[int, list[str]]:
    rc = 0
    lines: list[str] = []
    for surface in SURFACES:
        # ── payload ──
        counts = payload_counts(root, surface)
        rows = PAYLOAD_RATCHET.get(surface)
        if not rows:
            lines.append(f"  ⚠ {surface}: no payload budget seeded — UNKNOWN, not clean")
            rc = 1
            continue
        if not _monotonic(rows):
            lines.append(f"  ✗ {surface}: payload ratchet is not monotonically non-increasing")
            rc = 1
        budget = rows[-1][1]
        total = sum(counts.values())
        biggest = max(counts.items(), key=lambda kv: kv[1], default=("(none)", 0))
        if total > budget:
            lines.append(
                f"  ✗ {surface}: island payload {total:,} elements > budget {budget:,} "
                f"(over by {total - budget:,}; largest panel {biggest[0]} at {biggest[1]:,})"
            )
            rc = 1
        else:
            lines.append(
                f"  ✓ {surface}: island payload {total:,} <= {budget:,} "
                f"(largest panel {biggest[0]} at {biggest[1]:,})"
            )

        # ── bytes ──
        brows = BYTE_RATCHET.get(surface)
        if not brows:
            lines.append(f"  ⚠ {surface}: no byte budget seeded — UNKNOWN, not clean")
            rc = 1
            continue
        for prob in _reviewed_raises(brows):
            lines.append(f"  ✗ {surface}: {prob}")
            rc = 1
        bbudget = brows[-1][1]
        size = byte_size(root, surface)
        if size > bbudget:
            lines.append(
                f"  ✗ {surface}: {size:,} bytes > budget {bbudget:,} "
                f"(over by {size - bbudget:,} = {(size - bbudget) / 1048576:.2f} MB)"
            )
            rc = 1
        else:
            seed_val = brows[0][1]
            grown = size - seed_val
            pct = (grown / seed_val * 100) if seed_val else 0
            lines.append(
                f"  ✓ {surface}: {size:,} bytes <= {bbudget:,} "
                f"(cumulative growth since seed: {grown:+,} = {pct:+.2f}%)"
            )
    return rc, lines


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=".")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--seed", action="store_true")
    ap.add_argument("--must-fail", action="store_true")
    ap.add_argument("--must-fail-convention", action="store_true")
    args = ap.parse_args()

    if args.must_fail_convention:
        print("must-fail-teeth-exit: 1")
        return 0

    _load_seed()
    root = Path(args.root).resolve()

    if args.seed:
        import json

        data = {"payload": {}, "bytes": {}}
        for surface in SURFACES:
            total = sum(payload_counts(root, surface).values())
            data["payload"][surface] = [["seeded 2026-08-19", total,
                                        "measured before any inventory authoring"]]
            data["bytes"][surface] = [["seeded 2026-08-19", byte_size(root, surface),
                                       "measured before any inventory authoring"]]
        print(json.dumps(data, indent=2))
        return 0

    if args.must_fail:
        # TEETH. Raise the measured value past the budget and require a catch, in
        # BOTH dimensions independently — a single over-broad failure path would
        # otherwise hide a dead one.
        rc_before, _ = evaluate(root)
        if rc_before != 0:
            print("✗ must-fail: the pristine tree already fails, so a planted overrun")
            print("  proves nothing. Fix or re-seed the budgets first.")
            return 0
        caught = 0
        for table in (PAYLOAD_RATCHET, BYTE_RATCHET):
            saved = {k: list(v) for k, v in table.items()}
            for k in table:
                table[k] = [(lbl, max(0, val - 1), why) for lbl, val, why in table[k]]
            rc_after, _ = evaluate(root)
            for k, v in saved.items():
                table[k] = v
            if rc_after != 0:
                caught += 1
        if caught != 2:
            print(f"✗ must-fail: only {caught} of 2 budget dimensions caught an overrun.")
            print("  A dimension that cannot fail is not a budget.")
            return 0
        print("✓ must-fail: both the payload and the byte budget catch an overrun,")
        print("  and the pristine tree passes. Exiting 1, the DECLARED teeth code.")
        return 1

    rc, lines = evaluate(root)
    print("── artifact budgets: island payload + bytes (⛔ R5) ──")
    for ln in lines:
        print(ln)
    print()
    print("  ⛔ Seeded BEFORE bulk authoring. A budget established after a batch")
    print("     lands describes what happened; it does not constrain it.")
    print("     To raise one legitimately: APPEND a row to artifact-budgets.seed.json")
    print("     with a cause comment. Never edit a row — the append is the review.")
    return rc if args.check else 0


if __name__ == "__main__":
    sys.exit(main())
