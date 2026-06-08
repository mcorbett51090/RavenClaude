#!/usr/bin/env python3
"""automotive_dealership_calc.py — a zero-dependency Automotive Dealership Operations decision calculator.

Removes arithmetic error from 3 recurring automotive dealership operations decisions:

  days-supply   Inventory days-supply + monthly floorplan carrying cost.

  absorption    Service absorption rate vs total fixed overhead.

  gross-per-unitTotal gross (front + back) per unit + F&I penetration.

This is a CALCULATOR, not a data source — it does not fetch benchmarks or live
data. The user supplies every input; the tool does the arithmetic and shows the
formula. Stdlib only (argparse); runs anywhere Python 3.8+ is present.

IMPORTANT: outputs are decision-support, not professional/legal/regulatory/
financial advice (see ../CLAUDE.md S2). Validate every figure against the
client's actual data; route every professional determination to the qualified
authority. No customer PII belongs in any input or output.
"""
from __future__ import annotations

import argparse
import sys

DISCLAIMER = (
    "Decision-support only — not professional/legal/regulatory/financial advice. "
    "Validate every input against the client's actual data; route professional "
    "determinations to the qualified authority (CLAUDE.md S2). No customer PII."
)


def _pct(x):
    return f"{x * 100:.1f}%"


def _money(x):
    return f"${x:,.0f}"


def cmd_days_supply(a):
    if a.daily_sales_rate <= 0:
        print("error: --daily-sales-rate > 0", file=sys.stderr)
        return 2
    if a.target_days_supply <= 0:
        print("error: --target-days-supply > 0", file=sys.stderr)
        return 2
    days_supply = a.units_in_stock / a.daily_sales_rate
    monthly_carry = a.units_in_stock * a.per_unit_daily_carry * 30.0
    target_units = a.target_days_supply * a.daily_sales_rate
    excess_units = a.units_in_stock - target_units
    print("=== Inventory days-supply (CLAUDE.md S3 #2) ===")
    print(f"  Units in stock       : {a.units_in_stock:g}")
    print(f"  Daily sales rate     : {a.daily_sales_rate:g}/day")
    print(f"  >> Days-supply       : {days_supply:.1f} days  (target {a.target_days_supply:g})")
    print(f"  Per-unit daily carry : {_money(a.per_unit_daily_carry)}")
    print(f"  >> Monthly floorplan carry: {_money(monthly_carry)}  (carrying-cost cash, S3 #2)")
    if excess_units > 0:
        print(f"  >> OVER target by {excess_units:.1f} units ({_money(excess_units * a.per_unit_daily_carry * 30.0)}/mo extra carry) — price-to-turn aged units")
    else:
        print(f"  >> At/under target (room for {abs(excess_units):.1f} more units)")
    print(f"\n  {DISCLAIMER}")
    return 0

def cmd_absorption(a):
    if a.total_fixed_expense <= 0:
        print("error: --total-fixed-expense > 0", file=sys.stderr)
        return 2
    absorption = a.fixed_ops_gross / a.total_fixed_expense
    gap = a.total_fixed_expense - a.fixed_ops_gross
    print("=== Service absorption (CLAUDE.md S3 #5) ===")
    print(f"  Fixed-ops gross      : {_money(a.fixed_ops_gross)}  (service + parts)")
    print(f"  Total fixed overhead : {_money(a.total_fixed_expense)}")
    print(f"  >> Absorption rate   : {_pct(absorption)}")
    if absorption >= 1.0:
        print(f"  >> AT/ABOVE 100% — store self-covers overhead; variable ops is pure upside (surplus {_money(-gap)})")
    else:
        print(f"  >> BELOW 100% — showroom must cover {_money(gap)} of overhead: structural fragility (S3 #1 #5)")
    print(f"\n  {DISCLAIMER}")
    return 0

def cmd_gross_per_unit(a):
    if a.units <= 0:
        print("error: --units > 0", file=sys.stderr)
        return 2
    total_per_unit = a.front_gross_per_unit + a.fi_back_per_unit
    total_gross = total_per_unit * a.units
    front_total = a.front_gross_per_unit * a.units
    back_total = a.fi_back_per_unit * a.units
    back_share = a.fi_back_per_unit / total_per_unit if total_per_unit else 0
    print("=== Total gross per unit (CLAUDE.md S3 #3) ===")
    print(f"  Units retailed       : {a.units:g}")
    print(f"  Front gross/unit     : {_money(a.front_gross_per_unit)}  (total {_money(front_total)})")
    print(f"  F&I back/unit (PVR)  : {_money(a.fi_back_per_unit)}  (total {_money(back_total)})")
    print(f"  >> Total gross/unit  : {_money(total_per_unit)}")
    print(f"  >> Total gross       : {_money(total_gross)}")
    print(f"  >> Back-end share of total gross: {_pct(back_share)}  (the F&I lever, S3 #4)")
    print("  NOTE: manage front + back together; keep F&I inside compliance — counsel's call (S3 #4 / S2).")
    print(f"\n  {DISCLAIMER}")
    return 0


def build_parser():
    p = argparse.ArgumentParser(
        prog='automotive_dealership_calc.py',
        description="Automotive Dealership Operations decision calculator (stdlib only). Decision-support, not advice.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser('days-supply', help='units / daily sales rate => days-supply + monthly floorplan carry')
    sp.add_argument('--units-in-stock', type=float, required=True, help='units in stock')
    sp.add_argument('--daily-sales-rate', type=float, required=True, help='average units sold per day')
    sp.add_argument('--per-unit-daily-carry', type=float, required=True, help='floorplan carry per unit per day $')
    sp.add_argument('--target-days-supply', type=float, default=45.0, help='target days-supply')
    sp.set_defaults(func=cmd_days_supply)

    sp = sub.add_parser('absorption', help='fixed-ops gross / total fixed overhead => absorption % + flag')
    sp.add_argument('--fixed-ops-gross', type=float, required=True, help='service + parts gross profit $')
    sp.add_argument('--total-fixed-expense', type=float, required=True, help='total fixed overhead $')
    sp.set_defaults(func=cmd_absorption)

    sp = sub.add_parser('gross-per-unit', help='(front + F&I back) x units => total gross, per-unit, F&I penetration')
    sp.add_argument('--front-gross-per-unit', type=float, required=True, help='front (vehicle) gross per unit $')
    sp.add_argument('--fi-back-per-unit', type=float, required=True, help='F&I back-end gross per unit $')
    sp.add_argument('--units', type=float, required=True, help='units retailed in the period')
    sp.set_defaults(func=cmd_gross_per_unit)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
