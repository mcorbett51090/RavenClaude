#!/usr/bin/env python3
"""marketingops_calc.py — a zero-dependency Marketing Operations decision calculator.

Removes arithmetic error from 3 recurring marketing operations decisions:

  funnel        MQL->SQL->opp->win required leads + the leaking stage.

  cac-ltv       CAC, LTV, LTV:CAC ratio, and CAC-payback months.

  channel-roi   Channel ROI + cost-per-opp under a NAMED attribution model.

This is a CALCULATOR, not a data source — it does not fetch benchmarks or live
data. The user supplies every input; the tool does the arithmetic and shows the
formula. Stdlib only (argparse); runs anywhere Python 3.8+ is present.

IMPORTANT: outputs are decision-support, not professional/legal/regulatory/
financial advice (see ../CLAUDE.md S2). Validate every figure against the
client's actual data; route every professional determination to the qualified
authority. No customer/lead PII belongs in any input or output.
"""
from __future__ import annotations

import argparse
import sys

DISCLAIMER = (
    "Decision-support only — not professional/legal/regulatory/financial advice. "
    "Validate every input against the client's actual data; route professional "
    "determinations to the qualified authority (CLAUDE.md S2). No customer/lead PII."
)


def _pct(x):
    return f"{x * 100:.1f}%"


def _money(x):
    return f"${x:,.0f}"


def cmd_funnel(a):
    rates = {"lead->MQL": a.lead_mql, "MQL->SQL": a.mql_sql, "SQL->opp": a.sql_opp, "opp->win": a.opp_win}
    for n, r in rates.items():
        if not (0 < r <= 1):
            print(f"error: {n} must be in (0,1]", file=sys.stderr)
            return 2
    opps = a.target_wins / a.opp_win
    sqls = opps / a.sql_opp
    mqls = sqls / a.mql_sql
    leads = mqls / a.lead_mql
    print("=== Funnel: required leads + leak (CLAUDE.md S3 #1) ===")
    print(f"  Target wins         : {a.target_wins:g}")
    print(f"  Required opps       : {opps:,.0f}  (opp->win {_pct(a.opp_win)})")
    print(f"  Required SQLs       : {sqls:,.0f}  (SQL->opp {_pct(a.sql_opp)})")
    print(f"  Required MQLs       : {mqls:,.0f}  (MQL->SQL {_pct(a.mql_sql)})")
    print(f"  Required leads      : {leads:,.0f}  (lead->MQL {_pct(a.lead_mql)})")
    worst = min(rates, key=rates.get)
    print(f"  >> Leaking stage    : '{worst}' at {_pct(rates[worst])} — fix BEFORE adding leads (S3 #1)")
    print(f"\n  {DISCLAIMER}")
    return 0

def cmd_cac_ltv(a):
    if a.cac <= 0:
        print("error: --cac > 0", file=sys.stderr)
        return 2
    ratio = a.ltv / a.cac
    print("=== CAC / LTV economics (CLAUDE.md S3 #3) ===")
    print(f"  Fully-loaded CAC    : {_money(a.cac)}")
    print(f"  LTV (gross-margin)  : {_money(a.ltv)}")
    print(f"  >> LTV:CAC ratio    : {ratio:.2f}:1")
    if ratio < 1:
        print("  >> UNSUSTAINABLE — spending more than the customer is worth; fix before scaling (S3 #3)")
    elif ratio < 3:
        print("  >> Below the ~3:1 health frame [unverified] — efficient growth, thin headroom (S3 #3 #8)")
    else:
        print("  >> At/above the ~3:1 health frame [unverified] — room to invest in growth (S3 #8)")
    if a.monthly_margin > 0:
        payback = a.cac / a.monthly_margin
        print(f"  Monthly margin/cust : {_money(a.monthly_margin)}")
        print(f"  >> CAC-payback      : {payback:,.1f} months")
    print(f"\n  {DISCLAIMER}")
    return 0

def cmd_channel_roi(a):
    if a.spend <= 0:
        print("error: --spend > 0", file=sys.stderr)
        return 2
    roi = (a.pipeline - a.spend) / a.spend
    models = {1: "first-touch", 2: "last-touch", 3: "multi-touch"}
    model_name = models.get(int(a.model), "multi-touch")
    print("=== Channel ROI (CLAUDE.md S3 #2/#5) ===")
    print(f"  Attribution model   : {model_name}  (the model CHANGES the ranking, S3 #2)")
    print(f"  Channel spend       : {_money(a.spend)}")
    print(f"  Pipeline contribution: {_money(a.pipeline)}")
    print(f"  >> ROI              : {_pct(roi)}  ((contribution - spend) / spend)")
    if a.opps > 0:
        cost_per_opp = a.spend / a.opps
        print(f"  Opportunities       : {a.opps:g}")
        print(f"  >> Cost per opp     : {_money(cost_per_opp)}")
    print("  NOTE: read MARGINAL ROI before scaling — average ROI hides saturation (S3 #5).")
    print(f"\n  {DISCLAIMER}")
    return 0


def build_parser():
    p = argparse.ArgumentParser(
        prog='marketingops_calc.py',
        description="Marketing Operations decision calculator (stdlib only). Decision-support, not advice.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser('funnel', help='back-solve required leads + flag the leaking stage')
    sp.add_argument('--target-wins', type=float, required=True, help='target closed-won deals')
    sp.add_argument('--lead-mql', type=float, required=True, help='lead->MQL rate (0-1)')
    sp.add_argument('--mql-sql', type=float, required=True, help='MQL->SQL rate (0-1)')
    sp.add_argument('--sql-opp', type=float, required=True, help='SQL->opp rate (0-1)')
    sp.add_argument('--opp-win', type=float, required=True, help='opp->win rate (0-1)')
    sp.set_defaults(func=cmd_funnel)

    sp = sub.add_parser('cac-ltv', help='LTV:CAC + payback gate spend, not lead count')
    sp.add_argument('--cac', type=float, required=True, help='fully-loaded customer acquisition cost $')
    sp.add_argument('--ltv', type=float, required=True, help='gross-margin lifetime value per customer $')
    sp.add_argument('--monthly-margin', type=float, default=0.0, help='monthly gross-margin per customer $ (for payback)')
    sp.set_defaults(func=cmd_cac_ltv)

    sp = sub.add_parser('channel-roi', help='(contribution - spend) / spend; state the attribution model')
    sp.add_argument('--spend', type=float, required=True, help='channel spend $')
    sp.add_argument('--pipeline', type=float, required=True, help='pipeline contribution attributed to the channel $')
    sp.add_argument('--opps', type=float, default=0.0, help='opportunities attributed to the channel')
    sp.add_argument('--model', type=float, default=3.0, help='attribution model code (1=first 2=last 3=multi)')
    sp.set_defaults(func=cmd_channel_roi)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
