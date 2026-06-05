#!/usr/bin/env python3
"""rcm_calc.py — a zero-dependency revenue-cycle decision calculator.

Removes arithmetic error from four recurring RCM read/decision points an
RCM leader, analyst, or consultant runs constantly:

  ar-days         Days in accounts receivable = total outstanding A/R /
                  average daily charges. Optionally segments the A/R by aging
                  bucket and flags the over-90-day share against the <10%
                  benchmark. Pairs with knowledge/rcm-decision-trees.md
                  ("A/R is piling up") and the work-down-ar skill.

  net-collection  Net collection rate = payments / (charges - contractual
                  adjustments), i.e. collected against the ALLOWED amount, not
                  gross charges (CLAUDE.md §3 #4). Optionally shows the gross
                  collection rate alongside it to expose the gap. Flags against
                  the 95-98% benchmark. Pairs with knowledge/rcm-kpi-glossary.md.

  clean-claim     The cost of every point below your clean-claim / first-pass
                  target: rework_claims = total_claims * (target - actual), then
                  rework_cost = rework_claims * cost_per_rework. Turns "our
                  first-pass rate is 88%" into a dollar figure (CLAUDE.md §3 #2).

  denial-recovery The cash sitting in an unworked denial queue: recoverable =
                  denied_dollars * recoverable_rate, and the amount lost if the
                  industry "never reworked" share holds. Pairs with the
                  denials decision trees and the prevent-denials skill.

This is a CALCULATOR, not a data source — it does not fetch benchmarks, fee
schedules, contracts, or live A/R. The user supplies every input; the tool does
the arithmetic and shows the formula. Stdlib only (argparse); runs anywhere
Python 3.8+ is present.

IMPORTANT: outputs are decision-support, not coding, billing-compliance, or
legal advice (see ../CLAUDE.md §2). Coding/billing decisions remain with a
credentialed coder. Validate every figure against the client's actual data
before any deliverable (CLAUDE.md §3 #8). Benchmark thresholds shown here are
defaults from public sources (see ../knowledge/rcm-benchmarks-2026.md) and are
overridable; they are dated and payer-dependent.

Examples
--------
  # Days in A/R: $1.2M outstanding, $40k average daily charges, with the
  # over-90 bucket at $180k of that A/R
  python3 rcm_calc.py ar-days --ar 1200000 --avg-daily-charges 40000 \\
      --over-90 180000

  # Net collection rate: $900k collected, $1.5M charges, $480k contractual
  # adjustments (so allowed = 1,020,000)
  python3 rcm_calc.py net-collection --payments 900000 --charges 1500000 \\
      --contractual-adjustments 480000

  # Clean-claim rework cost: 10,000 claims/mo at 88% first-pass vs a 95%
  # target, $7 fully-loaded cost per rework touch
  python3 rcm_calc.py clean-claim --claims 10000 --actual 88% --target 95% \\
      --cost-per-rework 7

  # Denial recovery: $500k denied this period, 65% recoverable, assume the
  # industry 60% never-reworked share
  python3 rcm_calc.py denial-recovery --denied 500000 --recoverable 65% \\
      --never-reworked 60%
"""

from __future__ import annotations

import argparse
import sys


def _parse_rate(s: str) -> float:
    """Parse a rate like '95%' or '0.95' into a fraction (0.95)."""
    s = s.strip()
    try:
        return float(s[:-1]) / 100.0 if s.endswith("%") else float(s)
    except ValueError:
        raise argparse.ArgumentTypeError(f"must be like '95%' or '0.95', got {s!r}")


