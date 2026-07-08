#!/usr/bin/env python3
"""qa_suite_metrics.py — test-suite health metrics (stdlib only, Python 3.8+).

Two modes remove guesswork from two recurring QA decisions:

  flake_rate     Given a JSONL log of test runs, compute a per-test flake rate
                 (a test that passed only on retry is a FLAKE EVENT, not a pass)
                 and rank the flakiest tests. The scenario "flaky-test quarantine
                 graveyard" turns on this: instrument the rate before touching retries.

  pyramid_ratio  Given counts of unit / integration / e2e tests (or a directory to
                 auto-count by filename convention), report the pyramid shape and
                 flag an inverted "ice-cream cone". The scenario "ice-cream cone slow
                 suite" turns on this: measure the distribution before re-platforming.

This is a CALCULATOR / ANALYZER, not a test runner or a data source — the user supplies
the inputs (a run log, or counts). Outputs are decision-support, not a verdict.

Examples:
  qa_suite_metrics.py flake_rate --log runs.jsonl --window-days 30 --top 10
  echo '<jsonl on stdin>' | qa_suite_metrics.py flake_rate
  qa_suite_metrics.py pyramid_ratio --unit 160 --integration 40 --e2e 50
  qa_suite_metrics.py pyramid_ratio --dir tests/

flake_rate input — one JSON object per line (a "run"):
  {"test": "checkout/pays", "outcome": "pass" | "fail" | "flake", "ts": "2026-06-05T..."}
  - "flake" means passed-only-on-retry (the honest classification).
  - A test's flake rate = (fail + flake events) / total runs. `ts` is optional; when
    present and --window-days is set, runs older than the window are dropped.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import sys
from collections import defaultdict

# Outcomes that count against a test's reliability. "flake" = passed only on retry.
_BAD_OUTCOMES = {"fail", "flake"}
_VALID_OUTCOMES = {"pass", "fail", "flake"}

# Filename substrings used to auto-classify a test file's level in pyramid_ratio --dir.
_LEVEL_HINTS: dict[str, tuple[str, ...]] = {
    "e2e": ("e2e", "end2end", "end-to-end", ".cy.", "playwright", "cypress"),
    "integration": ("integration", "_it", ".it.", "contract"),
    "unit": ("unit", ".spec.", ".test.", "_test"),
}
_TEST_FILE_MARKERS = (".test.", ".spec.", "_test", "test_", ".cy.", ".it.")


def _parse_ts(value: object) -> _dt.datetime | None:
    """Parse an ISO-8601 timestamp; return None on anything unparseable."""
    if not isinstance(value, str) or not value:
        return None
    text = value.replace("Z", "+00:00")
    try:
        parsed = _dt.datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=_dt.timezone.utc)
    return parsed


def _read_jsonl(path: str | None) -> list[dict]:
    """Read JSONL run records from a file or stdin. Bad lines are skipped, not fatal."""
    if path:
        with open(path, encoding="utf-8") as handle:
            lines = handle.readlines()
    else:
        lines = sys.stdin.read().splitlines()
    records: list[dict] = []
    for raw in lines:
        raw = raw.strip()
        if not raw:
            continue
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            records.append(obj)
    return records


def compute_flake_rates(
    records: list[dict], window_days: int | None
) -> tuple[dict[str, dict[str, int]], int]:
    """Aggregate per-test outcome counts, honoring an optional recency window.

    Returns (per_test_counts, dropped_count) where per_test_counts maps a test name
    to {"pass", "fail", "flake", "total"} counts.
    """
    cutoff: _dt.datetime | None = None
    if window_days is not None and window_days > 0:
        cutoff = _dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(days=window_days)

    per_test: dict[str, dict[str, int]] = defaultdict(
        lambda: {"pass": 0, "fail": 0, "flake": 0, "total": 0}
    )
    dropped = 0
    for rec in records:
        name = rec.get("test")
        outcome = rec.get("outcome")
        if not isinstance(name, str) or outcome not in _VALID_OUTCOMES:
            dropped += 1
            continue
        if cutoff is not None:
            ts = _parse_ts(rec.get("ts"))
            if ts is not None and ts < cutoff:
                continue
        per_test[name][outcome] += 1
        per_test[name]["total"] += 1
    return per_test, dropped


def _rate(counts: dict[str, int]) -> float:
    total = counts["total"]
    if total == 0:
        return 0.0
    bad = sum(counts[o] for o in _BAD_OUTCOMES)
    return bad / total


def run_flake_rate(args: argparse.Namespace) -> int:
    # Reject a nonsensical negative window at the boundary so it can't be silently
    # treated as all-time by the filter while the header still claims "last -Nd".
    if args.window_days is not None and args.window_days <= 0:
        print("error: --window-days must be > 0", file=sys.stderr)
        return 2
    records = _read_jsonl(args.log)
    if not records:
        print("No usable run records found (empty input or all lines unparseable).")
        return 0
    per_test, dropped = compute_flake_rates(records, args.window_days)
    ranked = sorted(
        per_test.items(),
        key=lambda kv: (_rate(kv[1]), kv[1]["total"]),
        reverse=True,
    )

    total_runs = sum(c["total"] for c in per_test.values())
    flaky_tests = [name for name, c in per_test.items() if _rate(c) > 0]
    window = f"last {args.window_days}d" if args.window_days else "all time"

    print("Flake-rate report")
    print(f"  window:        {window}")
    print(f"  tests seen:    {len(per_test)}")
    print(f"  total runs:    {total_runs}")
    print(f"  flaky tests:   {len(flaky_tests)} (rate > 0)")
    if dropped:
        print(f"  dropped lines: {dropped} (missing test/outcome)")
    print()
    print(f"  Top {args.top} by flake rate:")
    print(f"  {'rate':>7}  {'runs':>5}  {'fail':>4}  {'flake':>5}  test")
    for name, counts in ranked[: args.top]:
        print(
            f"  {_rate(counts) * 100:6.1f}%  {counts['total']:>5}  "
            f"{counts['fail']:>4}  {counts['flake']:>5}  {name}"
        )
    print()
    print(
        "  Note: a test that passed only on retry is a FLAKE EVENT, not a pass. "
        "Instrument the rate, then triage by the flake-triage tree — quarantine "
        "carries an owner + deadline, never a graveyard."
    )
    return 0


def _count_tests_in_dir(root: str) -> dict[str, int]:
    """Walk a directory and classify each test file into unit/integration/e2e."""
    counts = {"unit": 0, "integration": 0, "e2e": 0}
    for dirpath, _dirnames, filenames in os.walk(root):
        for fname in filenames:
            lower = fname.lower()
            if not any(marker in lower for marker in _TEST_FILE_MARKERS):
                continue
            rel = os.path.join(dirpath, fname).lower()
            level = "unit"  # default when only a generic test marker matches
            for candidate in ("e2e", "integration", "unit"):
                if any(hint in rel for hint in _LEVEL_HINTS[candidate]):
                    level = candidate
                    break
            counts[level] += 1
    return counts


def run_pyramid_ratio(args: argparse.Namespace) -> int:
    if args.dir is not None:
        if not os.path.isdir(args.dir):
            print(f"error: --dir {args.dir!r} is not a directory", file=sys.stderr)
            return 2
        counts = _count_tests_in_dir(args.dir)
        source = f"auto-counted from {args.dir}"
    else:
        counts = {"unit": args.unit, "integration": args.integration, "e2e": args.e2e}
        source = "supplied counts"

    unit, integ, e2e = counts["unit"], counts["integration"], counts["e2e"]
    total = unit + integ + e2e
    if total == 0:
        print("No tests found / supplied — nothing to analyze.")
        return 0

    def pct(n: int) -> float:
        return n / total * 100

    # Inverted ("ice-cream cone") when E2E is the largest tier or e2e >= unit.
    inverted = e2e >= unit and e2e >= integ
    cone_ish = e2e > unit
    if inverted or cone_ish:
        shape = "ICE-CREAM CONE (inverted) — fat slow E2E layer on a thin unit base"
    elif unit >= integ >= e2e:
        shape = "healthy pyramid (unit > integration > e2e)"
    else:
        shape = "mixed — not a clean pyramid; review the distribution"

    print("Test-pyramid ratio")
    print(f"  source: {source}")
    print(f"  {'unit':>12}: {unit:>5}  ({pct(unit):4.1f}%)")
    print(f"  {'integration':>12}: {integ:>5}  ({pct(integ):4.1f}%)")
    print(f"  {'e2e':>12}: {e2e:>5}  ({pct(e2e):4.1f}%)")
    print(f"  {'total':>12}: {total:>5}")
    print()
    print(f"  shape: {shape}")
    if inverted or cone_ish:
        print(
            "  -> For each slow E2E test, ask the cheapest level that catches THAT "
            "defect (test-level-selection tree). A logic bug caught through the "
            "browser belongs at the unit level."
        )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Test-suite health metrics: flake rate + pyramid ratio.",
    )
    sub = parser.add_subparsers(dest="mode", required=True)

    flake = sub.add_parser("flake_rate", help="per-test flake rate from a JSONL run log")
    flake.add_argument("--log", help="path to JSONL run log (default: stdin)")
    flake.add_argument(
        "--window-days",
        type=int,
        default=None,
        help="drop runs older than N days (requires a 'ts' field; default: all)",
    )
    flake.add_argument("--top", type=int, default=10, help="how many to list (default 10)")
    flake.set_defaults(func=run_flake_rate)

    pyr = sub.add_parser("pyramid_ratio", help="pyramid shape from counts or a directory")
    pyr.add_argument("--unit", type=int, default=0, help="unit test count")
    pyr.add_argument("--integration", type=int, default=0, help="integration test count")
    pyr.add_argument("--e2e", type=int, default=0, help="e2e test count")
    pyr.add_argument(
        "--dir",
        default=None,
        help="auto-count test files under this directory (overrides the counts)",
    )
    pyr.set_defaults(func=run_pyramid_ratio)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
