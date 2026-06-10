#!/usr/bin/env python3
"""engineering_management_calc.py — a zero-dependency Engineering Management decision calculator.

Removes arithmetic error from 3 recurring engineering-management decisions:

  oncall-load    Per-engineer on-call load vs a sustainable threshold, with off-hours burden.

  attrition-cost Fully-loaded cost of regretted attrition (replacement + ramp loss + team drag).

  tech-debt      Carrying cost of a debt and the payback period of paying it down.

This is a CALCULATOR, not a data source — it does not fetch benchmarks or live
data. The user supplies every input; the tool does the arithmetic and shows the
formula. Stdlib only (argparse); runs anywhere Python 3.8+ is present.

IMPORTANT: outputs are decision-support, not HR/compensation/legal advice
(see ../CLAUDE.md S2). Validate every figure against the team's actual
situation; route every HR/comp/legal determination to the qualified authority.
No real personnel PII belongs in any input or output.
"""
from __future__ import annotations

import argparse
import sys

DISCLAIMER = (
    "Decision-support only — not HR/compensation/legal advice. Validate every "
    "input against the team's actual situation; route HR/comp/legal "
    "determinations to the qualified authority (CLAUDE.md S2). No personnel PII."
)


def _money(x):
    return f"${x:,.0f}"


def _pct(x):
    return f"{x * 100:.1f}%"


def cmd_oncall_load(a):
    if a.rotation_depth <= 0:
        print("error: --rotation-depth must be > 0", file=sys.stderr)
        return 2
    if a.pages_per_week < 0 or a.off_hours_pages < 0:
        print("error: page counts must be >= 0", file=sys.stderr)
        return 2
    if a.off_hours_pages > a.pages_per_week:
        print("error: --off-hours-pages cannot exceed --pages-per-week", file=sys.stderr)
        return 2

    per_eng_week = a.pages_per_week / a.rotation_depth
    # Each engineer is primary 1/depth of the time; pages/shift while primary ≈ pages_per_week/7.
    pages_per_primary_day = a.pages_per_week / 7.0
    off_hours_burden = (a.off_hours_pages / a.pages_per_week) if a.pages_per_week > 0 else 0.0

    print("On-call load")
    print(f"  Actionable pages / week (team) : {a.pages_per_week:g}")
    print(f"  Rotation depth (engineers)     : {a.rotation_depth:g}")
    print(f"  = pages / engineer / week      : {per_eng_week:.2f}")
    print(f"  Pages / day while primary      : {pages_per_primary_day:.2f}")
    print(f"  Off-hours burden               : {_pct(off_hours_burden)} of pages")

    flags = []
    if pages_per_primary_day > a.sustainable_pages_per_day:
        flags.append(
            f"load {pages_per_primary_day:.2f}/day exceeds the sustainable threshold "
            f"({a.sustainable_pages_per_day:g}/day) — cut pages (toil/false-alarms) FIRST (§3, economics §2)"
        )
    if off_hours_burden > 0.5:
        flags.append(
            f"off-hours burden {_pct(off_hours_burden)} > 50% — the burnout driver; reduce before deepening rotation"
        )
    if a.rotation_depth < 4:
        flags.append(
            f"rotation depth {a.rotation_depth:g} < 4 — each engineer is on the hook often; thin rotations burn out"
        )
    if flags:
        print("  FLAGS:")
        for f in flags:
            print(f"    - {f}")
    else:
        print("  No threshold flags — still validate against how the team actually feels.")
    print(f"\n{DISCLAIMER}")
    return 0


def cmd_attrition_cost(a):
    for name, v in (("--salary", a.salary), ("--months-to-ramp", a.months_to_ramp)):
        if v < 0:
            print(f"error: {name} must be >= 0", file=sys.stderr)
            return 2
    monthly_loaded = a.salary * a.loaded_multiplier / 12.0
    replacement_cost = a.salary * a.replacement_fraction
    ramp_loss = monthly_loaded * a.months_to_ramp * a.ramp_loss_fraction
    team_drag = a.team_drag
    total = replacement_cost + ramp_loss + team_drag

    print("Cost of regretted attrition (one engineer)")
    print(f"  Annual salary                  : {_money(a.salary)}")
    print(f"  Loaded monthly cost (×{a.loaded_multiplier:g})    : {_money(monthly_loaded)}")
    print("  ---")
    print(f"  Replacement cost ({_pct(a.replacement_fraction)} salary) : {_money(replacement_cost)}")
    print(
        f"  Ramp loss ({a.months_to_ramp:g}mo × {_pct(a.ramp_loss_fraction)} lost) : {_money(ramp_loss)}"
    )
    print(f"  Team drag (your estimate)      : {_money(team_drag)}")
    print(f"  = Total estimated cost         : {_money(total)}")
    print(f"  As a multiple of salary        : {total / a.salary:.2f}× " if a.salary else "")
    print(
        "\n  Framing: a held 1:1 and a real growth path are cheap against this number (§3 #2)."
    )
    print("  Every fraction here is an [unverified] org-specific estimate — replace with your own (§3 #8).")
    print(f"\n{DISCLAIMER}")
    return 0


