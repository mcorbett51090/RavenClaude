#!/usr/bin/env python3
"""fleet_calc.py — a zero-dependency fleet & logistics decision calculator.

Removes arithmetic error from four recurring fleet-economics decisions a fleet
owner / operations manager / cost analyst runs constantly:

  cost-per-mile   Builds ALL-IN cost-per-mile BOTTOM-UP from a fixed monthly
                  cost block (truck/trailer payment, insurance, permits,
                  overhead) plus per-mile variable costs (fuel via price/MPG,
                  driver pay, maintenance, tires, tolls), at a stated monthly
                  utilization. Prints the fixed CPM, variable CPM, all-in CPM,
                  and — if a rate is supplied — the per-mile and monthly margin
                  against it. Pairs with knowledge/fleet-economics.md and the
                  build-cost-per-mile skill. CPM is the master number (§3 #1).

  deadhead        Quantifies the empty-mile leak: revenue lost to deadhead at a
                  given empty-mile %, the loaded-mile ratio, and the all-in cost
                  burned running empty. Shows the dollar value of pulling
                  deadhead down by a target number of points (the backhaul
                  prize). Pairs with knowledge/fleet-decision-trees.md and the
                  reduce-deadhead skill (§3 #3).

  replace-repair  The keep-vs-replace crossover for one unit: trailing
                  maintenance CPM (incl. an optional unplanned-downtime cost)
                  vs. the ownership CPM of a replacement (payment + insurance
                  amortized over projected miles). Prints the per-mile gap, a
                  verdict, and the annual-dollar swing. Pairs with the Fleet —
                  Truck Replacement Timing tree and the lease-vs-buy-vs-rent
                  tree (knowledge/fleet-lease-vs-buy-vs-rent-decision-tree.md).

  turnover        The unit-economics of driver turnover: annual replacement
                  cost = drivers x turnover-rate x cost-per-replacement, plus
                  the unseated-truck revenue lost while each seat is empty.
                  Shows the annual dollar saved by cutting turnover by a target
                  number of points (the retention prize). Pairs with the
                  quantify-driver-retention skill (§3 #4).

This is a CALCULATOR, not a data source — it does not fetch benchmarks, rates,
fuel prices, or live costs. The user supplies every input; the tool does the
arithmetic and shows the formula. Stdlib only (argparse); runs anywhere Python
3.8+ is present.

IMPORTANT: outputs are decision-support, not legal, safety, or licensed
financial advice (see ../CLAUDE.md §2). The team is not a DOT/FMCSA authority
and does not rule on hours-of-service. Validate every figure against the
fleet's actual data before any deliverable (CLAUDE.md §3 #8).

Examples
--------
  # Cost-per-mile: $6,500/mo fixed, 10,000 mi/mo, diesel $3.90 @ 6.5 mpg,
  # $0.70/mi driver pay, $0.20/mi maintenance, $0.05/mi tires, vs a $2.40 rate
  python3 fleet_calc.py cost-per-mile --fixed-monthly 6500 --miles 10000 \
      --fuel-price 3.90 --mpg 6.5 --driver-pay 0.70 --maintenance 0.20 \
      --tires 0.05 --rate 2.40

  # Deadhead leak: 100,000 mi/mo at 22% deadhead, $2.26 all-in CPM,
  # $2.40 avg loaded rate, modelling a 7-point reduction
  python3 fleet_calc.py deadhead --total-miles 100000 --deadhead 22% \
      --cpm 2.26 --rate 2.40 --target-reduction 7

  # Replace vs repair: unit at $0.42/mi maintenance + 8% downtime on
  # $700/day, vs a replacement at $2,000/mo payment + $110/mo insurance
  # over 9,000 mi/mo
  python3 fleet_calc.py replace-repair --maintenance-cpm 0.42 \
      --downtime-rate 8% --downtime-day-cost 700 --miles 9000 \
      --replacement-payment 2000 --replacement-insurance 110

  # Turnover: 50 drivers, 90% annual turnover, $12,000/replacement,
  # 6 days unseated at $900/day, modelling a 20-point reduction
  python3 fleet_calc.py turnover --drivers 50 --turnover 90% \
      --cost-per-replacement 12000 --unseated-days 6 --unseated-day-cost 900 \
      --target-reduction 20
"""

from __future__ import annotations

import argparse
import sys


