#!/usr/bin/env python3
"""people_calc.py — a zero-dependency People-Ops / HR decision calculator.

Removes arithmetic error from four recurring People decisions an HRBP /
People-Ops leader / founder runs constantly:

  attrition     Annualized turnover with cost and cause. Converts separations +
                average headcount into an annualized turnover %, splits regretted
                vs total, prices the regretted loss at a replacement cost, and
                reports a segment delta vs the company rate. Pairs with
                knowledge/people-ops-decision-trees.md (Tree 1).

  hiring-plan   The recruiting funnel as a system. Takes target hires + the four
                stage conversion rates (sourced->screen->onsite->offer->accept),
                back-solves the required pipeline at every stage, flags the
                leaking stage vs benchmark, and sizes recruiter capacity. Pairs
                with Tree 2 and CLAUDE.md SS3 #3/#6.

  comp-band     Band mechanics. Takes a salary + band min/mid/max and prints
                compa-ratio, range penetration, and an over/under-band flag.
                Pairs with knowledge/people-ops-economics.md SS3.

  pay-equity    Raw + ILLUSTRATIVE residual gap. Takes two groups' mean pay and
                (optionally) a controlled mean per group and prints the raw gap,
                the controlled gap, and the share of the raw gap explained by
                composition. This is a SIGNAL, not a regression or a legal
                conclusion (CLAUDE.md SS2, SS3 #5). Pairs with Tree 3.

This is a CALCULATOR, not a data source — it does not fetch benchmarks, salary
surveys, or live costs. The user supplies every input; the tool does the
arithmetic and shows the formula. Stdlib only (argparse); runs anywhere
Python 3.8+ is present.

IMPORTANT: outputs are decision-support, not legal, regulatory, or licensed
financial advice (see ../CLAUDE.md SS2). Validate every figure against the
client's actual HRIS/ATS data; route every legal/pay-equity determination to
qualified counsel (CLAUDE.md SS2, SS3 #5/#8). No employee PII belongs in any
input or output.

Examples
--------
  people_calc.py attrition --separations 42 --regretted 30 --avg-headcount 500 \\
      --months 12 --replacement-cost 45000 --segment-separations 9 \\
      --segment-headcount 60
  people_calc.py hiring-plan --target-hires 30 --accept 0.8 --onsite-offer 0.4 \\
      --screen-onsite 0.5 --source-screen 0.25 --sourced-per-recruiter 120
  people_calc.py comp-band --salary 132000 --band-min 110000 --band-mid 130000 \\
      --band-max 150000
  people_calc.py pay-equity --mean-a 118000 --mean-b 112000 \\
      --controlled-a 116000 --controlled-b 115000
"""
from __future__ import annotations

import argparse
import sys

DISCLAIMER = (
    "Decision-support only — not legal/regulatory/financial advice. Validate every "
    "input against the client's actual HRIS/ATS data; route legal & pay-equity "
    "determinations to qualified counsel (CLAUDE.md S2, S3 #5/#8). No employee PII."
)


def _pct(x: float) -> str:
    return f"{x * 100:.1f}%"


def _money(x: float) -> str:
    return f"${x:,.0f}"


