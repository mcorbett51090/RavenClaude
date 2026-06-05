#!/usr/bin/env python3
"""perf_budget.py - a zero-dependency frontend performance-budget checker.

Two recurring frontend perf decisions, made mechanical and CI-gateable:

  bundle    Compare measured per-route JavaScript transfer sizes against a
            per-route budget (KB, gzip/brotli transfer size). Prints each
            route's headroom or overage and exits non-zero if any route is
            over budget - so it can gate a PR. Pairs with
            best-practices/the-bundle-is-a-budget.md and
            knowledge/styling-and-bundle-decision-trees.md.

  vitals    Check Core Web Vitals field measurements (75th-percentile RUM/CrUX)
            against Google's published "good" thresholds and report
            good / needs-improvement / poor per metric. Pairs with
            best-practices/avoid-layout-shift-reserve-space-for-async-content.md
            and the cls-lcp-perf-budget-regression scenario.

This is a CHECKER, not a measurement tool - it does not run Lighthouse, build
your bundle, or fetch CrUX. You supply the measured numbers (from your bundler's
analyze output and your RUM/CrUX field data); it does the comparison and the
arithmetic and exits with a CI-friendly status. Stdlib only (argparse, json);
runs anywhere Python 3.8+ is present.

Core Web Vitals "good" thresholds are evaluated at the 75th percentile of real
users (Google web.dev, https://web.dev/articles/vitals, retrieved 2026-06-05):
LCP < 2.5 s, INP < 200 ms, CLS < 0.1; "poor" boundaries LCP > 4.0 s,
INP > 500 ms, CLS > 0.25. These thresholds are version-volatile - re-confirm
against web.dev before treating a gate as authoritative ([verify-at-use]).

IMPORTANT: outputs are decision-support. A passing budget is necessary, not
sufficient - measure real field data, not just lab numbers (see the
cls-lcp-perf-budget-regression scenario).

Examples
--------
  # Bundle budget from a JSON map of {route: {size_kb, budget_kb}}
  python3 perf_budget.py bundle --from-json routes.json

  # Bundle budget for a single route inline
  python3 perf_budget.py bundle --route /dashboard --size-kb 240 --budget-kb 180

  # Core Web Vitals field check (LCP seconds, INP ms, CLS unitless)
  python3 perf_budget.py vitals --lcp 3.8 --inp 240 --cls 0.28
"""

from __future__ import annotations

import argparse
import json
import sys

# Core Web Vitals thresholds (75th percentile). [verify-at-use] - web.dev.
# Each metric: (good_max, poor_min, unit). good if value <= good_max;
# poor if value > poor_min; needs-improvement in between.
VITALS_THRESHOLDS = {
    "lcp": (2.5, 4.0, "s"),
    "inp": (200.0, 500.0, "ms"),
    "cls": (0.1, 0.25, ""),
}


def _rate_bucket(value: float, good_max: float, poor_min: float) -> str:
    """Classify a CWV value into good / needs-improvement / poor."""
    if value <= good_max:
        return "good"
    if value > poor_min:
        return "poor"
    return "needs-improvement"


def _check_bundle_rows(rows: list) -> int:
    """Print a per-route budget table; return count of over-budget routes."""
    over = 0
    print(f"{'route':<28} {'size KB':>10} {'budget KB':>10} {'headroom':>10}  status")
    print("-" * 74)
    for row in rows:
        route = str(row["route"])
        size = float(row["size_kb"])
        budget = float(row["budget_kb"])
        headroom = budget - size
        ok = headroom >= 0
        if not ok:
            over += 1
        status = "OK" if ok else "OVER BUDGET"
        print(
            f"{route:<28} {size:>10.1f} {budget:>10.1f} {headroom:>10.1f}  {status}"
        )
    print("-" * 74)
    if over:
        print(f"\n{over} route(s) over budget - failing.")
    else:
        print("\nAll routes within budget.")
    return over


def cmd_bundle(args: argparse.Namespace) -> int:
    """Bundle-budget check. Exit 1 if any route is over budget."""
    if args.from_json:
        try:
            with open(args.from_json, encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"error: could not read --from-json: {exc}", file=sys.stderr)
            return 2
        # Accept either {route: {size_kb, budget_kb}} or a list of row dicts.
        if isinstance(data, dict):
            rows = [
                {"route": k, "size_kb": v["size_kb"], "budget_kb": v["budget_kb"]}
                for k, v in data.items()
            ]
        elif isinstance(data, list):
            rows = data
        else:
            print("error: --from-json must be an object or a list", file=sys.stderr)
            return 2
    else:
        if args.route is None or args.size_kb is None or args.budget_kb is None:
            print(
                "error: provide --from-json, or all of "
                "--route/--size-kb/--budget-kb",
                file=sys.stderr,
            )
            return 2
        rows = [
            {"route": args.route, "size_kb": args.size_kb, "budget_kb": args.budget_kb}
        ]

    try:
        over = _check_bundle_rows(rows)
    except (KeyError, TypeError, ValueError) as exc:
        print(f"error: malformed budget row ({exc})", file=sys.stderr)
        return 2
    return 1 if over else 0


def cmd_vitals(args: argparse.Namespace) -> int:
    """Core Web Vitals field check. Exit 1 if any metric is not 'good'."""
    measured = {"lcp": args.lcp, "inp": args.inp, "cls": args.cls}
    not_good = 0
    print(f"{'metric':<6} {'value':>10} {'good <=':>10} {'poor >':>10}  status")
    print("-" * 56)
    for metric, value in measured.items():
        if value is None:
            continue
        good_max, poor_min, unit = VITALS_THRESHOLDS[metric]
        bucket = _rate_bucket(value, good_max, poor_min)
        if bucket != "good":
            not_good += 1
        vstr = f"{value:g}{unit}"
        print(
            f"{metric.upper():<6} {vstr:>10} {good_max:>9g}{unit:<1} "
            f"{poor_min:>9g}{unit:<1}  {bucket}"
        )
    print("-" * 56)
    if not_good:
        print(
            f"\n{not_good} metric(s) not 'good' (75th pct). "
            "Diagnose by metric + cause - see the cls-lcp scenario."
        )
    else:
        print("\nAll provided metrics are 'good' at the 75th percentile.")
    return 1 if not_good else 0


def build_parser() -> argparse.ArgumentParser:
    """Construct the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="perf_budget.py",
        description="Frontend performance-budget checker (bundle + Core Web Vitals).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    pb = sub.add_parser("bundle", help="Check per-route JS sizes against a budget.")
    pb.add_argument("--from-json", help="JSON file: {route: {size_kb, budget_kb}}.")
    pb.add_argument("--route", help="Single route name (with --size-kb/--budget-kb).")
    pb.add_argument("--size-kb", type=float, help="Measured transfer size (KB).")
    pb.add_argument("--budget-kb", type=float, help="Budget for the route (KB).")
    pb.set_defaults(func=cmd_bundle)

    pv = sub.add_parser("vitals", help="Check field CWV against good thresholds.")
    pv.add_argument("--lcp", type=float, help="Largest Contentful Paint, seconds.")
    pv.add_argument("--inp", type=float, help="Interaction to Next Paint, ms.")
    pv.add_argument("--cls", type=float, help="Cumulative Layout Shift, unitless.")
    pv.set_defaults(func=cmd_vitals)

    return parser


def main(argv: list | None = None) -> int:
    """Entry point. Returns a process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