def _parse_rate(s: str) -> float:
    """Parse a rate like '22%' or '0.22' into a fraction (0.22)."""
    s = s.strip()
    try:
        return float(s[:-1]) / 100.0 if s.endswith("%") else float(s)
    except ValueError:
        raise argparse.ArgumentTypeError(f"must be like '22%' or '0.22', got {s!r}")


def cmd_cost_per_mile(args: argparse.Namespace) -> int:
    if args.miles <= 0:
        print("error: --miles must be > 0", file=sys.stderr)
        return 2
    if args.mpg <= 0:
        print("error: --mpg must be > 0", file=sys.stderr)
        return 2

    fuel_cpm = args.fuel_price / args.mpg
    variable_cpm = (
        fuel_cpm
        + args.driver_pay
        + args.maintenance
        + args.tires
        + args.tolls
    )
    fixed_cpm = args.fixed_monthly / args.miles
    all_in_cpm = fixed_cpm + variable_cpm

    print("Cost-per-mile — built bottom-up")
    print(f"  monthly miles            : {args.miles:,.0f}")
    print(f"  fixed monthly cost       : {args.fixed_monthly:,.0f}")
    print(f"  fuel                     : {args.fuel_price:,.2f}/gal / {args.mpg:g} mpg "
          f"= {fuel_cpm:,.3f}/mi")
    print(f"  driver pay               : {args.driver_pay:,.3f}/mi")
    print(f"  maintenance              : {args.maintenance:,.3f}/mi")
    print(f"  tires                    : {args.tires:,.3f}/mi")
    print(f"  tolls/other variable     : {args.tolls:,.3f}/mi")
    print("  ------")
    print(f"  → fixed CPM              : {fixed_cpm:,.3f}/mi ({args.fixed_monthly:,.0f} / {args.miles:,.0f} mi)")
    print(f"  → variable CPM           : {variable_cpm:,.3f}/mi")
    print(f"  → ALL-IN CPM             : {all_in_cpm:,.3f}/mi")

    if args.rate is not None:
        margin_cpm = args.rate - all_in_cpm
        monthly_margin = margin_cpm * args.miles
        verdict = "PROFIT" if margin_cpm > 0 else "LOSS"
        print()
        print(f"  against a {args.rate:,.2f}/mi rate:")
        print(f"    margin/mile            : {margin_cpm:,.3f}/mi  ({verdict})")
        print(f"    margin/month           : {monthly_margin:,.0f}")
        if margin_cpm <= 0:
            print("    note: rate is below all-in CPM — every mile loses money (§3 #6).")
    print("  note: fixed CPM swings with utilization — re-run at your REAL miles/mo,")
    print("        not a target. CPM is the master number; build it bottom-up (§3 #1).")
    return 0


def cmd_deadhead(args: argparse.Namespace) -> int:
    if args.total_miles <= 0:
        print("error: --total-miles must be > 0", file=sys.stderr)
        return 2
    if not 0.0 <= args.deadhead < 1.0:
        print("error: --deadhead must be in [0%, 100%)", file=sys.stderr)
        return 2

    empty_miles = args.total_miles * args.deadhead
    loaded_miles = args.total_miles - empty_miles
    loaded_ratio = loaded_miles / args.total_miles
    cost_burned = empty_miles * args.cpm

    print("Deadhead — the empty-mile leak")
    print(f"  total miles              : {args.total_miles:,.0f}")
    print(f"  deadhead rate            : {args.deadhead * 100:g}%")
    print(f"  empty miles              : {empty_miles:,.0f}")
    print(f"  loaded miles             : {loaded_miles:,.0f}")
    print(f"  loaded-mile ratio        : {loaded_ratio * 100:,.1f}%")
    print(f"  all-in CPM               : {args.cpm:,.3f}/mi")
    print(f"  → cost burned running empty : {cost_burned:,.0f}")
    if args.rate is not None:
        forgone_revenue = empty_miles * args.rate
        print(f"  → revenue forgone if those miles were loaded @ {args.rate:,.2f}/mi : "
              f"{forgone_revenue:,.0f}")

    if args.target_reduction is not None:
        if args.target_reduction <= 0:
            print("error: --target-reduction must be > 0 (points)", file=sys.stderr)
            return 2
        recovered_miles = args.total_miles * (args.target_reduction / 100.0)
        recovered_miles = min(recovered_miles, empty_miles)
        cost_saving = recovered_miles * args.cpm
        print()
        print(f"  cutting deadhead by {args.target_reduction:g} points:")
        print(f"    empty miles avoided    : {recovered_miles:,.0f}")
        print(f"    cost saving            : {cost_saving:,.0f}")
        if args.rate is not None:
            revenue_added = recovered_miles * args.rate
            print(f"    + backhaul revenue if reloaded @ {args.rate:,.2f}/mi : {revenue_added:,.0f}")
        print("    note: backhaul fills the gap before a rate conversation (§3 #3).")
    return 0