def cmd_attrition(a: argparse.Namespace) -> int:
    if a.avg_headcount <= 0 or a.months <= 0:
        print("error: --avg-headcount and --months must be > 0", file=sys.stderr)
        return 2
    period_rate = a.separations / a.avg_headcount
    annualized = period_rate * (12.0 / a.months)
    regretted = a.regretted if a.regretted is not None else a.separations
    regretted_share = regretted / a.separations if a.separations else 0.0
    # Cost only the regretted (recoverable) loss — non-regretted is often intended.
    annual_regretted = regretted * (12.0 / a.months)
    attrition_cost = annual_regretted * a.replacement_cost

    print("=== Attrition: cost & cause (CLAUDE.md S3 #1) ===")
    print(f"  Period turnover     : {a.separations} sep / {a.avg_headcount:g} avg HC "
          f"= {_pct(period_rate)} over {a.months:g} mo")
    print(f"  Annualized turnover : {_pct(annualized)}  (period rate x 12/{a.months:g})")
    print(f"  Regretted share     : {regretted}/{a.separations} = {_pct(regretted_share)} "
          f"<- the headline split; non-regretted may be intended (S3 #1)")
    print(f"  Annual regretted exits (annualized): {annual_regretted:.1f}")
    print(f"  Replacement cost/role: {_money(a.replacement_cost)}")
    print(f"  >> Annual regretted attrition cost: {_money(attrition_cost)}")

    if a.segment_separations is not None and a.segment_headcount:
        seg_rate = (a.segment_separations / a.segment_headcount) * (12.0 / a.months)
        delta = seg_rate - annualized
        flag = "ABOVE" if delta > 0 else "below"
        print("  --- Segment delta (S3 #7: localize to team/manager) ---")
        print(f"  Segment annualized  : {_pct(seg_rate)}  "
              f"({_pct(abs(delta))} {flag} company {_pct(annualized)})")
        if delta > 0:
            print("  >> This segment is a hotspot — read it at the manager/span level.")
    print(f"\n  {DISCLAIMER}")
    return 0


def cmd_hiring_plan(a: argparse.Namespace) -> int:
    rates = {
        "offer->accept": a.accept,
        "onsite->offer": a.onsite_offer,
        "screen->onsite": a.screen_onsite,
        "sourced->screen": a.source_screen,
    }
    for name, r in rates.items():
        if not (0 < r <= 1):
            print(f"error: {name} rate must be in (0, 1]", file=sys.stderr)
            return 2
    offers = a.target_hires / a.accept
    onsites = offers / a.onsite_offer
    screens = onsites / a.screen_onsite
    sourced = screens / a.source_screen
    overall = a.target_hires / sourced

    print("=== Hiring plan: funnel as a system (CLAUDE.md S3 #3/#6) ===")
    print(f"  Target hires        : {a.target_hires:g}")
    print(f"  Required offers     : {offers:,.0f}   (accept {_pct(a.accept)})")
    print(f"  Required onsites    : {onsites:,.0f}   (onsite->offer {_pct(a.onsite_offer)})")
    print(f"  Required screens    : {screens:,.0f}   (screen->onsite {_pct(a.screen_onsite)})")
    print(f"  Required sourced    : {sourced:,.0f}   (sourced->screen {_pct(a.source_screen)})")
    print(f"  Overall conversion  : {_pct(overall)} sourced->hire")

    # Leaking-stage flag: lowest conversion rate is the constraint to fix first.
    worst = min(rates, key=rates.get)
    print(f"  >> Leaking stage    : '{worst}' at {_pct(rates[worst])} — fix this BEFORE "
          f"adding sourcing volume (S3 #3)")

    if a.sourced_per_recruiter:
        recruiters = sourced / a.sourced_per_recruiter
        print(f"  Recruiter capacity  : {recruiters:.1f} recruiter-loads "
              f"({a.sourced_per_recruiter:g} sourced/recruiter)")
    print(f"\n  {DISCLAIMER}")
    return 0


def cmd_comp_band(a: argparse.Namespace) -> int:
    if not (a.band_min < a.band_mid < a.band_max):
        print("error: require band-min < band-mid < band-max", file=sys.stderr)
        return 2
    compa = a.salary / a.band_mid
    penetration = (a.salary - a.band_min) / (a.band_max - a.band_min)
    spread = (a.band_max - a.band_min) / a.band_min

    print("=== Comp band mechanics (CLAUDE.md S3 #2) ===")
    print(f"  Salary              : {_money(a.salary)}")
    print(f"  Band                : {_money(a.band_min)} / {_money(a.band_mid)} / {_money(a.band_max)} (min/mid/max)")
    print(f"  Band spread         : {_pct(spread)}")
    print(f"  Compa-ratio         : {compa:.2f}   (salary / midpoint)")
    print(f"  Range penetration   : {_pct(penetration)}  (position in range)")
    if a.salary > a.band_max:
        print("  >> OVER band (green-circled) — frozen until band catches up; do not "
              "compound with a counteroffer (S3 #2)")
    elif a.salary < a.band_min:
        print("  >> UNDER band (red-circled) — equity/retention risk; fix to band, not ad hoc")
    elif compa < 0.8 or compa > 1.2:
        print("  >> Compa-ratio outlier (<0.8 or >1.2) — review leveling & market fit")
    else:
        print("  >> Within band and compa-ratio range — no action flagged")
    print(f"\n  {DISCLAIMER}")
    return 0


