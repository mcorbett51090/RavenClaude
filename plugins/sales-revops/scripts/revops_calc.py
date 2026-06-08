#!/usr/bin/env python3
"""revops_calc.py — a zero-dependency Sales & Revenue Operations decision calculator.

Removes arithmetic error from 5 recurring sales & revenue operations decisions:

  coverage      Pipeline coverage vs the win-rate-implied requirement.

  forecast      Stage-weighted forecast with a slip/age haircut.

  funnel        Stage conversions + the leaking stage.

  velocity      Sales velocity across its four levers.

  quota-capacityQuota fit against ramped-rep capacity.

This is a CALCULATOR, not a data source — it does not fetch benchmarks or live
data. The user supplies every input; the tool does the arithmetic and shows the
formula. Stdlib only (argparse); runs anywhere Python 3.8+ is present.

IMPORTANT: outputs are decision-support, not professional/legal/regulatory/
financial advice (see ../CLAUDE.md S2). Validate every figure against the
client's actual data; route every professional determination to the qualified
authority. No customer/rep PII belongs in any input or output.
"""
from __future__ import annotations

import argparse
import sys

DISCLAIMER = (
    "Decision-support only — not professional/legal/regulatory/financial advice. "
    "Validate every input against the client's actual data; route professional "
    "determinations to the qualified authority (CLAUDE.md S2). No customer/rep PII."
)


def _pct(x):
    return f"{x * 100:.1f}%"


def _money(x):
    return f"${x:,.0f}"


def cmd_coverage(a):
    if a.remaining_quota <= 0 or not (0 < a.win_rate <= 1):
        print("error: --remaining-quota > 0 and 0 < --win-rate <= 1", file=sys.stderr)
        return 2
    required = 1.0 / a.win_rate
    ratio = a.open_pipeline / a.remaining_quota
    gap = (required - ratio) * a.remaining_quota
    print("=== Pipeline coverage (CLAUDE.md S3 #1) ===")
    print(f"  Open pipeline       : {_money(a.open_pipeline)}")
    print(f"  Remaining quota     : {_money(a.remaining_quota)}")
    print(f"  Win-rate            : {_pct(a.win_rate)}")
    print(f"  Required coverage   : {required:.2f}x  (1 / win-rate)")
    print(f"  Actual coverage     : {ratio:.2f}x  (pipeline / quota)")
    if gap > 0:
        print(f"  >> SHORT by {_money(gap)} of pipeline to hit the required ratio")
    else:
        print(f"  >> Coverage adequate (surplus {_money(-gap)})")
    print(f"\n  {DISCLAIMER}")
    return 0

def cmd_forecast(a):
    if not (0 <= a.aging_haircut < 1):
        print("error: 0 <= --aging-haircut < 1", file=sys.stderr)
        return 2
    slip_adj = a.weighted_pipeline * (1 - a.aging_haircut)
    print("=== Stage-weighted forecast (CLAUDE.md S3 #2/#6) ===")
    print(f"  Weighted pipeline   : {_money(a.weighted_pipeline)}  (Sum value x stage win-rate)")
    print(f"  Aging haircut       : {_pct(a.aging_haircut)}")
    print(f"  >> Slip-adjusted forecast: {_money(slip_adj)}")
    if a.committed:
        delta = a.committed - slip_adj
        print(f"  Rep-committed total : {_money(a.committed)}")
        flag = "ABOVE" if delta > 0 else "below"
        print(f"  >> Commits run {_money(abs(delta))} {flag} the weighted+aged model "
              f"({_pct(abs(delta)/a.committed) if a.committed else 0}) — commits are an input, not the model")
    print(f"\n  {DISCLAIMER}")
    return 0

def cmd_funnel(a):
    rates = {"lead->qual": a.qual, "qual->demo": a.demo, "demo->proposal": a.proposal, "proposal->close": a.close}
    for n, r in rates.items():
        if not (0 < r <= 1):
            print(f"error: {n} must be in (0,1]", file=sys.stderr)
            return 2
    proposals = a.target_wins / a.close
    demos = proposals / a.proposal
    quals = demos / a.demo
    leads = quals / a.qual
    print("=== Funnel: required pipeline + leak (CLAUDE.md S3 #3) ===")
    print(f"  Target wins         : {a.target_wins:g}")
    print(f"  Required proposals  : {proposals:,.0f}  (close {_pct(a.close)})")
    print(f"  Required demos      : {demos:,.0f}  (demo->proposal {_pct(a.proposal)})")
    print(f"  Required quals      : {quals:,.0f}  (qual->demo {_pct(a.demo)})")
    print(f"  Required leads      : {leads:,.0f}  (lead->qual {_pct(a.qual)})")
    worst = min(rates, key=rates.get)
    print(f"  >> Leaking stage    : '{worst}' at {_pct(rates[worst])} — fix BEFORE adding leads (S3 #3)")
    print(f"\n  {DISCLAIMER}")
    return 0

