#!/usr/bin/env python3
"""Fabric capacity / F-SKU sizing helper — decision-support, NOT pricing.

Removes arithmetic error from three recurring Microsoft Fabric capacity decisions.
It is a *calculator*, not a data source and not a price list: the user supplies every
input (CU readings come from the Fabric Capacity Metrics app), and **no prices are
baked in** — cost is left to the Azure Pricing Calculator / a reservation quote, by
design (the repo forbids baked-in prices, and Fabric SKU pricing is region- and
time-volatile). Outputs are decision-support, never a sizing guarantee.

Three modes:

  sku-fit       Given an average and peak CU reading, recommend the smallest F-SKU
                that covers the average (the size-to-average-not-peak rule) and report
                the headroom + whether smoothing/bursting should absorb the peak.

  smoothing     Given a background job's CU-seconds and the smoothing window, show the
                smoothed per-timepoint CU draw (background ops smooth over 24h) so you
                can see whether a "scary" peak actually fits under a SKU after smoothing.

  isolation     Given per-workload average CU, compare "one shared capacity" vs
                "isolate the noisy workload onto its own capacity" by required CU only
                (the FinOps isolation lever — house opinion #5). Reports CU per option;
                the cost trade-off is the user's to price out per SKU.

All inputs are explicit flags; nothing is fetched or assumed. Python 3.8+, stdlib only.

Examples:
  python3 fabric_capacity_calc.py sku-fit --avg-cu 48 --peak-cu 110
  python3 fabric_capacity_calc.py smoothing --cu-seconds 540000 --window-hours 24
  python3 fabric_capacity_calc.py isolation --interactive-cu 40 --background-cu 36
"""

from __future__ import annotations

import argparse
import sys

# F-SKU -> Capacity Units. Source: Microsoft Learn "Microsoft Fabric concepts and
# licenses" / "Plan your capacity size" (retrieved 2026-06-05). CU is a capability
# figure, NOT a price; re-confirm the ladder at use (Fabric ships monthly).
F_SKU_CU = {
    "F2": 2,
    "F4": 4,
    "F8": 8,
    "F16": 16,
    "F32": 32,
    "F64": 64,
    "F128": 128,
    "F256": 256,
    "F512": 512,
    "F1024": 1024,
    "F2048": 2048,
}

DISCLAIMER = (
    "Decision-support only — CU figures from the Fabric Capacity Metrics app; "
    "no prices baked in (price per SKU/region via the Azure Pricing Calculator). "
    "Validate against live Metrics-app data before a deliverable."
)


def _smallest_sku_for(cu_needed: float) -> str | None:
    """Return the smallest F-SKU name whose CU >= cu_needed, or None if off the ladder."""
    for name, cu in sorted(F_SKU_CU.items(), key=lambda kv: kv[1]):
        if cu >= cu_needed:
            return name
    return None


def cmd_sku_fit(args: argparse.Namespace) -> int:
    avg = args.avg_cu
    peak = args.peak_cu
    if avg <= 0:
        print("error: --avg-cu must be > 0", file=sys.stderr)
        return 2
    if peak < avg:
        print("error: --peak-cu must be >= --avg-cu", file=sys.stderr)
        return 2

    sku = _smallest_sku_for(avg)
    print("== Fabric SKU fit (size to AVERAGE, not peak) ==")
    print(f"  Average CU draw : {avg:g}")
    print(f"  Peak CU draw    : {peak:g}")
    if sku is None:
        print(
            f"  Recommended SKU : none on the F2..F2048 ladder covers {avg:g} CU "
            "— scale out (multiple capacities) instead of up."
        )
        return _emit_disclaimer_ok()

    cu = F_SKU_CU[sku]
    headroom = cu - avg
    headroom_pct = (headroom / cu) * 100
    peak_ratio = peak / cu
    print(f"  Recommended SKU : {sku} ({cu} CU) — smallest covering the average")
    print(f"  Headroom        : {headroom:g} CU ({headroom_pct:.0f}% of the SKU)")
    print(f"  Peak vs SKU     : {peak_ratio:.2f}x the SKU's CU")
    if peak_ratio <= 1.0:
        print("  Peak note       : peak is within the SKU — comfortably covered.")
    else:
        print(
            "  Peak note       : peak exceeds the SKU; for BACKGROUND work, 24h "
            "smoothing + bursting often absorb it (check the 'smoothing' mode). "
            "For sustained INTERACTIVE peaks, isolate the noisy workload or size up "
            "(traverse the capacity-throttled decision tree before scaling)."
        )
    if headroom_pct < 15:
        print(
            "  Warning         : <15% headroom — little room for growth; "
            "consider the next SKU up if load is trending upward."
        )
    return _emit_disclaimer_ok()


