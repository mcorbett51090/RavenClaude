#!/usr/bin/env python3
"""hotel_hospitality_operations_calc.py — a zero-dependency Hotel & Hospitality Operations decision calculator.

Removes arithmetic error from 3 recurring hotel & hospitality operations decisions:

  revpar        Occupancy, ADR, RevPAR (+ optional GOPPAR).

  channel-cost  Net rate per channel after acquisition cost.

  labor         Labor hours, cost, and cost-per-occupied-room from a standard.

This is a CALCULATOR, not a data source — it does not fetch benchmarks or live
data. The user supplies every input; the tool does the arithmetic and shows the
formula. Stdlib only (argparse); runs anywhere Python 3.8+ is present.

IMPORTANT: outputs are decision-support, not professional/legal/regulatory/
financial advice (see ../CLAUDE.md S2). Validate every figure against the
client's actual data; route every professional determination to the qualified
authority. No guest PII belongs in any input or output.
"""
from __future__ import annotations

import argparse
import sys

DISCLAIMER = (
    "Decision-support only — not professional/legal/regulatory/financial advice. "
    "Validate every input against the client's actual data; route professional "
    "determinations to the qualified authority (CLAUDE.md S2). No guest PII."
)


def _pct(x):
    return f"{x * 100:.1f}%"


def _money(x):
    return f"${x:,.0f}"


def cmd_revpar(a):
    if a.rooms_available <= 0 or a.rooms_sold < 0:
        print("error: --rooms-available > 0 and --rooms-sold >= 0", file=sys.stderr)
        return 2
    if a.rooms_sold > a.rooms_available:
        print("error: --rooms-sold cannot exceed --rooms-available", file=sys.stderr)
        return 2
    occ = a.rooms_sold / a.rooms_available
    adr = a.room_revenue / a.rooms_sold if a.rooms_sold else 0
    revpar = a.room_revenue / a.rooms_available
    print("=== RevPAR (CLAUDE.md S3 #1) ===")
    print(f"  Rooms available      : {a.rooms_available:g}")
    print(f"  Rooms sold           : {a.rooms_sold:g}")
    print(f"  >> Occupancy         : {_pct(occ)}")
    print(f"  >> ADR               : {_money(adr)}  (room revenue / rooms sold)")
    print(f"  >> RevPAR            : {_money(revpar)}  (= ADR x occupancy)")
    if a.gop:
        goppar = a.gop / a.rooms_available
        print(f"  >> GOPPAR            : {_money(goppar)}  (gross operating profit / rooms available)")
        if a.total_revenue > 0:
            gop_margin = a.gop / a.total_revenue
            print(f"  >> GOP margin        : {_pct(gop_margin)}  — profit beats top line (S3 #5)")
    print(f"\n  {DISCLAIMER}")
    return 0

def cmd_channel_cost(a):
    if a.gross_rate <= 0 or not (0 <= a.ota_commission < 1):
        print("error: --gross-rate > 0 and 0 <= --ota-commission < 1", file=sys.stderr)
        return 2
    net_ota = a.gross_rate * (1 - a.ota_commission)
    net_direct = a.gross_rate - a.direct_acquisition_cost
    print("=== Channel net rate (CLAUDE.md S3 #2) ===")
    print(f"  Gross rate           : {_money(a.gross_rate)}")
    print(f"  OTA commission       : {_pct(a.ota_commission)}")
    print(f"  >> Net rate (OTA)    : {_money(net_ota)}  (gross x (1 - commission))")
    print(f"  Direct acq. cost     : {_money(a.direct_acquisition_cost)}")
    print(f"  >> Net rate (direct) : {_money(net_direct)}  (gross - acquisition cost)")
    diff = net_direct - net_ota
    if diff > 0:
        print(f"  >> DIRECT keeps {_money(diff)} more per booking — value direct/loyalty demand (S3 #2 #6)")
    elif diff < 0:
        print(f"  >> OTA keeps {_money(-diff)} more per booking here — but watch repeat/direct margin over time (S3 #6)")
    else:
        print("  >> Channels net the same per booking at these inputs")
    print(f"\n  {DISCLAIMER}")
    return 0

def cmd_labor(a):
    if a.occupied_rooms <= 0:
        print("error: --occupied-rooms > 0", file=sys.stderr)
        return 2
    if a.target_hours_per_occupied_room < 0 or a.hourly_wage < 0:
        print("error: --target-hours-per-occupied-room and --hourly-wage must be >= 0", file=sys.stderr)
        return 2
    labor_hours = a.occupied_rooms * a.target_hours_per_occupied_room
    labor_cost = labor_hours * a.hourly_wage
    cost_per_occ = labor_cost / a.occupied_rooms
    print("=== Labor productivity (CLAUDE.md S3 #4) ===")
    print(f"  Occupied rooms       : {a.occupied_rooms:g}")
    print(f"  Target hrs/occ room  : {a.target_hours_per_occupied_room:g}")
    print(f"  Loaded hourly wage   : {_money(a.hourly_wage)}")
    print(f"  >> Labor hours       : {labor_hours:,.0f}")
    print(f"  >> Labor cost        : {_money(labor_cost)}")
    print(f"  >> Cost per occupied room: {_money(cost_per_occ)}  (the productivity number, S3 #4)")
    print("  NOTE: flex this to the occupancy pace forecast — a fixed roster over-spends low nights (S3 #4).")
    print(f"\n  {DISCLAIMER}")
    return 0


def build_parser():
    p = argparse.ArgumentParser(
        prog='hotel_hospitality_operations_calc.py',
        description="Hotel & Hospitality Operations decision calculator (stdlib only). Decision-support, not advice.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser('revpar', help='rooms sold / available + revenue => occupancy, ADR, RevPAR, GOPPAR')
    sp.add_argument('--rooms-available', type=float, required=True, help='rooms available (room-nights)')
    sp.add_argument('--rooms-sold', type=float, required=True, help='rooms sold (room-nights)')
    sp.add_argument('--room-revenue', type=float, required=True, help='room revenue $')
    sp.add_argument('--total-revenue', type=float, default=0.0, help='total revenue $ (for GOPPAR)')
    sp.add_argument('--gop', type=float, default=0.0, help='gross operating profit $ (for GOPPAR)')
    sp.set_defaults(func=cmd_revpar)

    sp = sub.add_parser('channel-cost', help='gross rate - OTA commission vs direct acquisition cost => net rate + better channel')
    sp.add_argument('--gross-rate', type=float, required=True, help='gross room rate $')
    sp.add_argument('--ota-commission', type=float, required=True, help='OTA commission rate (0-1)')
    sp.add_argument('--direct-acquisition-cost', type=float, default=0.0, help='direct acquisition cost per booking $')
    sp.set_defaults(func=cmd_channel_cost)

    sp = sub.add_parser('labor', help='occupied rooms x target hrs/occ room x wage => hours, cost, cost/occ room')
    sp.add_argument('--occupied-rooms', type=float, required=True, help='occupied rooms (room-nights)')
    sp.add_argument('--target-hours-per-occupied-room', type=float, required=True, help='target labor hours per occupied room')
    sp.add_argument('--hourly-wage', type=float, required=True, help='loaded hourly wage $')
    sp.set_defaults(func=cmd_labor)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