def cmd_velocity(a):
    if a.cycle_days <= 0 or not (0 < a.win_rate <= 1):
        print("error: --cycle-days > 0 and 0 < --win-rate <= 1", file=sys.stderr)
        return 2
    vel = (a.open_deals * a.win_rate * a.acv) / a.cycle_days
    print("=== Sales velocity (CLAUDE.md S3 #3) ===")
    print(f"  Open deals          : {a.open_deals:g}")
    print(f"  Win-rate            : {_pct(a.win_rate)}")
    print(f"  Avg deal size (ACV) : {_money(a.acv)}")
    print(f"  Cycle length        : {a.cycle_days:g} days")
    print(f"  >> Velocity         : {_money(vel)} of bookings/day")
    print("  --- per-lever sensitivity (+10% each, others held) ---")
    for lever, newvel in [("deals", vel*1.1), ("win-rate", vel*1.1), ("ACV", vel*1.1), ("cycle -10%", (a.open_deals*a.win_rate*a.acv)/(a.cycle_days*0.9))]:
        print(f"  {lever:<12}-> {_money(newvel)}/day")
    print("  NOTE: levers trade off — more volume often lowers win-rate (S3 #3).")
    print(f"\n  {DISCLAIMER}")
    return 0

def cmd_quota_capacity(a):
    if not (0 < a.ramp_factor <= 1):
        print("error: 0 < --ramp-factor <= 1", file=sys.stderr)
        return 2
    capacity_per_rep = a.productivity * a.ramp_factor
    team_capacity = capacity_per_rep * a.ramped_reps
    implied = capacity_per_rep / a.proposed_quota if a.proposed_quota else 0
    print("=== Quota vs capacity (CLAUDE.md S3 #4) ===")
    print(f"  Ramped reps         : {a.ramped_reps:g}")
    print(f"  Productivity/rep    : {_money(a.productivity)}  (fully ramped)")
    print(f"  Ramp factor         : {_pct(a.ramp_factor)}")
    print(f"  Capacity/rep        : {_money(capacity_per_rep)}")
    print(f"  Team capacity       : {_money(team_capacity)}")
    print(f"  Proposed quota/rep  : {_money(a.proposed_quota)}")
    print(f"  >> Implied median attainment: {_pct(implied)}")
    if implied < 0.9:
        print("  >> Quota likely OVER capacity — median rep set up to miss; refit (S3 #4)")
    elif implied > 1.15:
        print("  >> Quota likely UNDER capacity — leaving bookings on the table")
    else:
        print("  >> Quota fits capacity (median attainment in a healthy band)")
    print(f"\n  {DISCLAIMER}")
    return 0


def build_parser():
    p = argparse.ArgumentParser(
        prog='revops_calc.py',
        description="Sales & Revenue Operations decision calculator (stdlib only). Decision-support, not advice.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser('coverage', help='coverage ratio + required coverage from win-rate')
    sp.add_argument('--open-pipeline', type=float, required=True, help='open pipeline $')
    sp.add_argument('--remaining-quota', type=float, required=True, help='remaining quota $')
    sp.add_argument('--win-rate', type=float, required=True, help='stage-weighted win-rate (0-1)')
    sp.set_defaults(func=cmd_coverage)

    sp = sub.add_parser('forecast', help='weighted forecast = value x stage win-rate, minus slip haircut')
    sp.add_argument('--weighted-pipeline', type=float, required=True, help='Sum(deal value x stage win-rate) $')
    sp.add_argument('--committed', type=float, default=0.0, help='rep-committed total $ (for comparison)')
    sp.add_argument('--aging-haircut', type=float, default=0.0, help='slip/age haircut (0-1)')
    sp.set_defaults(func=cmd_forecast)

    sp = sub.add_parser('funnel', help='back-solve required leads + flag the leaking stage')
    sp.add_argument('--target-wins', type=float, required=True, help='target closed-won deals')
    sp.add_argument('--qual', type=float, required=True, help='lead->qual rate (0-1)')
    sp.add_argument('--demo', type=float, required=True, help='qual->demo rate (0-1)')
    sp.add_argument('--proposal', type=float, required=True, help='demo->proposal rate (0-1)')
    sp.add_argument('--close', type=float, required=True, help='proposal->close rate (0-1)')
    sp.set_defaults(func=cmd_funnel)

    sp = sub.add_parser('velocity', help='(deals x win-rate x ACV) / cycle, with per-lever sensitivity')
    sp.add_argument('--open-deals', type=float, required=True, help='open deals')
    sp.add_argument('--win-rate', type=float, required=True, help='win-rate (0-1)')
    sp.add_argument('--acv', type=float, required=True, help='avg deal size $')
    sp.add_argument('--cycle-days', type=float, required=True, help='cycle length in days')
    sp.set_defaults(func=cmd_velocity)

    sp = sub.add_parser('quota-capacity', help='capacity = reps x productivity x ramp; implied attainment')
    sp.add_argument('--ramped-reps', type=float, required=True, help='number of ramped reps')
    sp.add_argument('--productivity', type=float, required=True, help='annual bookings per fully-ramped rep $')
    sp.add_argument('--ramp-factor', type=float, default=0.85, help='avg ramp factor (0-1)')
    sp.add_argument('--proposed-quota', type=float, required=True, help='proposed quota per rep $')
    sp.set_defaults(func=cmd_quota_capacity)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
