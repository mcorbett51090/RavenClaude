#!/usr/bin/env python3
"""mortgage_lending_calc.py — a zero-dependency Mortgage Lending Operations decision calculator.

Removes arithmetic error from 3 recurring mortgage lending operations decisions:

  pullthrough   Pull-through funnel + the worst fallout stage.

  cycle-capacityMonthly capacity from cycle time + the bottleneck.

  cost-to-originateCost-to-originate + breakeven volume.

This is a CALCULATOR, not a data source — it does not fetch benchmarks or live
data. The user supplies every input; the tool does the arithmetic and shows the
formula. Stdlib only (argparse); runs anywhere Python 3.8+ is present.

IMPORTANT: outputs are decision-support, not professional/legal/regulatory/
financial advice (see ../CLAUDE.md S2). Validate every figure against the
client's actual data; route every professional determination to the qualified
authority. No borrower PII / NPI belongs in any input or output.
"""
from __future__ import annotations

import argparse
import sys

DISCLAIMER = (
    "Decision-support only — not professional/legal/regulatory/financial advice. "
    "Validate every input against the client's actual data; route professional "
    "determinations to the qualified authority (CLAUDE.md S2). No borrower PII / NPI."
)


def _pct(x):
    return f"{x * 100:.1f}%"


def _money(x):
    return f"${x:,.0f}"


def cmd_pullthrough(a):
    rates = {"app->approved": a.app_to_approved, "approved->CTC": a.approved_to_ctc, "CTC->funded": a.ctc_to_funded}
    for n, r in rates.items():
        if not (0 < r <= 1):
            print(f"error: {n} must be in (0,1]", file=sys.stderr)
            return 2
    if a.apps <= 0:
        print("error: --apps must be > 0", file=sys.stderr)
        return 2
    approved = a.apps * a.app_to_approved
    ctc = approved * a.approved_to_ctc
    funded = ctc * a.ctc_to_funded
    pull_through = funded / a.apps
    print("=== Pull-through funnel (CLAUDE.md S3 #1) ===")
    print(f"  Applications        : {a.apps:,.0f}")
    print(f"  -> Approved         : {approved:,.0f}  (app->approved {_pct(a.app_to_approved)})")
    print(f"  -> Clear-to-close   : {ctc:,.0f}  (approved->CTC {_pct(a.approved_to_ctc)})")
    print(f"  -> Funded           : {funded:,.0f}  (CTC->funded {_pct(a.ctc_to_funded)})")
    print(f"  >> Pull-through     : {_pct(pull_through)}  (funded / apps)")
    worst = min(rates, key=rates.get)
    print(f"  >> Worst fallout    : '{worst}' at {_pct(rates[worst])} — fix BEFORE buying more apps (S3 #1)")
    print(f"\n  {DISCLAIMER}")
    return 0

def cmd_cycle_capacity(a):
    if a.cycle_days <= 0 or a.processors <= 0 or a.baseline_cycle_days <= 0:
        print("error: --cycle-days, --processors, --baseline-cycle-days must be > 0", file=sys.stderr)
        return 2
    loans_per_processor = a.concurrent_loans * (a.baseline_cycle_days / a.cycle_days)
    monthly_capacity = a.processors * loans_per_processor
    print("=== Cycle -> capacity (CLAUDE.md S3 #2/#4) ===")
    print(f"  Cycle time          : {a.cycle_days:g} days  (baseline {a.baseline_cycle_days:g})")
    print(f"  Processors          : {a.processors:g}")
    print(f"  Concurrent loans@base: {a.concurrent_loans:g}")
    print(f"  >> Loans/processor  : {loans_per_processor:,.1f}  (falls as cycle lengthens)")
    print(f"  >> Monthly capacity : {monthly_capacity:,.1f} loans")
    if a.pipeline > 0:
        gap = a.pipeline - monthly_capacity
        if gap > 0:
            print(f"  Pipeline            : {a.pipeline:,.0f} loans")
            print(f"  >> SHORT by {gap:,.1f} loans — staff to the cycle, not a fixed ratio (S3 #4)")
        else:
            print(f"  Pipeline            : {a.pipeline:,.0f} loans")
            print(f"  >> Capacity covers pipeline (slack {abs(gap):,.1f} loans)")
    print("  NOTE: plan capacity for the rate swing/breakeven, not the last peak (S3 #7).")
    print(f"\n  {DISCLAIMER}")
    return 0