def cmd_pay_equity(a: argparse.Namespace) -> int:
    raw_gap = a.mean_a - a.mean_b
    raw_pct = raw_gap / a.mean_a if a.mean_a else 0.0
    print("=== Pay equity: raw vs illustrative residual (CLAUDE.md S3 #5) ===")
    print(f"  Group A mean pay    : {_money(a.mean_a)}")
    print(f"  Group B mean pay    : {_money(a.mean_b)}")
    print(f"  Raw gap (A - B)     : {_money(raw_gap)}  ({_pct(raw_pct)} of A)")
    print("  NOTE: the raw gap is mostly COMPOSITION (who holds which levels/roles),")
    print("        not pay discrimination — it is NOT the finding (S3 #5).")

    if a.controlled_a is not None and a.controlled_b is not None:
        residual = a.controlled_a - a.controlled_b
        residual_pct = residual / a.controlled_a if a.controlled_a else 0.0
        explained = (raw_gap - residual)
        explained_share = (explained / raw_gap) if raw_gap else 0.0
        print(f"  Controlled A / B    : {_money(a.controlled_a)} / {_money(a.controlled_b)}")
        print(f"  Residual gap        : {_money(residual)}  ({_pct(residual_pct)})")
        print(f"  Explained by comp.  : {_pct(explained_share)} of the raw gap")
        print("  >> The residual is a SIGNAL TO INVESTIGATE, not a legal conclusion.")
        print("     A defensible audit uses a regression + privileged legal review (S2).")
    else:
        print("  (supply --controlled-a/--controlled-b for the illustrative residual gap)")
    print("  >> Route any material residual to qualified counsel (S2). No PII in output.")
    print(f"\n  {DISCLAIMER}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="people_calc.py",
        description="People-Ops / HR decision calculator (stdlib only). Decision-support, not advice.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("attrition", help="annualized turnover, regretted split, replacement cost, segment delta")
    a.add_argument("--separations", type=float, required=True)
    a.add_argument("--regretted", type=float, default=None, help="regretted separations (default: all)")
    a.add_argument("--avg-headcount", type=float, required=True)
    a.add_argument("--months", type=float, default=12.0)
    a.add_argument("--replacement-cost", type=float, default=0.0, help="$ per regretted backfill")
    a.add_argument("--segment-separations", type=float, default=None)
    a.add_argument("--segment-headcount", type=float, default=None)
    a.set_defaults(func=cmd_attrition)

    h = sub.add_parser("hiring-plan", help="back-solve the funnel pipeline + leaking stage")
    h.add_argument("--target-hires", type=float, required=True)
    h.add_argument("--accept", type=float, required=True, help="offer->accept rate (0-1)")
    h.add_argument("--onsite-offer", type=float, required=True, help="onsite->offer rate (0-1)")
    h.add_argument("--screen-onsite", type=float, required=True, help="screen->onsite rate (0-1)")
    h.add_argument("--source-screen", type=float, required=True, help="sourced->screen rate (0-1)")
    h.add_argument("--sourced-per-recruiter", type=float, default=None)
    h.set_defaults(func=cmd_hiring_plan)

    c = sub.add_parser("comp-band", help="compa-ratio, range penetration, over/under-band flag")
    c.add_argument("--salary", type=float, required=True)
    c.add_argument("--band-min", type=float, required=True)
    c.add_argument("--band-mid", type=float, required=True)
    c.add_argument("--band-max", type=float, required=True)
    c.set_defaults(func=cmd_comp_band)

    e = sub.add_parser("pay-equity", help="raw gap + illustrative residual (signal, not a legal conclusion)")
    e.add_argument("--mean-a", type=float, required=True)
    e.add_argument("--mean-b", type=float, required=True)
    e.add_argument("--controlled-a", type=float, default=None)
    e.add_argument("--controlled-b", type=float, default=None)
    e.set_defaults(func=cmd_pay_equity)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
