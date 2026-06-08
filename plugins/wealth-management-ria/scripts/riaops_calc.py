#!/usr/bin/env python3
"""riaops_calc.py — a zero-dependency Wealth Management (RIA Practice) decision calculator.

Removes arithmetic error from 3 recurring wealth management (ria practice) decisions:

  aum-revenue   Tiered-fee revenue, blended fee, and net-new vs market growth.

  advisor-capacityHouseholds per advisor vs a target capacity band.

  client-profitabilityClient revenue vs cost-to-serve: margin + breakeven AUM.

This is a CALCULATOR, not a data source — it does not fetch benchmarks or live
data. The user supplies every input; the tool does the arithmetic and shows the
formula. Stdlib only (argparse); runs anywhere Python 3.8+ is present.

IMPORTANT: outputs are decision-support, not professional/legal/regulatory/
financial advice (see ../CLAUDE.md S2). Validate every figure against the
client's actual data; route every professional determination to the qualified
authority. No client financial PII belongs in any input or output.
"""
from __future__ import annotations

import argparse
import sys

DISCLAIMER = (
    "Decision-support only — not professional/legal/regulatory/financial advice. "
    "Validate every input against the client's actual data; route professional "
    "determinations to the qualified authority (CLAUDE.md S2). No client financial PII."
)


def _pct(x):
    return f"{x * 100:.1f}%"


def _money(x):
    return f"${x:,.0f}"


def cmd_aum_revenue(a):
    if a.beginning_aum <= 0:
        print("error: --beginning-aum > 0", file=sys.stderr)
        return 2
    if not (0 <= a.blended_fee < 1):
        print("error: 0 <= --blended-fee < 1", file=sys.stderr)
        return 2
    aum_growth = a.ending_aum - a.beginning_aum
    market_growth = aum_growth - a.net_new_flows
    organic_rate = a.net_new_flows / a.beginning_aum
    revenue = a.ending_aum * a.blended_fee
    print("=== AUM revenue + organic vs market (CLAUDE.md S3 #1/#7) ===")
    print(f"  Beginning AUM       : {_money(a.beginning_aum)}")
    print(f"  Ending AUM          : {_money(a.ending_aum)}")
    print(f"  Total AUM growth    : {_money(aum_growth)}")
    print(f"  Net new flows       : {_money(a.net_new_flows)}  (growth the practice EARNED)")
    print(f"  Market appreciation : {_money(market_growth)}  (NOT earned growth, S3 #1)")
    print(f"  >> Organic growth   : {_pct(organic_rate)}  (net new flows / beginning AUM = real health metric, S3 #7)")
    print(f"  Revenue @ {_pct(a.blended_fee)} blended fee: {_money(revenue)}")
    if organic_rate <= 0:
        print("  >> Organically FLAT/SHRINKING — AUM rise was market; only organic survives a drawdown (S3 #7)")
    print(f"\n  {DISCLAIMER}")
    return 0

def cmd_advisor_capacity(a):
    if a.advisors <= 0 or a.target_per_advisor <= 0:
        print("error: --advisors > 0 and --target-per-advisor > 0", file=sys.stderr)
        return 2
    per_advisor = a.households / a.advisors
    utilization = per_advisor / a.target_per_advisor
    print("=== Advisor capacity (CLAUDE.md S3 #4) ===")
    print(f"  Households          : {a.households:,.0f}")
    print(f"  Advisors            : {a.advisors:g}")
    print(f"  Target/advisor      : {a.target_per_advisor:,.0f}  [unverified — calibrate to service model, S3 #8]")
    print(f"  >> Households/advisor: {per_advisor:,.1f}")
    print(f"  >> Capacity utilization: {_pct(utilization)}")
    if utilization > 1.0:
        extra = a.households - a.target_per_advisor * a.advisors
        print(f"  >> OVER capacity by ~{extra:,.0f} households — leading retention + cadence risk (S3 #4 #5)")
    elif utilization < 0.7:
        print("  >> UNDER capacity — room to add households or consolidate advisors")
    else:
        print("  >> Within a healthy capacity band")
    print(f"\n  {DISCLAIMER}")
    return 0

def cmd_client_profitability(a):
    if a.aum <= 0 or not (0 < a.effective_fee < 1):
        print("error: --aum > 0 and 0 < --effective-fee < 1", file=sys.stderr)
        return 2
    if a.cost_to_serve < 0:
        print("error: --cost-to-serve >= 0", file=sys.stderr)
        return 2
    revenue = a.aum * a.effective_fee
    margin = revenue - a.cost_to_serve
    breakeven_aum = a.cost_to_serve / a.effective_fee
    print("=== Client profitability (CLAUDE.md S3 #2) ===")
    print(f"  Client AUM          : {_money(a.aum)}")
    print(f"  Effective fee       : {_pct(a.effective_fee)}")
    print(f"  Revenue             : {_money(revenue)}")
    print(f"  Cost to serve       : {_money(a.cost_to_serve)}")
    print(f"  >> Client margin    : {_money(margin)}  ({_pct(margin/revenue) if revenue else 0} of revenue)")
    print(f"  >> Breakeven AUM    : {_money(breakeven_aum)}  (cost / effective fee)")
    if margin < 0:
        print("  >> BELOW breakeven — re-price, re-tier, or right-size service (rank by margin not AUM, S3 #2)")
    else:
        print("  >> Profitable — protect retention + capacity (S3 #4 #5)")
    print(f"\n  {DISCLAIMER}")
    return 0


def build_parser():
    p = argparse.ArgumentParser(
        prog='riaops_calc.py',
        description="Wealth Management (RIA Practice) decision calculator (stdlib only). Decision-support, not advice.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser('aum-revenue', help='revenue from tiered fee + separate organic (net new) from market growth')
    sp.add_argument('--beginning-aum', type=float, required=True, help='beginning AUM $')
    sp.add_argument('--ending-aum', type=float, required=True, help='ending AUM $')
    sp.add_argument('--net-new-flows', type=float, required=True, help='net new flows (new money - withdrawals) $')
    sp.add_argument('--blended-fee', type=float, default=0.01, help='blended advisory fee (0-1) for revenue')
    sp.set_defaults(func=cmd_aum_revenue)

    sp = sub.add_parser('advisor-capacity', help='households / advisors vs target; over-capacity = retention risk')
    sp.add_argument('--households', type=float, required=True, help='total households served')
    sp.add_argument('--advisors', type=float, required=True, help='number of client-facing advisors')
    sp.add_argument('--target-per-advisor', type=float, default=100.0, help='target households per advisor')
    sp.set_defaults(func=cmd_advisor_capacity)

    sp = sub.add_parser('client-profitability', help='margin = revenue - cost-to-serve; breakeven AUM = cost / effective fee')
    sp.add_argument('--aum', type=float, required=True, help='client AUM $')
    sp.add_argument('--effective-fee', type=float, required=True, help='client effective fee (0-1)')
    sp.add_argument('--cost-to-serve', type=float, required=True, help='annual cost to serve the client $')
    sp.set_defaults(func=cmd_client_profitability)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
