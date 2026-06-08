#!/usr/bin/env python3
"""platform_engineering_idp_calc.py — a zero-dependency Platform Engineering (IDP) decision calculator.

Removes arithmetic error from 3 recurring platform engineering (idp) decisions:

  dora          Classify the four DORA keys into elite/high/medium/low.

  adoption      Golden-path adoption ratio and the gap.

  toil          Toil automation ROI in engineer-hours per year.

This is a CALCULATOR, not a data source — it does not fetch benchmarks or live
data. The user supplies every input; the tool does the arithmetic and shows the
formula. Stdlib only (argparse); runs anywhere Python 3.8+ is present.

IMPORTANT: outputs are decision-support, not professional/legal/regulatory/
financial advice (see ../CLAUDE.md S2). Validate every figure against the
client's actual data; route every professional determination to the qualified
authority. No internal credentials/PII belongs in any input or output.
"""
from __future__ import annotations

import argparse
import sys

DISCLAIMER = (
    "Decision-support only — not professional/legal/regulatory/financial advice. "
    "Validate every input against the client's actual data; route professional "
    "determinations to the qualified authority (CLAUDE.md S2). No internal credentials/PII."
)


def _pct(x):
    return f"{x * 100:.1f}%"


def _money(x):
    return f"${x:,.0f}"


def cmd_dora(a):
    if not (0 <= a.change_fail_rate <= 1):
        print("error: 0 <= --change-fail-rate <= 1", file=sys.stderr)
        return 2
    if a.deploys_per_week < 0 or a.lead_time_hours < 0 or a.mttr_hours < 0:
        print("error: rates and times must be >= 0", file=sys.stderr)
        return 2
    def band_df(d):
        if d >= 7: return "elite"
        if d >= 1: return "high"
        if d >= 0.25: return "medium"
        return "low"
    def band_lt(h):
        if h < 24: return "elite"
        if h < 168: return "high"
        if h < 720: return "medium"
        return "low"
    def band_cf(r):
        if r <= 0.05: return "elite"
        if r <= 0.10: return "high"
        if r <= 0.15: return "medium"
        return "low"
    def band_mttr(h):
        if h < 1: return "elite"
        if h < 24: return "high"
        if h < 168: return "medium"
        return "low"
    order = {"elite": 4, "high": 3, "medium": 2, "low": 1}
    keys = [("Deploy frequency", band_df(a.deploys_per_week), f"{a.deploys_per_week:g}/wk"),
            ("Lead time for change", band_lt(a.lead_time_hours), f"{a.lead_time_hours:g}h"),
            ("Change-failure rate", band_cf(a.change_fail_rate), _pct(a.change_fail_rate)),
            ("MTTR", band_mttr(a.mttr_hours), f"{a.mttr_hours:g}h")]
    print("=== DORA classification (CLAUDE.md S3 #3) ===")
    for name, band, val in keys:
        print(f"  {name:<22}: {val:<10} -> {band.upper()}")
    overall = min(keys, key=lambda k: order[k[1]])
    print(f"  >> Org band (weakest key): {overall[1].upper()}  ('{overall[0]}' is the lever)")
    print("  NOTE: bands are [unverified - training knowledge]; classify against a dated source (S3 #8).")
    print(f"\n  {DISCLAIMER}")
    return 0

def cmd_adoption(a):
    if a.total_teams <= 0:
        print("error: --total-teams > 0", file=sys.stderr)
        return 2
    if a.teams_on_path < 0 or a.teams_on_path > a.total_teams:
        print("error: 0 <= --teams-on-path <= --total-teams", file=sys.stderr)
        return 2
    adoption = a.teams_on_path / a.total_teams
    gap = a.total_teams - a.teams_on_path
    print("=== Golden-path adoption (CLAUDE.md S3 #7) ===")
    print(f"  Teams on path       : {a.teams_on_path:g}")
    print(f"  Total teams         : {a.total_teams:g}")
    print(f"  >> Adoption         : {_pct(adoption)}")
    print(f"  >> Gap (backlog)    : {gap:g} teams not on the path")
    if adoption >= 0.8:
        print("  >> Strong adoption — close the remaining gap, segment the holdouts (S3 #7)")
    elif adoption >= 0.5:
        print("  >> Majority adoption — the gap is the backlog; segment by friction (S3 #2)")
    else:
        print("  >> Minority adoption — feature count is misleading; pave the binding friction first (S3 #2 #7)")
    print(f"\n  {DISCLAIMER}")
    return 0

def cmd_toil(a):
    if a.task_minutes < 0 or a.per_year < 0 or a.engineers < 0:
        print("error: all inputs must be >= 0", file=sys.stderr)
        return 2
    hours_per_year = (a.task_minutes * a.per_year * a.engineers) / 60.0
    print("=== Toil automation ROI (CLAUDE.md S3 #4) ===")
    print(f"  Minutes per task    : {a.task_minutes:g}")
    print(f"  Occurrences/eng/yr  : {a.per_year:g}")
    print(f"  Engineers affected  : {a.engineers:g}")
    print(f"  >> Toil cost        : {hours_per_year:,.0f} engineer-hours/yr")
    if a.build_hours:
        payback = a.build_hours / hours_per_year if hours_per_year else float('inf')
        print(f"  Build+maintain cost : {a.build_hours:g} hours (one-time)")
        if payback <= 1:
            print(f"  >> Payback in {payback:.2f} yr — automate; clears the bar (S3 #4)")
        else:
            print(f"  >> Payback in {payback:.2f} yr — defer unless it's a high-adoption path (S3 #7)")
    else:
        print("  >> Every recurring ticket is platform debt — weigh vs the self-service build cost (S3 #4)")
    print(f"\n  {DISCLAIMER}")
    return 0


def build_parser():
    p = argparse.ArgumentParser(
        prog='platform_engineering_idp_calc.py',
        description="Platform Engineering (IDP) decision calculator (stdlib only). Decision-support, not advice.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser('dora', help='classify deploy freq, lead time, change-fail, MTTR')
    sp.add_argument('--deploys-per-week', type=float, required=True, help='deployments to prod per week')
    sp.add_argument('--lead-time-hours', type=float, required=True, help='median commit->prod lead time (hours)')
    sp.add_argument('--change-fail-rate', type=float, required=True, help='change-failure rate (0-1)')
    sp.add_argument('--mttr-hours', type=float, required=True, help='median time to restore (hours)')
    sp.set_defaults(func=cmd_dora)

    sp = sub.add_parser('adoption', help='teams on path / total -> adoption % + gap')
    sp.add_argument('--teams-on-path', type=float, required=True, help='teams on the golden path')
    sp.add_argument('--total-teams', type=float, required=True, help='total teams')
    sp.set_defaults(func=cmd_adoption)

    sp = sub.add_parser('toil', help='minutes x frequency x engineers -> hours/yr saved')
    sp.add_argument('--task-minutes', type=float, required=True, help='manual minutes per occurrence')
    sp.add_argument('--per-year', type=float, required=True, help='occurrences per engineer per year')
    sp.add_argument('--engineers', type=float, required=True, help='engineers affected')
    sp.add_argument('--build-hours', type=float, default=0.0, help='one-time build+maintain hours (for ROI)')
    sp.set_defaults(func=cmd_toil)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