def cmd_replace_repair(args: argparse.Namespace) -> int:
    if args.miles <= 0:
        print("error: --miles must be > 0", file=sys.stderr)
        return 2
    if not 0.0 <= args.downtime_rate < 1.0:
        print("error: --downtime-rate must be in [0%, 100%)", file=sys.stderr)
        return 2

    # Approximate working days the unit is available per month from miles is
    # not derivable; the downtime cost is modelled per WORKING DAY supplied.
    downtime_cpm = (args.downtime_rate * args.downtime_day_cost * args.working_days) / args.miles
    keep_cpm = args.maintenance_cpm + downtime_cpm

    replacement_monthly = args.replacement_payment + args.replacement_insurance
    replacement_cpm = replacement_monthly / args.miles

    gap = keep_cpm - replacement_cpm
    annual_swing = gap * args.miles * 12
    verdict = "REPLACE" if gap > 0 else "KEEP"

    print("Replace vs. repair — per-mile crossover for one unit")
    print(f"  monthly miles            : {args.miles:,.0f}")
    print(f"  keep — maintenance CPM   : {args.maintenance_cpm:,.3f}/mi")
    print(f"  keep — downtime          : {args.downtime_rate * 100:g}% x "
          f"{args.downtime_day_cost:,.0f}/day x {args.working_days:g} days "
          f"= {downtime_cpm:,.3f}/mi")
    print(f"  → KEEP all-in CPM        : {keep_cpm:,.3f}/mi")
    print(f"  replace — payment+ins/mo : {replacement_monthly:,.0f} "
          f"({args.replacement_payment:,.0f} + {args.replacement_insurance:,.0f})")
    print(f"  → REPLACE ownership CPM  : {replacement_cpm:,.3f}/mi")
    print("  ------")
    print(f"  → per-mile gap (keep − replace) : {gap:,.3f}/mi")
    print(f"  → annual swing           : {annual_swing:,.0f}")
    print(f"  → VERDICT                : {verdict}")
    print("  note: this is the COST crossover only. Confirm with the replacement-timing")
    print("        tree — downtime % and a near-term major repair can move the call (§3 #5).")
    return 0