def cmd_ar_days(args: argparse.Namespace) -> int:
    if args.avg_daily_charges <= 0:
        print("error: --avg-daily-charges must be > 0", file=sys.stderr)
        return 2
    if args.ar < 0:
        print("error: --ar must be >= 0", file=sys.stderr)
        return 2

    days = args.ar / args.avg_daily_charges
    print("Days in A/R")
    print(f"  total outstanding A/R    : {args.ar:,.0f}")
    print(f"  average daily charges    : {args.avg_daily_charges:,.0f}")
    print(f"  → DAYS IN A/R            : {days:,.1f}")

    # Benchmark band (public sources; see ../knowledge/rcm-benchmarks-2026.md)
    if days < 30:
        band = "high-performing (<30)"
    elif days <= 40:
        band = "acceptable (31-40 per MGMA/AAFP)"
    else:
        band = "ABOVE benchmark (>40) — read by bucket + payer before acting"
    print(f"  benchmark read           : {band}")

    if args.over_90 is not None:
        if args.over_90 < 0 or args.over_90 > args.ar:
            print("error: --over-90 must be in [0, --ar]", file=sys.stderr)
            return 2
        over_90_pct = (args.over_90 / args.ar * 100.0) if args.ar else 0.0
        print()
        print(f"  A/R over 90 days         : {args.over_90:,.0f}  ({over_90_pct:.1f}% of A/R)")
        target = "OK (<10%)" if over_90_pct < 10.0 else "OVER target (>10%) — concentration to work down"
        print(f"  over-90 vs <10% target   : {target}")
    print("  note: never act on a blended A/R-days number — segment by aging bucket")
    print("        and payer first (§3 #3); the over-90 bucket usually concentrates")
    print("        in a couple of fixable causes (credentialing block, one slow payer).")
    return 0


def cmd_net_collection(args: argparse.Namespace) -> int:
    if args.charges <= 0:
        print("error: --charges must be > 0", file=sys.stderr)
        return 2
    if args.contractual_adjustments < 0:
        print("error: --contractual-adjustments must be >= 0", file=sys.stderr)
        return 2
    allowed = args.charges - args.contractual_adjustments
    if allowed <= 0:
        print("error: charges - contractual-adjustments (the allowed amount) must be > 0",
              file=sys.stderr)
        return 2

    ncr = args.payments / allowed * 100.0
    gcr = args.payments / args.charges * 100.0

    print("Net collection rate (collected against ALLOWED, not gross — §3 #4)")
    print(f"  payments collected       : {args.payments:,.0f}")
    print(f"  gross charges            : {args.charges:,.0f}")
    print(f"  contractual adjustments  : {args.contractual_adjustments:,.0f}")
    print(f"  allowed amount (charges - adjustments) : {allowed:,.0f}")
    print(f"  → NET COLLECTION RATE    : {ncr:.1f}%")
    print(f"    gross collection rate  : {gcr:.1f}%  (vanity number — fee schedules nobody pays)")

    if ncr >= 95.0:
        band = "in benchmark (95-98%+)"
    elif ncr >= 90.0:
        band = "below benchmark (<95%) — decompose by payer before blaming coding"
    else:
        band = "well below benchmark — suspect payer underpayment OR systemic leakage"
    print(f"  benchmark read           : {band}")
    print("  note: a falling NCR with a FLAT coding-denial rate points at the payer")
    print("        side (underpayment vs contracted allowed), not coding (§3 #4, #5).")
    return 0


def cmd_clean_claim(args: argparse.Namespace) -> int:
    if args.claims < 0:
        print("error: --claims must be >= 0", file=sys.stderr)
        return 2
    for name, val in (("--actual", args.actual), ("--target", args.target)):
        if not 0.0 <= val <= 1.0:
            print(f"error: {name} must be in [0%, 100%]", file=sys.stderr)
            return 2

    gap = args.target - args.actual
    print("Clean-claim / first-pass rework cost (every point below target is rework — §3 #2)")
    print(f"  total claims (period)    : {args.claims:,.0f}")
    print(f"  actual first-pass rate   : {args.actual * 100:g}%")
    print(f"  target first-pass rate   : {args.target * 100:g}%")

    if gap <= 0:
        print(f"  → at or above target ({args.actual * 100:g}% >= {args.target * 100:g}%) — no rework gap")
        print("    keep tracking first-pass monthly so a regression surfaces immediately.")
        return 0

    rework_claims = args.claims * gap
    print(f"  gap to target            : {gap * 100:.1f} points")
    print(f"  → REWORK CLAIMS (period) : {rework_claims:,.0f}  (claims needing a second touch)")
    if args.cost_per_rework is not None:
        if args.cost_per_rework < 0:
            print("error: --cost-per-rework must be >= 0", file=sys.stderr)
            return 2
        rework_cost = rework_claims * args.cost_per_rework
        print(f"  cost per rework touch    : {args.cost_per_rework:,.2f}")
        print(f"  → REWORK COST (period)   : {rework_cost:,.0f}")
    print("  note: rework is cost AND delayed cash — it raises cost-to-collect and")
    print("        days-in-A/R together. Trace rejections to the recurring CARC cluster")
    print("        (CO-16 missing info, CO-11 dx/procedure mismatch) and tune the scrubber.")
    return 0