def cmd_cost_to_originate(a):
    if a.loans <= 0:
        print("error: --loans must be > 0", file=sys.stderr)
        return 2
    total_cost = a.fixed_cost + a.variable_cost * a.loans
    cost_to_originate = total_cost / a.loans
    print("=== Cost-to-originate (CLAUDE.md S3 #5/#7) ===")
    print(f"  Fixed cost          : {_money(a.fixed_cost)}")
    print(f"  Variable cost/loan  : {_money(a.variable_cost)}")
    print(f"  Funded loans        : {a.loans:,.0f}")
    print(f"  >> Cost-to-originate: {_money(cost_to_originate)} / loan")
    if a.revenue_per_loan > 0:
        margin = a.revenue_per_loan - a.variable_cost
        if margin <= 0:
            print(f"  Revenue/loan        : {_money(a.revenue_per_loan)}")
            print("  >> Variable margin <= 0 — every loan loses money before fixed cost (S3 #5)")
        else:
            breakeven = a.fixed_cost / margin
            print(f"  Revenue/loan        : {_money(a.revenue_per_loan)}")
            print(f"  Contribution margin : {_money(margin)} / loan")
            print(f"  >> Breakeven volume : {breakeven:,.1f} loans/period — the rate swing must clear this (S3 #7)")
            if a.loans < breakeven:
                print(f"  >> BELOW breakeven by {breakeven - a.loans:,.1f} loans — not covering fixed cost")
    else:
        print("  NOTE: pass --revenue-per-loan to compute the breakeven volume (S3 #5 #7).")
    print(f"\n  {DISCLAIMER}")
    return 0


def build_parser():
    p = argparse.ArgumentParser(
        prog='mortgage_lending_calc.py',
        description="Mortgage Lending Operations decision calculator (stdlib only). Decision-support, not advice.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser('pullthrough', help='funded from chained stage rates + the worst fallout stage')
    sp.add_argument('--apps', type=float, required=True, help='applications in the cohort')
    sp.add_argument('--app-to-approved', type=float, required=True, help='app->approved rate (0-1)')
    sp.add_argument('--approved-to-ctc', type=float, required=True, help='approved->clear-to-close rate (0-1)')
    sp.add_argument('--ctc-to-funded', type=float, required=True, help='clear-to-close->funded rate (0-1)')
    sp.set_defaults(func=cmd_pullthrough)

    sp = sub.add_parser('cycle-capacity', help='loans-per-processor falls with cycle; monthly capacity vs pipeline')
    sp.add_argument('--cycle-days', type=float, required=True, help='avg app-to-close cycle in days')
    sp.add_argument('--processors', type=float, required=True, help='number of processors')
    sp.add_argument('--concurrent-loans', type=float, required=True, help='loans a processor handles concurrently at a baseline cycle')
    sp.add_argument('--baseline-cycle-days', type=float, default=30.0, help='the cycle at which concurrent-loans holds')
    sp.add_argument('--pipeline', type=float, default=0.0, help='open pipeline loans to clear this month')
    sp.set_defaults(func=cmd_cycle_capacity)

    sp = sub.add_parser('cost-to-originate', help='(fixed + variable x loans) / loans; breakeven = fixed / margin')
    sp.add_argument('--fixed-cost', type=float, required=True, help='fixed cost for the period $')
    sp.add_argument('--variable-cost', type=float, required=True, help='variable cost per funded loan $')
    sp.add_argument('--loans', type=float, required=True, help='funded loans in the period')
    sp.add_argument('--revenue-per-loan', type=float, default=0.0, help='revenue per funded loan $ (for breakeven)')
    sp.set_defaults(func=cmd_cost_to_originate)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