def cmd_smoothing(args: argparse.Namespace) -> int:
    cu_seconds = args.cu_seconds
    window_hours = args.window_hours
    if cu_seconds <= 0 or window_hours <= 0:
        print("error: --cu-seconds and --window-hours must be > 0", file=sys.stderr)
        return 2

    window_seconds = window_hours * 3600
    smoothed_cu = cu_seconds / window_seconds
    print("== CU smoothing (background ops smooth over ~24h) ==")
    print(f"  Job total CU-seconds : {cu_seconds:g}")
    print(f"  Smoothing window     : {window_hours:g} h ({window_seconds:g} s)")
    print(f"  Smoothed CU draw     : {smoothed_cu:.3f} CU (averaged across the window)")
    sku = _smallest_sku_for(smoothed_cu)
    if sku is not None:
        print(
            f"  Fits under           : {sku} ({F_SKU_CU[sku]} CU) on the smoothed draw "
            "alone — a large momentary peak can still be absorbed once spread."
        )
    print(
        "  Note                 : interactive ops smooth over 5-64 min, background "
        "over ~24h. A peak that looks over-budget for 10 min may be fine once "
        "smoothed — verify over a LONG window in the Metrics app, don't panic-scale."
    )
    return _emit_disclaimer_ok()


def cmd_isolation(args: argparse.Namespace) -> int:
    interactive = args.interactive_cu
    background = args.background_cu
    if interactive <= 0 or background <= 0:
        print(
            "error: --interactive-cu and --background-cu must be > 0", file=sys.stderr
        )
        return 2

    shared_cu = interactive + background
    shared_sku = _smallest_sku_for(shared_cu)
    bi_sku = _smallest_sku_for(interactive)
    prep_sku = _smallest_sku_for(background)

    print("== Isolation: one shared capacity vs isolate the noisy workload ==")
    print(f"  Interactive BI avg CU : {interactive:g}")
    print(f"  Background avg CU     : {background:g}")
    print()
    print("  Option A — one shared capacity (no isolation):")
    print(
        f"    required CU = {shared_cu:g} -> "
        f"{shared_sku or 'off-ladder; scale out'}"
    )
    print("    risk: per-capacity throttling — a background surge can reject BI ops")
    print("          (many SQL/UI ops bill as background). House-opinion #5 anti-pattern.")
    print()
    print("  Option B — isolate (BI on its own capacity, prep on another):")
    print(f"    BI capacity   = {interactive:g} CU -> {bi_sku or 'off-ladder'}")
    print(f"    prep capacity = {background:g} CU -> {prep_sku or 'off-ladder'}")
    print("    benefit: BI is structurally protected from background surges.")
    print()
    print(
        "  Trade-off is yours to price: compare Option A's single SKU vs Option B's two "
        "SKUs at your region's rates (Azure Pricing Calculator / reservation quote). "
        "Isolation often costs less than scaling the shared SKU up to brute-force the "
        "collision — but always price both."
    )
    return _emit_disclaimer_ok()


def _emit_disclaimer_ok() -> int:
    print()
    print(f"  [{DISCLAIMER}]")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fabric_capacity_calc.py",
        description="Fabric capacity / F-SKU sizing helper (decision-support, no prices).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_fit = sub.add_parser(
        "sku-fit", help="recommend the smallest F-SKU for an average CU draw"
    )
    p_fit.add_argument("--avg-cu", type=float, required=True, help="average CU draw")
    p_fit.add_argument("--peak-cu", type=float, required=True, help="peak CU draw")
    p_fit.set_defaults(func=cmd_sku_fit)

    p_sm = sub.add_parser(
        "smoothing", help="show the smoothed per-window CU draw for a background job"
    )
    p_sm.add_argument(
        "--cu-seconds", type=float, required=True, help="total CU-seconds the job consumes"
    )
    p_sm.add_argument(
        "--window-hours",
        type=float,
        default=24.0,
        help="smoothing window in hours (background ~24; default 24)",
    )
    p_sm.set_defaults(func=cmd_smoothing)

    p_iso = sub.add_parser(
        "isolation", help="compare shared vs isolated capacity by required CU"
    )
    p_iso.add_argument(
        "--interactive-cu", type=float, required=True, help="interactive BI average CU"
    )
    p_iso.add_argument(
        "--background-cu",
        type=float,
        required=True,
        help="background (prep/pipeline/AI) average CU",
    )
    p_iso.set_defaults(func=cmd_isolation)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