def cmd_turnover(args: argparse.Namespace) -> int:
    if args.drivers <= 0:
        print("error: --drivers must be > 0", file=sys.stderr)
        return 2
    if not 0.0 <= args.turnover <= 5.0:
        print("error: --turnover must be a sane rate (e.g. 90% or 0.90)", file=sys.stderr)
        return 2

    annual_separations = args.drivers * args.turnover
    replacement_cost = annual_separations * args.cost_per_replacement
    unseated_cost = annual_separations * args.unseated_days * args.unseated_day_cost
    total_annual = replacement_cost + unseated_cost

    print("Driver turnover — annual unit economics")
    print(f"  drivers                  : {args.drivers:,.0f}")
    print(f"  annual turnover rate     : {args.turnover * 100:g}%")
    print(f"  annual separations       : {annual_separations:,.1f}")
    print(f"  cost per replacement     : {args.cost_per_replacement:,.0f} "
          "(recruiting + screening + training)")
    print(f"  → direct replacement cost: {replacement_cost:,.0f}")
    print(f"  unseated-truck cost      : {args.unseated_days:g} days x "
          f"{args.unseated_day_cost:,.0f}/day per seat")
    print(f"  → unseated-truck cost    : {unseated_cost:,.0f}")
    print("  ------")
    print(f"  → TOTAL annual turnover cost : {total_annual:,.0f}")

    if args.target_reduction is not None:
        if args.target_reduction <= 0:
            print("error: --target-reduction must be > 0 (points)", file=sys.stderr)
            return 2
        new_rate = max(args.turnover - args.target_reduction / 100.0, 0.0)
        new_separations = args.drivers * new_rate
        new_total = (
            new_separations * args.cost_per_replacement
            + new_separations * args.unseated_days * args.unseated_day_cost
        )
        saving = total_annual - new_total
        print()
        print(f"  cutting turnover by {args.target_reduction:g} points "
              f"({args.turnover * 100:g}% → {new_rate * 100:g}%):")
        print(f"    new annual cost        : {new_total:,.0f}")
        print(f"    → annual saving        : {saving:,.0f}")
        print("    note: turnover is a margin lever, not HR overhead (§3 #4).")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="fleet_calc.py",
        description="Fleet & logistics decision calculator (stdlib only). "
        "Decision-support, not legal/safety/financial advice — validate every input.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    cpm = sub.add_parser("cost-per-mile", help="Build all-in cost-per-mile bottom-up")
    cpm.add_argument("--fixed-monthly", type=float, required=True,
                     help="fixed monthly cost block (payment, insurance, permits, overhead)")
    cpm.add_argument("--miles", type=float, required=True, help="monthly miles run")
    cpm.add_argument("--fuel-price", type=float, required=True, help="fuel price per gallon")
    cpm.add_argument("--mpg", type=float, required=True, help="miles per gallon")
    cpm.add_argument("--driver-pay", type=float, default=0.0, help="driver pay per mile")
    cpm.add_argument("--maintenance", type=float, default=0.0, help="maintenance cost per mile")
    cpm.add_argument("--tires", type=float, default=0.0, help="tire cost per mile")
    cpm.add_argument("--tolls", type=float, default=0.0, help="tolls/other variable per mile")
    cpm.add_argument("--rate", type=float, default=None,
                     help="revenue per mile for a margin readout (optional)")
    cpm.set_defaults(func=cmd_cost_per_mile)

    dh = sub.add_parser("deadhead", help="Quantify the deadhead/empty-mile leak")
    dh.add_argument("--total-miles", type=float, required=True, help="total miles (loaded + empty)")
    dh.add_argument("--deadhead", type=_parse_rate, required=True,
                    help="deadhead/empty-mile rate (e.g. 22%)")
    dh.add_argument("--cpm", type=float, required=True, help="all-in cost per mile")
    dh.add_argument("--rate", type=float, default=None,
                    help="avg loaded rate per mile for a revenue readout (optional)")
    dh.add_argument("--target-reduction", type=float, default=None,
                    help="points to cut deadhead by, for the saving (optional)")
    dh.set_defaults(func=cmd_deadhead)

    rr = sub.add_parser("replace-repair", help="Keep-vs-replace per-mile crossover for one unit")
    rr.add_argument("--maintenance-cpm", type=float, required=True,
                    help="trailing maintenance cost per mile for the unit")
    rr.add_argument("--miles", type=float, required=True, help="monthly miles for the unit")
    rr.add_argument("--downtime-rate", type=_parse_rate, default=0.0,
                    help="unplanned-downtime rate (fraction of working days, e.g. 8%)")
    rr.add_argument("--downtime-day-cost", type=float, default=0.0,
                    help="cost of one downtime day (lost load + repair + driver)")
    rr.add_argument("--working-days", type=float, default=22.0,
                    help="working days per month (default 22)")
    rr.add_argument("--replacement-payment", type=float, required=True,
                    help="replacement monthly payment/lease")
    rr.add_argument("--replacement-insurance", type=float, default=0.0,
                    help="replacement incremental monthly insurance")
    rr.set_defaults(func=cmd_replace_repair)

    to = sub.add_parser("turnover", help="Annual driver-turnover cost + retention prize")
    to.add_argument("--drivers", type=float, required=True, help="number of driver seats")
    to.add_argument("--turnover", type=_parse_rate, required=True,
                    help="annual turnover rate (e.g. 90%)")
    to.add_argument("--cost-per-replacement", type=float, required=True,
                    help="cost to replace one driver (recruiting + screening + training)")
    to.add_argument("--unseated-days", type=float, default=0.0,
                    help="days a truck sits unseated per separation")
    to.add_argument("--unseated-day-cost", type=float, default=0.0,
                    help="lost revenue per unseated-truck day")
    to.add_argument("--target-reduction", type=float, default=None,
                    help="points to cut turnover by, for the saving (optional)")
    to.set_defaults(func=cmd_turnover)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
