#!/usr/bin/env python3
"""finops_cloud_cost_calc.py — a zero-dependency FinOps & Cloud Cost decision calculator.

Removes arithmetic error from 3 recurring finops & cloud cost decisions:

  commitment    Blended cost + savings + utilization risk for a coverage level.

  unit-cost     Cost per unit and the trend vs a prior period.

  rightsizing   Monthly savings from rightsizing to real utilization.

This is a CALCULATOR, not a data source — it does not fetch benchmarks or live
data. The user supplies every input; the tool does the arithmetic and shows the
formula. Stdlib only (argparse); runs anywhere Python 3.8+ is present.

IMPORTANT: outputs are decision-support, not professional/legal/regulatory/
financial advice (see ../CLAUDE.md S2). Validate every figure against the
client's actual data; route every professional determination to the qualified
authority. No billing/account PII belongs in any input or output.
"""
from __future__ import annotations

import argparse
import sys

DISCLAIMER = (
    "Decision-support only — not professional/legal/regulatory/financial advice. "
    "Validate every input against the client's actual data; route professional "
    "determinations to the qualified authority (CLAUDE.md S2). No billing/account PII."
)


def _pct(x):
    return f"{x * 100:.1f}%"


def _money(x):
    return f"${x:,.0f}"


def cmd_commitment(a):
    if not (0 <= a.coverage <= 1) or not (0 <= a.discount < 1) or not (0 < a.utilization <= 1):
        print("error: 0<=coverage<=1, 0<=discount<1, 0<utilization<=1", file=sys.stderr)
        return 2
    if a.on_demand_spend < 0:
        print("error: --on-demand-spend must be >= 0", file=sys.stderr)
        return 2
    committed_spend = a.on_demand_spend * a.coverage
    on_demand_left = a.on_demand_spend * (1 - a.coverage)
    committed_cost = committed_spend * (1 - a.discount)
    blended = committed_cost + on_demand_left
    savings = a.on_demand_spend - blended
    locked_waste = committed_spend * (1 - a.utilization)
    print("=== Commitment portfolio (CLAUDE.md S3 #3) ===")
    print(f"  On-demand spend     : {_money(a.on_demand_spend)}")
    print(f"  Coverage            : {_pct(a.coverage)}")
    print(f"  Discount            : {_pct(a.discount)}")
    print(f"  Expected utilization: {_pct(a.utilization)}")
    print(f"  Committed cost      : {_money(committed_cost)}  (on {_money(committed_spend)} covered)")
    print(f"  On-demand remaining : {_money(on_demand_left)}")
    print(f"  >> Blended cost     : {_money(blended)}")
    print(f"  >> Gross savings    : {_money(savings)}")
    print(f"  >> Locked-in waste risk (if utilization holds): {_money(locked_waste)}")
    if locked_waste > savings:
        print("  >> WARNING: utilization risk exceeds savings — lower coverage (S3 #3)")
    print("  NOTE: discount is [unverified - training knowledge]; verify vs live pricing (S3 #8).")
    print(f"\n  {DISCLAIMER}")
    return 0

def cmd_unit_cost(a):
    if a.units <= 0:
        print("error: --units > 0", file=sys.stderr)
        return 2
    if a.allocated_cost < 0:
        print("error: --allocated-cost must be >= 0", file=sys.stderr)
        return 2
    cpu = a.allocated_cost / a.units
    print("=== Unit economics (CLAUDE.md S3 #2) ===")
    print(f"  Allocated cost      : {_money(a.allocated_cost)}")
    print(f"  Units               : {a.units:,.0f}")
    print(f"  >> Cost per unit    : {_money(cpu)}")
    if a.prior_cost and a.prior_units > 0:
        prior_cpu = a.prior_cost / a.prior_units
        delta = cpu - prior_cpu
        bill_delta = a.allocated_cost - a.prior_cost
        print(f"  Prior cost per unit : {_money(prior_cpu)}")
        direction = "UP" if delta > 0 else "down"
        print(f"  >> Unit cost {direction} by {_money(abs(delta))} ({_pct(abs(delta)/prior_cpu)})")
        if bill_delta > 0 and delta <= 0:
            print("  >> Healthy scaling: bill rose but cost-per-unit held/fell (S3 #2)")
        elif delta > 0:
            print("  >> Decay risk: cost-per-unit rising — attribute the driving service (S3 #2)")
    print(f"\n  {DISCLAIMER}")
    return 0

def cmd_rightsizing(a):
    if not (0 < a.utilization <= 1) or not (0 < a.target_utilization <= 1):
        print("error: 0 < utilization <= 1 and 0 < target-utilization <= 1", file=sys.stderr)
        return 2
    if a.current_monthly < 0:
        print("error: --current-monthly must be >= 0", file=sys.stderr)
        return 2
    implied_fraction = a.utilization / a.target_utilization
    if implied_fraction > 1:
        implied_fraction = 1.0
    implied_cost = a.current_monthly * implied_fraction
    savings = a.current_monthly - implied_cost
    print("=== Rightsizing (CLAUDE.md S3 #4 #5) ===")
    print(f"  Current monthly     : {_money(a.current_monthly)}")
    print(f"  Observed utilization: {_pct(a.utilization)}")
    print(f"  Target utilization  : {_pct(a.target_utilization)}  (leave headroom)")
    print(f"  >> Implied size cost: {_money(implied_cost)}  ({_pct(implied_fraction)} of current)")
    if savings > 0:
        print(f"  >> Monthly savings  : {_money(savings)}  ({_money(savings*12)}/yr)")
        print("  >> Rightsize BEFORE committing — don't lock in this oversize (S3 #4)")
    else:
        print("  >> Already right-sized for the target headroom — no rightsizing savings")
    print(f"\n  {DISCLAIMER}")
    return 0


def build_parser():
    p = argparse.ArgumentParser(
        prog='finops_cloud_cost_calc.py',
        description="FinOps & Cloud Cost decision calculator (stdlib only). Decision-support, not advice.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser('commitment', help='on-demand spend, coverage %, discount -> blended cost + savings')
    sp.add_argument('--on-demand-spend', type=float, required=True, help='total eligible on-demand spend $ (per period)')
    sp.add_argument('--coverage', type=float, required=True, help='commitment coverage fraction (0-1)')
    sp.add_argument('--discount', type=float, required=True, help='commitment discount fraction (0-1)')
    sp.add_argument('--utilization', type=float, default=1.0, help='expected commitment utilization (0-1)')
    sp.set_defaults(func=cmd_commitment)

    sp = sub.add_parser('unit-cost', help='allocated cost / units -> cost per unit + trend')
    sp.add_argument('--allocated-cost', type=float, required=True, help='allocated cost this period $')
    sp.add_argument('--units', type=float, required=True, help='units this period (customers/txns/features)')
    sp.add_argument('--prior-cost', type=float, default=0.0, help='allocated cost prior period $')
    sp.add_argument('--prior-units', type=float, default=0.0, help='units prior period')
    sp.set_defaults(func=cmd_unit_cost)

    sp = sub.add_parser('rightsizing', help='current vs utilization-implied size -> monthly savings')
    sp.add_argument('--current-monthly', type=float, required=True, help='current monthly cost of the resource $')
    sp.add_argument('--utilization', type=float, required=True, help='observed peak utilization (0-1)')
    sp.add_argument('--target-utilization', type=float, default=0.7, help='target utilization headroom (0-1)')
    sp.set_defaults(func=cmd_rightsizing)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
