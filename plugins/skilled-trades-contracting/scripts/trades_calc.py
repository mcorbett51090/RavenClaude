#!/usr/bin/env python3
"""trades_calc.py — a zero-dependency skilled-trades-contracting decision calculator.

Removes arithmetic error from four recurring contracting-economics decisions a
trade-contractor owner / estimator / operations manager runs constantly:

  job-margin      Reconcile one job's ACTUAL gross margin against the estimate.
                  Takes the bid price plus actual labor hours x loaded rate,
                  material (with waste), subcontractor cost, and uncaptured
                  change-order scope, and prints estimated-vs-actual gross
                  margin, the dollar variance, and which bucket drove the gap.
                  Pairs with knowledge/trades-decision-trees.md (the post-
                  completion losing-money tree) and templates/job-cost-worksheet.md.

  markup         Convert a target gross MARGIN into the MARKUP you must apply to
                  cost, and show the margin you actually get from a given markup.
                  This is the #1 contractor pricing error: applying a markup
                  equal to the desired margin (a 20% markup yields only a 16.7%
                  margin). Pairs with knowledge/trades-markup-vs-margin-decision-tree.md.

  loaded-rate    Build the fully-loaded (billable) labor rate from base wage +
                  labor burden + the per-billable-hour share of overhead, then
                  apply billable-hour efficiency so the rate is recovered on the
                  hours you can actually sell. Pairs with §3 #1 / #3 and
                  skills/build-the-loaded-rate/SKILL.md.

  overhead-rate  Compute the overhead recovery markup (overhead / direct cost)
                  AND the revenue-based overhead ratio, so a bid carries its
                  share of overhead before any profit is added. Pairs with
                  best-practices/overhead-allocation-rate-must-be-built-before-pricing-any-job.md.

This is a CALCULATOR, not a data source — it does not fetch wages, material
prices, or live benchmarks. The user supplies every input; the tool does the
arithmetic and shows the formula. Stdlib only (argparse); runs anywhere Python
3.8+ is present.

IMPORTANT: outputs are decision-support, not licensed financial, accounting, or
legal advice (see ../CLAUDE.md §2). Validate every figure against the contractor's
actual job-cost and P&L data before any deliverable (CLAUDE.md §3 #8).

Examples
--------
  # Job margin: $12,000 bid, 60 actual hours at a $95 loaded rate, $3,400 material
  # (incl. waste), $1,200 sub cost, and $800 of scope added without a change order
  python3 trades_calc.py job-margin --bid 12000 --hours 60 --loaded-rate 95 \\
      --material 3400 --sub 1200 --uncaptured-change-order 800 --target-margin 35%

  # Markup vs margin: what markup yields a 35% margin? what margin does a 35% markup give?
  python3 trades_calc.py markup --target-margin 35% --applied-markup 35%

  # Loaded labor rate: $28 base wage, 32% burden, $145k annual overhead over
  # 5 billable techs, 1,500 billable hours/tech/yr, 65% billable efficiency
  python3 trades_calc.py loaded-rate --wage 28 --burden 32% --annual-overhead 145000 \\
      --techs 5 --billable-hours 1500 --efficiency 65%

  # Overhead recovery: $145k overhead against $900k of direct job cost
  python3 trades_calc.py overhead-rate --annual-overhead 145000 --direct-cost 900000 \\
      --revenue 1200000
"""

from __future__ import annotations

import argparse
import sys


def _parse_rate(s: str) -> float:
    """Parse a rate like '35%' or '0.35' into a fraction (0.35)."""
    s = s.strip()
    try:
        return float(s[:-1]) / 100.0 if s.endswith("%") else float(s)
    except ValueError:
        raise argparse.ArgumentTypeError(f"must be like '35%' or '0.35', got {s!r}")


def _margin_from_markup(markup: float) -> float:
    """Gross margin (fraction of price) implied by a markup (fraction of cost)."""
    return markup / (1.0 + markup)


def _markup_from_margin(margin: float) -> float:
    """Markup (fraction of cost) required to achieve a target margin (fraction of price)."""
    return margin / (1.0 - margin)


