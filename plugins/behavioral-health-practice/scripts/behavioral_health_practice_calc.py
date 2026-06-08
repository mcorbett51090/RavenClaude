#!/usr/bin/env python3
"""behavioral_health_practice_calc.py — a zero-dependency Behavioral Health Practice decision calculator.

Removes arithmetic error from 3 recurring behavioral health practice decisions:

  no-show       No-show loss as a flow + reminder-program recovery.

  caseload      Clinician caseload capacity vs demand + utilization.

  payer-mix     Blended reimbursement + margin and a mix-shift delta.

This is a CALCULATOR, not a data source — it does not fetch benchmarks or live
data. The user supplies every input; the tool does the arithmetic and shows the
formula. Stdlib only (argparse); runs anywhere Python 3.8+ is present.

IMPORTANT: outputs are decision-support, not professional/legal/regulatory/
financial advice (see ../CLAUDE.md S2). Validate every figure against the
client's actual data; route every professional determination to the qualified
authority. No patient PHI belongs in any input or output.
"""
from __future__ import annotations

import argparse
import sys

DISCLAIMER = (
    "Decision-support only — not professional/legal/regulatory/financial advice. "
    "Validate every input against the client's actual data; route professional "
    "determinations to the qualified authority (CLAUDE.md S2). No patient PHI."
)


def _pct(x):
    return f"{x * 100:.1f}%"


def _money(x):
    return f"${x:,.0f}"


def cmd_no_show(a):
    if not (0 <= a.no_show_rate <= 1):
        print("error: 0 <= --no-show-rate <= 1", file=sys.stderr)
        return 2
    if not (0 <= a.reminder_lift <= 1):
        print("error: 0 <= --reminder-lift <= 1", file=sys.stderr)
        return 2
    lost_slots = a.scheduled_visits * a.no_show_rate
    lost_revenue = lost_slots * a.avg_visit_revenue
    recovered_slots = lost_slots * a.reminder_lift
    recovered_revenue = lost_revenue * a.reminder_lift
    print("=== No-show flow: lost slots + revenue (CLAUDE.md S3 #1) ===")
    print(f"  Scheduled visits    : {a.scheduled_visits:g}")
    print(f"  No-show/late-cancel : {_pct(a.no_show_rate)}")
    print(f"  Avg visit revenue   : {_money(a.avg_visit_revenue)}")
    print(f"  >> Lost slots       : {lost_slots:,.0f}  (access NOT delivered)")
    print(f"  >> Lost revenue     : {_money(lost_revenue)}")
    if a.reminder_lift > 0:
        print(f"  Reminder lift       : {_pct(a.reminder_lift)}")
        print(f"  >> Recovered slots  : {recovered_slots:,.0f}")
        print(f"  >> Recovered revenue: {_money(recovered_revenue)}  (then backfill the residual)")
    else:
        print("  NOTE: pass --reminder-lift to model recovery; backfill residual via waitlist/telehealth (S3 #1 #7).")
    print(f"\n  {DISCLAIMER}")
    return 0

def cmd_caseload(a):
    if a.session_hours <= 0 or a.clinician_ftes <= 0:
        print("error: --session-hours > 0 and --clinician-ftes > 0", file=sys.stderr)
        return 2
    capacity = a.clinician_ftes * a.weekly_billable_hours / a.session_hours
    util = a.demand_sessions / capacity if capacity else 0
    gap = a.demand_sessions - capacity
    print("=== Caseload capacity vs demand (CLAUDE.md S3 #4) ===")
    print(f"  Clinician FTEs      : {a.clinician_ftes:g}")
    print(f"  Weekly billable hrs : {a.weekly_billable_hours:g} / FTE")
    print(f"  Avg session length  : {a.session_hours:g} h")
    print(f"  >> Weekly capacity  : {capacity:,.1f} sessions")
    print(f"  Demand              : {a.demand_sessions:,.1f} sessions")
    print(f"  >> Utilization      : {_pct(util)}  (demand / capacity)")
    if gap > 0:
        print(f"  >> SHORT by {gap:,.1f} sessions/week — access constrained; staff to demand (S3 #4)")
    elif util < 0.75:
        print(f"  >> Idle capacity ({abs(gap):,.1f} sessions/week) — margin on unbilled time (S3 #4)")
    else:
        print("  >> Capacity fits demand (utilization in a healthy band)")
    print(f"\n  {DISCLAIMER}")
    return 0

