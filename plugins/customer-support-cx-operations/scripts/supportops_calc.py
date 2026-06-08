#!/usr/bin/env python3
"""supportops_calc.py — a zero-dependency Customer Support & CX Operations decision calculator.

Removes arithmetic error from 3 recurring customer support & cx operations decisions:

  staffing      Workload-based agents at a target occupancy band.

  deflection    Self-service deflection savings vs cost-per-contact.

  sla-backlog   Arrivals vs resolution capacity: backlog change + days-to-clear.

This is a CALCULATOR, not a data source — it does not fetch benchmarks or live
data. The user supplies every input; the tool does the arithmetic and shows the
formula. Stdlib only (argparse); runs anywhere Python 3.8+ is present.

IMPORTANT: outputs are decision-support, not professional/legal/regulatory/
financial advice (see ../CLAUDE.md S2). Validate every figure against the
client's actual data; route every professional determination to the qualified
authority. No customer PII belongs in any input or output.
"""
from __future__ import annotations

import argparse
import sys

DISCLAIMER = (
    "Decision-support only — not professional/legal/regulatory/financial advice. "
    "Validate every input against the client's actual data; route professional "
    "determinations to the qualified authority (CLAUDE.md S2). No customer PII."
)


def _pct(x):
    return f"{x * 100:.1f}%"


def _money(x):
    return f"${x:,.0f}"


def cmd_staffing(a):
    if a.interval_hours <= 0 or a.aht_min <= 0:
        print("error: --interval-hours > 0 and --aht-min > 0", file=sys.stderr)
        return 2
    if not (0 < a.target_occupancy <= 1):
        print("error: 0 < --target-occupancy <= 1", file=sys.stderr)
        return 2
    workload_hours = a.contacts * (a.aht_min / 60.0)
    agents = workload_hours / (a.interval_hours * a.target_occupancy)
    print("=== Workload-based staffing (CLAUDE.md S3 #2) ===")
    print(f"  Forecast contacts   : {a.contacts:g}")
    print(f"  AHT                 : {a.aht_min:g} min")
    print(f"  Workload            : {workload_hours:,.1f} agent-hours")
    print(f"  Interval            : {a.interval_hours:g} h")
    print(f"  Target occupancy    : {_pct(a.target_occupancy)}")
    print(f"  >> Agents required  : {agents:,.1f}  (NOT a fixed agent:ticket ratio, S3 #2)")
    if a.target_occupancy > 0.9:
        print("  >> WARNING: occupancy above ~90% drives burnout and AHT creep (S3 #2)")
    print(f"\n  {DISCLAIMER}")
    return 0

def cmd_deflection(a):
    if not (0 <= a.deflection_rate <= 1):
        print("error: 0 <= --deflection-rate <= 1", file=sys.stderr)
        return 2
    if a.cost_per_contact < 0:
        print("error: --cost-per-contact >= 0", file=sys.stderr)
        return 2
    deflected = a.volume * a.deflection_rate
    residual = a.volume - deflected
    savings = deflected * a.cost_per_contact
    print("=== Deflection savings (CLAUDE.md S3 #1) ===")
    print(f"  Eligible volume     : {a.volume:,.0f}")
    print(f"  Deflection rate     : {_pct(a.deflection_rate)}  (measured, not assumed)")
    print(f"  Cost per contact    : {_money(a.cost_per_contact)}  (fully loaded)")
    print(f"  Contacts deflected  : {deflected:,.0f}")
    print(f"  Residual to staff   : {residual:,.0f}")
    print(f"  >> Recurring savings: {_money(savings)}  (deflection beats a recurring hire, S3 #1)")
    print(f"\n  {DISCLAIMER}")
    return 0

def cmd_sla_backlog(a):
    if a.arrivals < 0 or a.resolution_capacity < 0:
        print("error: --arrivals >= 0 and --resolution-capacity >= 0", file=sys.stderr)
        return 2
    backlog_change = a.arrivals - a.resolution_capacity
    net_capacity = a.resolution_capacity - a.arrivals
    print("=== SLA / backlog flow (CLAUDE.md S3 #5) ===")
    print(f"  Daily arrivals      : {a.arrivals:,.0f}")
    print(f"  Resolution capacity : {a.resolution_capacity:,.0f}/day")
    print(f"  Current backlog     : {a.current_backlog:,.0f}")
    print(f"  >> Backlog change   : {backlog_change:+,.0f}/day")
    if net_capacity > 0:
        days = a.current_backlog / net_capacity if a.current_backlog > 0 else 0
        print(f"  >> Net drain        : {net_capacity:,.0f}/day")
        print(f"  >> Days to clear    : {days:,.1f} days")
    else:
        print("  >> Arrivals >= capacity — backlog GROWS without bound; close the flow gap")
        print("     (deflect, staff, or tier — 'work faster' won't close it, S3 #5)")
    print(f"\n  {DISCLAIMER}")
    return 0


def build_parser():
    p = argparse.ArgumentParser(
        prog='supportops_calc.py',
        description="Customer Support & CX Operations decision calculator (stdlib only). Decision-support, not advice.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser('staffing', help='agents = contacts x AHT / (interval hours x occupancy)')
    sp.add_argument('--contacts', type=float, required=True, help='forecast contacts in the interval')
    sp.add_argument('--aht-min', type=float, required=True, help='average handle time in minutes')
    sp.add_argument('--interval-hours', type=float, required=True, help='interval length in hours')
    sp.add_argument('--target-occupancy', type=float, default=0.85, help='target occupancy (0-1)')
    sp.set_defaults(func=cmd_staffing)

    sp = sub.add_parser('deflection', help='cost avoided = deflection-rate x volume x cost-per-contact')
    sp.add_argument('--volume', type=float, required=True, help='contact volume eligible for deflection')
    sp.add_argument('--deflection-rate', type=float, required=True, help='measured deflection rate (0-1)')
    sp.add_argument('--cost-per-contact', type=float, required=True, help='fully-loaded cost per handled contact $')
    sp.set_defaults(func=cmd_deflection)

    sp = sub.add_parser('sla-backlog', help='backlog change = arrivals - capacity; days-to-clear')
    sp.add_argument('--arrivals', type=float, required=True, help='daily arriving contacts')
    sp.add_argument('--resolution-capacity', type=float, required=True, help='daily contacts the team can resolve')
    sp.add_argument('--current-backlog', type=float, default=0.0, help='current backlog of open contacts')
    sp.set_defaults(func=cmd_sla_backlog)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
