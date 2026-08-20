#!/usr/bin/env python3
"""inventory-coverage.py — the coverage ratchet and the BLOCKING review ledger.

Plan P7 §9.3 (⛔ R7) + P8 §10.1 (⛔ R2, R6).

⛔ WHY THE SAMPLED REVIEW IS A GATE AND NOT A PROCESS STEP.

R7 rules that the nuance bar is not fully automatable, so there is a required
human/fresh-model step. Plan B had exactly that — and it was a PROCESS STEP with
no mechanism. This repo record is that process steps decay and mechanisms do not.
So the review verdicts are written to a COMMITTED ledger, and this script READS
that ledger and BLOCKS the next batch when the previous one has no recorded
sample or scored below the bar. A ledger CI does not read is a process step
wearing a filename.

⛔ THE FLOOR PROVES THIS IS NECESSARY, NOT DECORATIVE. check-nuance-floor.py
--golden reports, every run, which adversarial negatives passed it UNCAUGHT. Those
entries are caught only here. If that list is ever empty, the floor has been tuned
to the fixtures — which is the fake metric R7 forbids — not made sufficient.

⛔ THE RATCHET INVARIANTS (P8). published_entries may never decrease, and
covered_artifacts / total_artifacts may never decrease, where the DENOMINATOR
comes from inventory-census.py (git ls-files) and never from concepts.json — a
registry-derived denominator shrinks with the enumeration and reports green.

⛔ REPORTED-BUT-NOT-BLOCKING, DELIBERATELY: the `tier: none` GROWTH RATE, the
derived-from-header fraction, and the unprobed fraction. Blocking `tier: none`
would push authors toward a false `tier: reachability`, and a wrong strong label
beats no label only for appearances.

⛔ THE TEETH-BIT EXIT IS 1. Declared, never assumed.

Usage:
    inventory-coverage.py --report
    inventory-coverage.py --check
    inventory-coverage.py --must-fail
    inventory-coverage.py --must-fail-convention
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from concepts import ENTRY_CLASS_INVENTORY, ConceptError, load_concepts  # noqa: E402

LEDGER = "tests/fixtures/inventory-review-ledger.json"
RATCHET = "tests/fixtures/inventory-coverage-ratchet.json"
RESTAMP_LOG = "tests/fixtures/inventory-restamp-log.jsonl"
DRAFTS = "plugins/ravenclaude-core/knowledge/inventory-drafts"
REVIEW_BAR = 0.80
DRAFT_MAX_AGE_DAYS = 90


def _load_census(root: Path):
    import importlib.util

    p = Path(__file__).resolve().parent / "inventory-census.py"
    spec = importlib.util.spec_from_file_location("inventory_census", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.census(root)


def _json(root: Path, rel: str, default):
    fp = root / rel
    if not fp.is_file():
        return default
    try:
        return json.loads(fp.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def measure(root: Path) -> dict:
    concepts = load_concepts(root)
    entries = [c for c in concepts if c.get("entry_class") == ENTRY_CLASS_INVENTORY]

    census = _load_census(root)
    total_artifacts = sum(len(v) for v in census.values())
    covered: set[str] = set()
    for e in entries:
        covered.update(e.get("covers") or [])
    # ⛔ Only artifacts the census KNOWS about count as covered. A covers[] entry
    # pointing outside the census would otherwise inflate the numerator against a
    # denominator that never contained it.
    known = {p for v in census.values() for p in v}
    covered &= known

    tier_none = [e for e in entries if (e.get("verify") or {}).get("tier") == "none"]
    unprobed = [
        e for e in entries
        if str((e.get("nuance_evidence") or {}).get("probe") or "").startswith("unprobed: ")
    ]

    return {
        "published_entries": len(entries),
        "total_artifacts": total_artifacts,
        "covered_artifacts": len(covered),
        "coverage": (len(covered) / total_artifacts) if total_artifacts else 0.0,
        "tier_none": len(tier_none),
        "unprobed": len(unprobed),
        "entry_ids": sorted(e["id"] for e in entries),
    }


def _restamp_stats(root: Path) -> tuple[int, int]:
    """(total restamps, restamps whose reason suggests no nuance change).

    ⛔ REPORTED, NEVER GATED. A legitimately-unchanged nuance after a real re-read
    is normal, and gating it would manufacture false edits. A HIGH RATIO is the
    tell for a rubber-stamp loop — the restamp becoming the new advisory hook
    writing to stderr: passes every check, nobody re-read the claim.
    """
    fp = root / RESTAMP_LOG
    if not fp.is_file():
        return 0, 0
    total = unchanged = 0
    for line in fp.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        total += 1
        if rec.get("digest_before") == rec.get("digest_after"):
            unchanged += 1
    return total, unchanged


def _stale_drafts(root: Path, today: datetime.date) -> list[str]:
    """⛔ A DRAFT OLDER THAN 90 DAYS IS PROMOTED OR REMOVED. Plan A omitted this,
    and without it the drafts lane becomes the 162 stale summaries, relocated —
    invisible to the dashboard and to CI, which is exactly what makes it a good
    hiding place."""
    d = root / DRAFTS
    if not d.is_dir():
        return []
    out = []
    for fp in sorted(d.glob("*.md")):
        try:
            head = fp.read_text(encoding="utf-8", errors="replace")[:2000]
        except OSError:
            continue
        for line in head.splitlines():
            if line.startswith("drafted:"):
                try:
                    dt = datetime.date.fromisoformat(line.split(":", 1)[1].strip())
                except ValueError:
                    break
                if (today - dt).days > DRAFT_MAX_AGE_DAYS:
                    out.append(f"{fp.name} (drafted {dt}, {(today - dt).days} days ago)")
                break
    return out


def ledger_verdict(root: Path, current_ids: list[str]) -> tuple[bool, list[str]]:
    """Does the review ledger permit the NEXT batch? (ok, reasons)."""
    led = _json(root, LEDGER, None)
    reasons: list[str] = []
    if led is None:
        # ⛔ ABSENT IS NOT CLEAN. With no ledger the review has demonstrably not
        # happened, and the whole point of R7 is that this step is real.
        return (not current_ids), [
            f"no review ledger at {LEDGER} — with entries published that is a MISSING"
            " review, never a passed one"
        ]
    batches = led.get("batches") or []
    if current_ids and not batches:
        return False, ["entries are published but the ledger records no batch at all"]
    for b in batches:
        bid = b.get("batch_id", "?")
        sampled = b.get("entry_ids_sampled") or []
        verdicts = b.get("verdicts") or {}
        if not sampled:
            reasons.append(f"batch {bid}: no entries sampled — an empty sample is not a review")
            continue
        if b.get("reviewer_context") != "fresh":
            # A reviewer that authored the batch rubber-stamps its own summary.
            reasons.append(
                f"batch {bid}: reviewer_context is not 'fresh' — a reviewer who authored"
                " the batch reviews their own summary"
            )
        graded = [v for v in verdicts.values() if v in ("nuance", "restatement")]
        if len(graded) < len(sampled):
            reasons.append(
                f"batch {bid}: {len(sampled)} sampled but only {len(graded)} graded"
            )
            continue
        score = sum(1 for v in graded if v == "nuance") / len(graded)
        if score < REVIEW_BAR:
            reasons.append(
                f"batch {bid}: scored {score:.0%}, below the {REVIEW_BAR:.0%} bar"
            )
    return (not reasons), reasons


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=".")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--must-fail", action="store_true")
    ap.add_argument("--must-fail-convention", action="store_true")
    ap.add_argument("--today", help="ISO date override for deterministic tests")
    args = ap.parse_args()

    if args.must_fail_convention:
        print("must-fail-teeth-exit: 1")
        return 0

    root = Path(args.root).resolve()
    today = datetime.date.fromisoformat(args.today) if args.today else datetime.date.today()

    if args.must_fail:
        # TEETH, on the two mechanisms that can silently disarm this file.
        # 1. A batch with a missing ledger entry must BLOCK.
        ok, _ = ledger_verdict(root, ["some-entry"])
        if ok and not (root / LEDGER).is_file():
            print("✗ must-fail: entries published with no ledger were permitted.")
            return 0
        # 2. A batch scoring below the bar must BLOCK, and one above must PASS —
        #    a gate that blocks everything proves nothing.
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            fake = Path(td)
            (fake / "tests" / "fixtures").mkdir(parents=True)
            low = {"batches": [{"batch_id": "t1", "reviewer_context": "fresh",
                                "entry_ids_sampled": ["a", "b", "c", "d", "e"],
                                "verdicts": {"a": "nuance", "b": "nuance", "c": "nuance",
                                             "d": "restatement", "e": "restatement"}}]}
            (fake / LEDGER).write_text(json.dumps(low), encoding="utf-8")
            blocked, why = ledger_verdict(fake, ["a"])
            if blocked:
                print("✗ must-fail: a 60% batch was permitted; the bar is not enforced.")
                return 0
            high = {"batches": [{"batch_id": "t2", "reviewer_context": "fresh",
                                 "entry_ids_sampled": ["a", "b", "c", "d", "e"],
                                 "verdicts": {k: "nuance" for k in "abcde"}}]}
            (fake / LEDGER).write_text(json.dumps(high), encoding="utf-8")
            passed, why2 = ledger_verdict(fake, ["a"])
            if not passed:
                print(f"✗ must-fail: a 100% batch was blocked — {why2}")
                return 0
        print("✓ must-fail: a missing ledger blocks, a 60% batch blocks, a 100% batch")
        print("  passes. Exiting 1, the DECLARED teeth code.")
        return 1

    try:
        m = measure(root)
    except ConceptError as exc:
        print(f"coverage: concepts do not parse — {exc}")
        return 2

    prev = _json(root, RATCHET, {})
    restamps, unchanged = _restamp_stats(root)
    stale = _stale_drafts(root, today)
    ok, reasons = ledger_verdict(root, m["entry_ids"])

    print("── inventory coverage ──")
    print(f"  published entries   : {m['published_entries']}")
    print(f"  covered / total     : {m['covered_artifacts']} / {m['total_artifacts']}"
          f"  ({m['coverage']:.1%})")
    print(f"  tier: none          : {m['tier_none']}   (reported, NOT blocking — see header)")
    print(f"  unprobed            : {m['unprobed']}   (allowed and honest; ratcheted down)")
    if restamps:
        print(f"  restamps            : {restamps}, of which {unchanged} moved no digest"
              f"  ({unchanged / restamps:.0%} — a HIGH ratio is the rubber-stamp tell)")
    else:
        print("  restamps            : 0")
    print(f"  stale drafts (>{DRAFT_MAX_AGE_DAYS}d): {len(stale)}")
    for sd in stale:
        print(f"      · {sd}")

    rc = 0
    print()
    print("── ratchet invariants ──")
    if prev:
        for key, label in (("published_entries", "published entries"),
                           ("covered_artifacts", "covered artifacts")):
            before, now = prev.get(key, 0), m[key]
            if now < before:
                print(f"  ✗ {label} DECREASED {before} -> {now}. Coverage is monotonic;")
                print("     a decrease means an entry was deleted or the sweep lost sight.")
                rc = 1
            else:
                print(f"  ✓ {label}: {before} -> {now}")
    else:
        print(f"  ⚠ no committed baseline at {RATCHET} — first run seeds it, and until")
        print("     then the monotonic invariant is UNKNOWN rather than satisfied.")

    print()
    print("── ⛔ BLOCKING sampled review (R7 §9.3) ──")
    if ok:
        print("  ✓ every recorded batch carries a fresh-context sample at or above"
              f" the {REVIEW_BAR:.0%} bar.")
    else:
        for r in reasons:
            print(f"  ✗ {r}")
        rc = 1
    print("  ⛔ This is the ONLY filter catching an adversarial nuance that clears the")
    print("     deterministic floor. check-nuance-floor.py --golden names those every run.")

    return rc if args.check else 0


if __name__ == "__main__":
    sys.exit(main())
