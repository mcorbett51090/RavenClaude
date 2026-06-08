#!/usr/bin/env python3
"""acctgops_calc.py — a zero-dependency Accounting & Bookkeeping Practice decision calculator.

Removes arithmetic error from 3 recurring accounting & bookkeeping practice decisions:

  working-capitalCash conversion cycle: DSO + DIO - DPO.

  aging         AR aging buckets -> weighted bad-debt estimate.

  close-cycle   Critical-path days-to-close + bottleneck task.

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


def cmd_working_capital(a):
    if a.revenue <= 0 or a.cogs <= 0 or a.days <= 0:
        print("error: --revenue > 0, --cogs > 0, --days > 0", file=sys.stderr)
        return 2
    dso = a.ar / a.revenue * a.days
    dpo = a.ap / a.cogs * a.days
    dio = a.inventory / a.cogs * a.days if a.inventory else 0.0
    ccc = dso + dio - dpo
    print("=== Cash conversion cycle (CLAUDE.md S3 #3/#4) ===")
    print("  NOTE: state the basis (accrual vs cash) — it changes the picture (S3 #6)")
    print(f"  DSO                 : {dso:,.1f} days  (AR / revenue x days)")
    print(f"  DIO                 : {dio:,.1f} days  (inventory / COGS x days)")
    print(f"  DPO                 : {dpo:,.1f} days  (AP / COGS x days)")
    print(f"  >> Cash conv. cycle : {ccc:,.1f} days  (DSO + DIO - DPO; lower frees cash)")
    if dso > dpo:
        print("  >> Cash trapped in AR vs financed by AP — collections is the lever (S3 #3)")
    print(f"\n  {DISCLAIMER}")
    return 0

def cmd_aging(a):
    buckets = [("current", a.current, 0.005), ("1-30", a.b30, 0.02), ("31-60", a.b60, 0.10),
               ("61-90", a.b90, 0.25), ("90+", a.b90plus, 0.50)]
    for name, bal, _ in buckets:
        if bal < 0:
            print(f"error: {name} balance must be >= 0", file=sys.stderr)
            return 2
    total_ar = sum(b for _, b, _ in buckets)
    bad_debt = sum(b * r for _, b, r in buckets)
    print("=== AR aging + weighted bad-debt (CLAUDE.md S3 #3) ===")
    print("  (illustrative loss rates [unverified] — calibrate to client history, S3 #8)")
    for name, bal, rate in buckets:
        print(f"  {name:<8} {_money(bal):>14}  x {_pct(rate)} loss = {_money(bal*rate)}")
    print(f"  Total AR            : {_money(total_ar)}")
    print(f"  >> Weighted bad-debt: {_money(bad_debt)}  ({_pct(bad_debt/total_ar) if total_ar else 0} of AR)")
    print("  >> AR is cash already earned but not collected (S3 #3)")
    print(f"\n  {DISCLAIMER}")
    return 0

def cmd_close_cycle(a):
    if a.critical_path_days <= 0 or a.bottleneck_days < 0:
        print("error: --critical-path-days > 0 and --bottleneck-days >= 0", file=sys.stderr)
        return 2
    if a.bottleneck_days > a.critical_path_days:
        print("error: --bottleneck-days cannot exceed --critical-path-days", file=sys.stderr)
        return 2
    print("=== Critical-path days-to-close (CLAUDE.md S3 #1) ===")
    print(f"  Critical-path days  : {a.critical_path_days:,.1f}  (longest dependent chain = days-to-close)")
    print(f"  Bottleneck task     : {a.bottleneck_days:,.1f} days  ({_pct(a.bottleneck_days/a.critical_path_days)} of the path)")
    print(f"  Target days-to-close: {a.target_days:,.1f}")
    if a.parallel_days:
        print(f"  Longest parallel run: {a.parallel_days:,.1f} days  (off the critical path)")
    gap = a.critical_path_days - a.target_days
    if gap > 0:
        print(f"  >> OVER target by {gap:,.1f} days — attack the bottleneck, parallelize the rest (S3 #1)")
    else:
        print(f"  >> Within target (margin {abs(gap):,.1f} days)")
    print("  >> Reconciliation gates the close — books can't close un-reconciled (S3 #2)")
    print(f"\n  {DISCLAIMER}")
    return 0


def build_parser():
    p = argparse.ArgumentParser(
        prog='acctgops_calc.py',
        description="Accounting & Bookkeeping Practice decision calculator (stdlib only). Decision-support, not advice.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser('working-capital', help='DSO, DPO, DIO -> cash conversion cycle (state the basis)')
    sp.add_argument('--ar', type=float, required=True, help='accounts receivable balance $')
    sp.add_argument('--revenue', type=float, required=True, help='revenue for the period $')
    sp.add_argument('--ap', type=float, required=True, help='accounts payable balance $')
    sp.add_argument('--cogs', type=float, required=True, help='cost of goods sold for the period $')
    sp.add_argument('--inventory', type=float, default=0.0, help='inventory balance $')
    sp.add_argument('--days', type=float, default=365.0, help='days in the period')
    sp.set_defaults(func=cmd_working_capital)

    sp = sub.add_parser('aging', help='weighted bad-debt = Sum(bucket x loss rate)')
    sp.add_argument('--current', type=float, required=True, help='current bucket balance $')
    sp.add_argument('--b30', type=float, required=True, help='1-30 days past due $')
    sp.add_argument('--b60', type=float, required=True, help='31-60 days past due $')
    sp.add_argument('--b90', type=float, required=True, help='61-90 days past due $')
    sp.add_argument('--b90plus', type=float, required=True, help='90+ days past due $')
    sp.set_defaults(func=cmd_aging)

    sp = sub.add_parser('close-cycle', help='critical-path days = longest dependent chain; flag the bottleneck')
    sp.add_argument('--critical-path-days', type=float, required=True, help='sum of durations along the longest dependent task chain (days)')
    sp.add_argument('--bottleneck-days', type=float, required=True, help='duration of the single longest critical-path task (days)')
    sp.add_argument('--target-days', type=float, default=5.0, help='days-to-close target')
    sp.add_argument('--parallel-days', type=float, default=0.0, help='longest NON-critical task chain (days), for comparison')
    sp.set_defaults(func=cmd_close_cycle)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