def cmd_tech_debt(a):
    if a.work_volume <= 0 or a.loaded_cost_per_unit < 0:
        print("error: --work-volume must be > 0 and --loaded-cost-per-unit >= 0", file=sys.stderr)
        return 2
    if not (0 <= a.extra_lead_time_fraction < 1):
        print("error: --extra-lead-time-fraction must be in [0, 1)", file=sys.stderr)
        return 2
    # Carrying cost per period = the tax the debt adds to each period's work.
    carrying_cost = a.extra_lead_time_fraction * a.work_volume * a.loaded_cost_per_unit
    if carrying_cost <= 0:
        payback = float("inf")
    else:
        payback = a.paydown_cost / carrying_cost

    print("Tech-debt carrying cost & payback")
    print(f"  Work volume / period (units)   : {a.work_volume:g}")
    print(f"  Loaded cost / unit             : {_money(a.loaded_cost_per_unit)}")
    print(f"  Extra lead-time from debt       : {_pct(a.extra_lead_time_fraction)}")
    print(f"  = Carrying cost / period       : {_money(carrying_cost)}")
    print(f"  One-time paydown cost          : {_money(a.paydown_cost)}")
    if payback == float("inf"):
        print("  Payback periods                : n/a (no carrying cost — defer, §3 #7)")
    else:
        print(f"  = Payback periods              : {payback:.2f}")

    print("\n  Decision (§3 #7):")
    if payback != float("inf") and payback <= a.life_periods * 0.5 and a.on_hotspot:
        print("    PAY DOWN — short payback on a hotspot within the code's remaining life.")
    elif payback != float("inf") and payback <= a.life_periods and a.on_hotspot:
        print("    LIKELY PAY DOWN — payback within remaining life; prefer incremental (strangler-fig).")
    elif not a.on_hotspot:
        print("    DEFER — not on a measured hotspot; low leverage. Log the carrying cost and revisit.")
    else:
        print("    DEFER / TRADE EXPLICITLY — payback exceeds remaining life; size against roadmap value.")
    print("    A rewrite is the highest-risk, longest-payback option — cost incremental paydown first.")
    print(f"\n{DISCLAIMER}")
    return 0


def build_parser():
    p = argparse.ArgumentParser(
        prog="engineering_management_calc.py",
        description="Zero-dependency engineering-management decision calculator. " + DISCLAIMER,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    oc = sub.add_parser("oncall-load", help="Per-engineer on-call load vs a sustainable threshold.")
    oc.add_argument("--pages-per-week", type=float, required=True, help="Actionable pages/week across the team.")
    oc.add_argument("--rotation-depth", type=float, required=True, help="Engineers in the rotation.")
    oc.add_argument("--off-hours-pages", type=float, default=0.0, help="Of those, how many are off-hours.")
    oc.add_argument(
        "--sustainable-pages-per-day", type=float, default=2.0,
        help="Sustainable actionable pages/day while primary (default 2 — [unverified], tune to your team).",
    )
    oc.set_defaults(func=cmd_oncall_load)

    ac = sub.add_parser("attrition-cost", help="Fully-loaded cost of regretted attrition.")
    ac.add_argument("--salary", type=float, required=True, help="Annual base salary of the engineer.")
    ac.add_argument("--loaded-multiplier", type=float, default=1.4, help="Fully-loaded multiplier on salary (default 1.4).")
    ac.add_argument("--replacement-fraction", type=float, default=0.5, help="Replacement cost as fraction of salary (default 0.5, [unverified]).")
    ac.add_argument("--months-to-ramp", type=float, default=6.0, help="Months to full productivity for the backfill (default 6).")
    ac.add_argument("--ramp-loss-fraction", type=float, default=0.5, help="Avg productivity lost over ramp (default 0.5).")
    ac.add_argument("--team-drag", type=float, default=0.0, help="Your estimate of morale/onboarding tax on the team.")
    ac.set_defaults(func=cmd_attrition_cost)

    td = sub.add_parser("tech-debt", help="Carrying cost of a debt and payback of paying it down.")
    td.add_argument("--work-volume", type=float, required=True, help="Units of work per period passing through the debt.")
    td.add_argument("--loaded-cost-per-unit", type=float, required=True, help="Loaded cost per unit of work.")
    td.add_argument("--extra-lead-time-fraction", type=float, required=True, help="Extra lead-time the debt adds, e.g. 0.2 = +20%%.")
    td.add_argument("--paydown-cost", type=float, required=True, help="One-time cost to pay the debt down.")
    td.add_argument("--life-periods", type=float, default=12.0, help="Remaining life of the code in periods (default 12).")
    td.add_argument("--on-hotspot", action="store_true", help="Set if the debt is on a measured hotspot (high churn × complexity).")
    td.set_defaults(func=cmd_tech_debt)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