def cmd_payer_mix(a):
    if not (0 <= a.shift_to_b <= 1):
        print("error: 0 <= --shift-to-b <= 1", file=sys.stderr)
        return 2
    total = a.volume_a + a.volume_b
    if total <= 0:
        print("error: total volume must be > 0", file=sys.stderr)
        return 2
    blended_reimb = (a.volume_a * a.reimb_a + a.volume_b * a.reimb_b) / total
    blended_margin = blended_reimb - a.variable_cost
    margin_a = a.reimb_a - a.variable_cost
    margin_b = a.reimb_b - a.variable_cost
    print("=== Payer mix: blended reimbursement + margin (CLAUDE.md S3 #5) ===")
    print(f"  Payer A             : {a.volume_a:g} visits @ {_money(a.reimb_a)}  -> margin/visit {_money(margin_a)}")
    print(f"  Payer B             : {a.volume_b:g} visits @ {_money(a.reimb_b)}  -> margin/visit {_money(margin_b)}")
    print(f"  Variable cost/visit : {_money(a.variable_cost)}")
    print(f"  >> Blended reimburse: {_money(blended_reimb)}")
    print(f"  >> Blended margin   : {_money(blended_margin)} / visit")
    if margin_a < 0 or margin_b < 0:
        neg = "A" if margin_a < 0 else "B"
        print(f"  >> WARNING: payer {neg} bills BELOW variable cost — check parity, route to counsel (S3 #5 #8)")
    if a.shift_to_b > 0:
        moved = a.volume_a * a.shift_to_b
        new_a = a.volume_a - moved
        new_b = a.volume_b + moved
        new_blended = (new_a * a.reimb_a + new_b * a.reimb_b) / total
        new_margin = new_blended - a.variable_cost
        delta = new_margin - blended_margin
        print(f"  Mix shift           : {_pct(a.shift_to_b)} of A -> B ({moved:g} visits)")
        print(f"  >> New blended margin: {_money(new_margin)} / visit  (delta {_money(delta)})")
        print("  NOTE: a mix shift assumes capacity to serve it — check caseload (S3 #4).")
    print(f"\n  {DISCLAIMER}")
    return 0


def build_parser():
    p = argparse.ArgumentParser(
        prog='behavioral_health_practice_calc.py',
        description="Behavioral Health Practice decision calculator (stdlib only). Decision-support, not advice.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser('no-show', help='lost slots + revenue, plus recovery from a reminder lift')
    sp.add_argument('--scheduled-visits', type=float, required=True, help='scheduled visits in the window')
    sp.add_argument('--no-show-rate', type=float, required=True, help='no-show + late-cancel rate (0-1)')
    sp.add_argument('--avg-visit-revenue', type=float, required=True, help='avg revenue per kept visit $')
    sp.add_argument('--reminder-lift', type=float, default=0.0, help='fraction of no-shows a reminder program recovers (0-1)')
    sp.set_defaults(func=cmd_no_show)

    sp = sub.add_parser('caseload', help='capacity in sessions vs demand -> utilization + gap')
    sp.add_argument('--clinician-ftes', type=float, required=True, help='clinician FTEs')
    sp.add_argument('--weekly-billable-hours', type=float, required=True, help='target weekly billable hours per FTE')
    sp.add_argument('--session-hours', type=float, required=True, help='avg session length in hours')
    sp.add_argument('--demand-sessions', type=float, required=True, help='demand in sessions for the same week')
    sp.set_defaults(func=cmd_caseload)

    sp = sub.add_parser('payer-mix', help='blended reimbursement + margin/visit + mix-shift delta')
    sp.add_argument('--volume-a', type=float, required=True, help='payer A visit volume')
    sp.add_argument('--reimb-a', type=float, required=True, help='payer A reimbursement/visit $')
    sp.add_argument('--volume-b', type=float, required=True, help='payer B visit volume')
    sp.add_argument('--reimb-b', type=float, required=True, help='payer B reimbursement/visit $')
    sp.add_argument('--variable-cost', type=float, required=True, help='variable cost per visit $')
    sp.add_argument('--shift-to-b', type=float, default=0.0, help='fraction of A volume shifted to B (0-1)')
    sp.set_defaults(func=cmd_payer_mix)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