def cmd_denial_recovery(args: argparse.Namespace) -> int:
    if args.denied < 0:
        print("error: --denied must be >= 0", file=sys.stderr)
        return 2
    if not 0.0 <= args.recoverable <= 1.0:
        print("error: --recoverable must be in [0%, 100%]", file=sys.stderr)
        return 2
    if not 0.0 <= args.never_reworked <= 1.0:
        print("error: --never-reworked must be in [0%, 100%]", file=sys.stderr)
        return 2

    recoverable = args.denied * args.recoverable
    lost_if_unworked = recoverable * args.never_reworked

    print("Denial recovery — cash in the unworked queue")
    print(f"  denied dollars (period)  : {args.denied:,.0f}")
    print(f"  recoverable share        : {args.recoverable * 100:g}%")
    print(f"  → RECOVERABLE DOLLARS    : {recoverable:,.0f}")
    print(f"  assumed never-reworked   : {args.never_reworked * 100:g}% of recoverable")
    print(f"  → LOST IF UNWORKED       : {lost_if_unworked:,.0f}")
    print("  note: industry studies report 50-65% of denied claims are never reworked")
    print("        and ~two-thirds are recoverable — but the cheaper win is PREVENTING")
    print("        the denial upstream, not reworking it (§3 #1, #6). Work the queue")
    print("        timely-filing-risk first, then recoverable-dollar-weighted (§3 #3).")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="rcm_calc.py",
        description="Revenue-cycle decision calculator (stdlib only). "
        "Decision-support, not coding/billing/legal advice — validate every input.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    ar = sub.add_parser("ar-days", help="Days in A/R + over-90 bucket flag")
    ar.add_argument("--ar", type=float, required=True,
                    help="total outstanding accounts receivable")
    ar.add_argument("--avg-daily-charges", type=float, required=True,
                    help="average daily charges (e.g. trailing-90-day charges / 90)")
    ar.add_argument("--over-90", type=float, default=None,
                    help="dollars of A/R aged over 90 days (optional; flags vs <10% target)")
    ar.set_defaults(func=cmd_ar_days)

    nc = sub.add_parser("net-collection", help="Net collection rate (vs allowed, not gross)")
    nc.add_argument("--payments", type=float, required=True, help="payments collected")
    nc.add_argument("--charges", type=float, required=True, help="gross charges")
    nc.add_argument("--contractual-adjustments", type=float, required=True,
                    help="contractual adjustments (charges - this = the allowed amount)")
    nc.set_defaults(func=cmd_net_collection)

    cc = sub.add_parser("clean-claim", help="Rework cost of each point below the clean-claim target")
    cc.add_argument("--claims", type=float, required=True, help="total claims in the period")
    cc.add_argument("--actual", type=_parse_rate, required=True,
                    help="actual clean-claim / first-pass rate (e.g. 88%%)")
    cc.add_argument("--target", type=_parse_rate, default=0.95,
                    help="target clean-claim rate (default 95%%)")
    cc.add_argument("--cost-per-rework", type=float, default=None,
                    help="fully-loaded cost per rework touch (optional; e.g. 7)")
    cc.set_defaults(func=cmd_clean_claim)

    dr = sub.add_parser("denial-recovery", help="Recoverable cash in the unworked denial queue")
    dr.add_argument("--denied", type=float, required=True, help="denied dollars in the period")
    dr.add_argument("--recoverable", type=_parse_rate, default=0.66,
                    help="recoverable share of denied dollars (default 66%%)")
    dr.add_argument("--never-reworked", type=_parse_rate, default=0.60,
                    help="share of recoverable that goes unworked (default 60%%)")
    dr.set_defaults(func=cmd_denial_recovery)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