def cmd_job_margin(args: argparse.Namespace) -> int:
    if args.bid <= 0:
        print("error: --bid must be > 0", file=sys.stderr)
        return 2

    labor = args.hours * args.loaded_rate
    direct_cost = labor + args.material + args.sub
    gross_profit = args.bid - direct_cost
    margin = gross_profit / args.bid

    print("Job gross-margin reconciliation (estimate vs actual)")
    print(f"  bid (contract) price     : {args.bid:,.0f}")
    print(f"  actual labor             : {labor:,.0f} ({args.hours:g} h x {args.loaded_rate:,.2f}/h loaded)")
    print(f"  material (incl. waste)   : {args.material:,.0f}")
    print(f"  subcontractor cost       : {args.sub:,.0f}")
    print(f"  = total direct cost      : {direct_cost:,.0f}")
    print(f"  = gross profit           : {gross_profit:,.0f}")
    print(f"  = gross margin           : {margin * 100:.1f}% of price")

    if args.target_margin is not None:
        target_profit = args.bid * args.target_margin
        variance = gross_profit - target_profit
        print()
        print(f"  target gross margin      : {args.target_margin * 100:g}%  ({target_profit:,.0f} target profit)")
        verdict = "ABOVE target" if variance >= 0 else "BELOW target"
        print(f"  → margin variance        : {variance:,.0f}  ({verdict})")

    if args.uncaptured_change_order > 0:
        # Scope delivered for free: cost incurred, no price collected.
        recovered_margin = (gross_profit + args.uncaptured_change_order) / args.bid
        print()
        print(f"  uncaptured change-order scope: {args.uncaptured_change_order:,.0f} of work delivered with no price")
        print(f"  → margin had this been billed : {recovered_margin * 100:.1f}% "
              f"(+{(recovered_margin - margin) * 100:.1f} pts)")
        print("    a callback/extra delivered free is a margin leak, not a goodwill gesture (§3 #4).")

    print("  note: compare to the ESTIMATE's assumed hours/material — the bucket with the")
    print("        biggest unfavorable variance is the driver. Run the post-completion tree.")
    return 0


def cmd_markup(args: argparse.Namespace) -> int:
    print("Markup vs margin (the contractor pricing trap)")
    print("  margin = profit / PRICE ;  markup = profit / COST  — they are NOT equal")
    print()

    if args.target_margin is not None:
        if not 0.0 <= args.target_margin < 1.0:
            print("error: --target-margin must be in [0%, 100%)", file=sys.stderr)
            return 2
        needed_markup = _markup_from_margin(args.target_margin)
        print(f"  to HIT a {args.target_margin * 100:g}% margin you must apply a "
              f"{needed_markup * 100:.1f}% markup on cost")
        print(f"    (price = cost x {1.0 + needed_markup:.4f})")

    if args.applied_markup is not None:
        if args.applied_markup < 0.0:
            print("error: --applied-markup must be >= 0%", file=sys.stderr)
            return 2
        got_margin = _margin_from_markup(args.applied_markup)
        print(f"  a {args.applied_markup * 100:g}% markup actually YIELDS a "
              f"{got_margin * 100:.1f}% margin")
        if args.target_margin is not None:
            shortfall = args.target_margin - got_margin
            if abs(shortfall) > 1e-9:
                print(f"    → applying {args.applied_markup * 100:g}% markup when you wanted a "
                      f"{args.target_margin * 100:g}% margin leaves you {shortfall * 100:.1f} pts short")

    if args.target_margin is None and args.applied_markup is None:
        print("error: supply --target-margin and/or --applied-markup", file=sys.stderr)
        return 2

    print("  note: a markup table built off the margin you actually want is the fix (§3 #2, #5).")
    return 0


def cmd_loaded_rate(args: argparse.Namespace) -> int:
    if args.techs < 1:
        print("error: --techs must be >= 1", file=sys.stderr)
        return 2
    if args.billable_hours <= 0:
        print("error: --billable-hours must be > 0", file=sys.stderr)
        return 2
    if not 0.0 < args.efficiency <= 1.0:
        print("error: --efficiency must be in (0%, 100%]", file=sys.stderr)
        return 2

    burdened_wage = args.wage * (1.0 + args.burden)
    sellable_hours = args.billable_hours * args.efficiency
    total_sellable = sellable_hours * args.techs
    overhead_per_hour = args.annual_overhead / total_sellable if total_sellable else 0.0
    loaded_rate = burdened_wage + overhead_per_hour

    print("Fully-loaded (billable) labor rate")
    print(f"  base wage                : {args.wage:,.2f}/h")
    print(f"  + labor burden           : {args.burden * 100:g}%  → burdened wage {burdened_wage:,.2f}/h")
    print(f"  billable hours/tech/yr   : {args.billable_hours:,.0f} at {args.efficiency * 100:g}% efficiency "
          f"= {sellable_hours:,.0f} SELLABLE h/tech")
    print(f"  techs                    : {args.techs}  → {total_sellable:,.0f} total sellable h/yr")
    print(f"  annual overhead          : {args.annual_overhead:,.0f}  → {overhead_per_hour:,.2f}/sellable h")
    print(f"  = LOADED LABOR RATE      : {loaded_rate:,.2f}/h  (cost floor, before profit)")
    print("  note: this is the COST floor — the rate must absorb wage+burden+overhead before")
    print("        a dollar of profit (§3 #1). Add margin via the markup mode, not by guessing.")
    return 0


