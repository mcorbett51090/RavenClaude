#!/usr/bin/env python3
"""property_management_calc.py — a zero-dependency Property Management Operations decision calculator.

Removes arithmetic error from 3 recurring property management operations decisions:

  noi           EGI-to-NOI bridge with optional cap-rate value.

  occupancy-rev Ending occupancy + revenue from the move-in/out flow.

  turn-time     Lost rent during unit turns, annualized.

This is a CALCULATOR, not a data source — it does not fetch benchmarks or live
data. The user supplies every input; the tool does the arithmetic and shows the
formula. Stdlib only (argparse); runs anywhere Python 3.8+ is present.

IMPORTANT: outputs are decision-support, not professional/legal/regulatory/
financial advice (see ../CLAUDE.md S2). Validate every figure against the
client's actual data; route every professional determination to the qualified
authority. No tenant PII belongs in any input or output.
"""
from __future__ import annotations

import argparse
import sys

DISCLAIMER = (
    "Decision-support only — not professional/legal/regulatory/financial advice. "
    "Validate every input against the client's actual data; route professional "
    "determinations to the qualified authority (CLAUDE.md S2). No tenant PII."
)


def _pct(x):
    return f"{x * 100:.1f}%"


def _money(x):
    return f"${x:,.0f}"


def cmd_noi(a):
    if a.gross_potential_rent <= 0:
        print("error: --gross-potential-rent > 0", file=sys.stderr)
        return 2
    egi = a.gross_potential_rent - a.vacancy_loss + a.other_income
    noi = egi - a.operating_expense
    econ_occ = egi / a.gross_potential_rent if a.gross_potential_rent else 0
    print("=== NOI bridge (CLAUDE.md S3 #4) ===")
    print(f"  Gross potential rent : {_money(a.gross_potential_rent)}")
    print(f"  Vacancy + loss       : -{_money(a.vacancy_loss)}")
    print(f"  Other income         : +{_money(a.other_income)}")
    print(f"  >> Effective gross income (EGI): {_money(egi)}  (economic occ {_pct(econ_occ)})")
    print(f"  Operating expense    : -{_money(a.operating_expense)}  (capex sits below the line, S3 #7)")
    print(f"  >> NOI               : {_money(noi)}")
    if a.cap_rate > 0:
        value = noi / a.cap_rate
        print(f"  Cap rate             : {_pct(a.cap_rate)}  (source + date it, S3 #8)")
        print(f"  >> Implied value     : {_money(value)}  (NOI / cap rate)")
    print(f"\n  {DISCLAIMER}")
    return 0

def cmd_occupancy_rev(a):
    if a.total_units <= 0:
        print("error: --total-units > 0", file=sys.stderr)
        return 2
    if not (0 < a.target_occupancy <= 1):
        print("error: 0 < --target-occupancy <= 1", file=sys.stderr)
        return 2
    end_occupied = a.start_occupied + a.move_ins - a.move_outs
    end_occupied = max(0.0, min(end_occupied, a.total_units))
    end_occ = end_occupied / a.total_units
    revenue = end_occupied * a.avg_rent
    target_units = a.target_occupancy * a.total_units
    gap_units = target_units - end_occupied
    print("=== Occupancy + revenue (CLAUDE.md S3 #1) ===")
    print(f"  Start occupied       : {a.start_occupied:g}")
    print(f"  Move-ins / move-outs : +{a.move_ins:g} / -{a.move_outs:g}  (net {a.move_ins - a.move_outs:+g})")
    print(f"  >> End occupied      : {end_occupied:g} of {a.total_units:g} units")
    print(f"  >> End occupancy     : {_pct(end_occ)}")
    print(f"  >> Monthly revenue   : {_money(revenue)}  (occupied x avg rent)")
    print(f"  Target occupancy     : {_pct(a.target_occupancy)} ({target_units:g} units)")
    if gap_units > 0:
        print(f"  >> SHORT by {gap_units:.1f} units ({_money(gap_units * a.avg_rent)}/mo) of target — manage the funnel + renewals (S3 #1 #6)")
    else:
        print(f"  >> At/above target (surplus {abs(gap_units):.1f} units)")
    print(f"\n  {DISCLAIMER}")
    return 0

def cmd_turn_time(a):
    if a.turn_days <= 0 or a.daily_rent <= 0:
        print("error: --turn-days > 0 and --daily-rent > 0", file=sys.stderr)
        return 2
    lost_per_cycle = a.vacant_units * a.turn_days * a.daily_rent
    turns_per_year = 365.0 / a.turn_days
    annualized = lost_per_cycle * turns_per_year
    day_value = a.vacant_units * a.daily_rent
    print("=== Unit-turn lost rent (CLAUDE.md S3 #3) ===")
    print(f"  Vacant units         : {a.vacant_units:g}")
    print(f"  Avg turn days        : {a.turn_days:g}")
    print(f"  Daily rent/unit      : {_money(a.daily_rent)}")
    print(f"  >> Lost rent this turn cycle : {_money(lost_per_cycle)}")
    print(f"  >> Each turn day costs       : {_money(day_value)} across these units")
    print(f"  >> Annualized drag at this cadence: {_money(annualized)}  ({turns_per_year:.1f} turns/yr)")
    print("  NOTE: this rent never bills and shows on NO maintenance cost line (S3 #3).")
    print(f"\n  {DISCLAIMER}")
    return 0


def build_parser():
    p = argparse.ArgumentParser(
        prog='property_management_calc.py',
        description="Property Management Operations decision calculator (stdlib only). Decision-support, not advice.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser('noi', help='GPR - vacancy/loss + other income - opex => EGI + NOI (+ value)')
    sp.add_argument('--gross-potential-rent', type=float, required=True, help='gross potential rent $')
    sp.add_argument('--vacancy-loss', type=float, required=True, help='vacancy + loss-to-lease + concessions + bad debt $')
    sp.add_argument('--other-income', type=float, required=True, help='other income $ (fees, parking, etc.)')
    sp.add_argument('--operating-expense', type=float, required=True, help='operating expense $ (excl. capex)')
    sp.add_argument('--cap-rate', type=float, default=0.0, help='market cap rate (0-1) for value')
    sp.set_defaults(func=cmd_noi)

    sp = sub.add_parser('occupancy-rev', help='start occupied + move-ins - move-outs => end occupancy %, revenue, gap to target')
    sp.add_argument('--start-occupied', type=float, required=True, help='units occupied at period start')
    sp.add_argument('--move-ins', type=float, required=True, help='move-ins in the period')
    sp.add_argument('--move-outs', type=float, required=True, help='move-outs in the period')
    sp.add_argument('--total-units', type=float, required=True, help='total units')
    sp.add_argument('--avg-rent', type=float, required=True, help='average monthly rent per unit $')
    sp.add_argument('--target-occupancy', type=float, default=0.95, help='target occupancy (0-1)')
    sp.set_defaults(func=cmd_occupancy_rev)

    sp = sub.add_parser('turn-time', help='vacant units x turn days x daily rent => lost rent + annualized drag')
    sp.add_argument('--vacant-units', type=float, required=True, help='vacant units awaiting/under turn')
    sp.add_argument('--turn-days', type=float, required=True, help='average turn days (move-out to rent-ready)')
    sp.add_argument('--daily-rent', type=float, required=True, help='daily rent per unit $')
    sp.set_defaults(func=cmd_turn_time)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