def cmd_overhead_rate(args: argparse.Namespace) -> int:
    if args.direct_cost <= 0:
        print("error: --direct-cost must be > 0", file=sys.stderr)
        return 2

    overhead_markup = args.annual_overhead / args.direct_cost

    print("Overhead recovery rate")
    print(f"  annual overhead          : {args.annual_overhead:,.0f}")
    print(f"  annual direct job cost   : {args.direct_cost:,.0f}")
    print(f"  → OVERHEAD MARKUP        : {overhead_markup * 100:.1f}% of direct cost")
    print("    (add this to every bid's direct cost just to break even on overhead)")

    if args.revenue is not None:
        if args.revenue <= 0:
            print("error: --revenue must be > 0", file=sys.stderr)
            return 2
        overhead_ratio = args.annual_overhead / args.revenue
        print(f"  overhead as % of revenue : {overhead_ratio * 100:.1f}%")
        print("    (top performers often run overhead at ~8-12% of revenue [verify-at-use])")

    print("  note: an understated overhead markup is silent margin loss — every job ships short")
    print("        by the gap. Rebuild this BEFORE pricing, not when a job loses money (§3 #1).")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="trades_calc.py",
        description="Skilled-trades-contracting decision calculator (stdlib only). "
        "Decision-support, not financial/accounting advice — validate every input.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    jm = sub.add_parser("job-margin", help="Reconcile a job's actual vs estimated gross margin")
    jm.add_argument("--bid", type=float, required=True, help="bid / contract price for the job")
    jm.add_argument("--hours", type=float, required=True, help="actual labor hours on the job")
    jm.add_argument("--loaded-rate", type=float, required=True, help="fully-loaded labor rate per hour")
    jm.add_argument("--material", type=float, default=0.0, help="material cost incl. waste")
    jm.add_argument("--sub", type=float, default=0.0, help="subcontractor cost")
    jm.add_argument("--uncaptured-change-order", type=float, default=0.0,
                    help="value of scope delivered with no change order (margin leak)")
    jm.add_argument("--target-margin", type=_parse_rate, default=None,
                    help="target gross margin to compare against (e.g. 35%%)")
    jm.set_defaults(func=cmd_job_margin)

    mk = sub.add_parser("markup", help="Convert target margin <-> applied markup")
    mk.add_argument("--target-margin", type=_parse_rate, default=None,
                    help="gross margin you want (e.g. 35%%)")
    mk.add_argument("--applied-markup", type=_parse_rate, default=None,
                    help="markup you are applying to cost (e.g. 35%%)")
    mk.set_defaults(func=cmd_markup)

    lr = sub.add_parser("loaded-rate", help="Build the fully-loaded billable labor rate")
    lr.add_argument("--wage", type=float, required=True, help="base hourly wage")
    lr.add_argument("--burden", type=_parse_rate, required=True,
                    help="labor burden as a fraction of wage (taxes, insurance, benefits; e.g. 32%%)")
    lr.add_argument("--annual-overhead", type=float, required=True, help="total annual overhead to recover")
    lr.add_argument("--techs", type=int, required=True, help="number of billable technicians")
    lr.add_argument("--billable-hours", type=float, required=True,
                    help="scheduled billable hours per tech per year (before efficiency)")
    lr.add_argument("--efficiency", type=_parse_rate, default=1.0,
                    help="billable-hour efficiency (sellable / scheduled; default 100%%)")
    lr.set_defaults(func=cmd_loaded_rate)

    oh = sub.add_parser("overhead-rate", help="Overhead recovery markup + revenue ratio")
    oh.add_argument("--annual-overhead", type=float, required=True, help="total annual overhead")
    oh.add_argument("--direct-cost", type=float, required=True, help="annual direct job cost (labor+material+sub)")
    oh.add_argument("--revenue", type=float, default=None, help="annual revenue (optional, for the ratio)")
    oh.set_defaults(func=cmd_overhead_rate)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
