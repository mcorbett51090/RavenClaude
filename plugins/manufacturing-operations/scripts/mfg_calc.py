#!/usr/bin/env python3
"""mfg_calc.py — a zero-dependency manufacturing-operations decision calculator.

Removes arithmetic error from three recurring shop-floor decisions the
manufacturing-operations agents run constantly — OEE, takt, and capacity — WITHOUT
pulling in pandas/numpy, so it runs anywhere Python 3.8+ is present. Every subcommand
prints the formula and the stated denominators, because an OEE/takt/capacity number with
undefined inputs is theater (the house opinion the whole plugin is built on).

  oee      Overall Equipment Effectiveness = Availability x Performance x Quality from
           run/downtime/count inputs, each factor with its denominator stated:
             Availability = run_time / planned_production_time
                            (planned_production_time = scheduled - planned_downtime)
             Performance  = (ideal_cycle_time * total_count) / run_time
             Quality      = good_count / total_count
             OEE          = Availability * Performance * Quality
           Decomposes the six big losses (A: breakdown+setup, P: minor-stops+reduced-speed,
           Q: scrap+rework). The ideal_cycle_time MUST be the demonstrated best repeatable
           rate, not a sandbagged marketing spec (oee-denominators-must-be-defined.md).

  takt     Takt time = available_time / demand, compared honestly to measured cycle time:
             takt_time  = available_time / demand_units
             required_rate = demand_units / available_time   (the drumbeat)
           Faster than takt makes inventory; slower misses demand. The gap is the signal,
           not the machine's top speed (produce-to-takt-not-to-machine-speed.md). With
           --cycle-time, reports the takt-vs-cycle verdict and the units of slack/shortfall.

  capacity MRP net-requirement and a load-vs-capacity check against the bottleneck rate:
             net_requirement = max(0, gross - on_hand - scheduled_receipts + safety_stock)
             required_capacity = net_requirement * cycle_time   (time the work needs)
             available_capacity = stations * shift_hours * shifts * util  (time on hand)
             load_pct = required_capacity / available_capacity
           load_pct > 1.0 means the demand exceeds the finite rate — the plan is a wish
           unless dates level, capacity is added, or the lot is re-cut. Plan to the
           constraint, never to infinite capacity (plan-to-the-constraint-...md).

This is a CALCULATOR, not a data source — it does not fetch MES exports, a BOM, or a
forecast. The user supplies every input; the tool does the arithmetic and shows the
formula + the denominators. It is decision-support, not a substitute for a floor check:
validate every figure against the line's actual data, state the ideal-cycle-time basis
and the planned/unplanned downtime split, and never quote a number with undefined
denominators (best-practices/oee-denominators-must-be-defined.md).

Examples
--------
  # OEE for an 8h shift in SECONDS (keep every time input in one unit): 28800s scheduled,
  # 1800s planned maint, 4320s breakdown+setup, 1.0s ideal cycle, 21000 made, 20580 good
  python3 mfg_calc.py oee --scheduled-time 28800 --planned-downtime 1800 \
      --unplanned-downtime 4320 --ideal-cycle-time 1.0 --total-count 21000 --good-count 20580

  # Takt for 450 units across a 27000s available shift, measured 55s cycle
  python3 mfg_calc.py takt --available-time 27000 --demand 450 --cycle-time 55

  # Net requirement + load: gross 1200, on-hand 300, receipts 100, safety 150,
  # 2.0 min/unit, 3 stations, 8h shift, 2 shifts, 0.85 utilization
  python3 mfg_calc.py capacity --gross 1200 --on-hand 300 --scheduled-receipts 100 \
      --safety-stock 150 --cycle-time 2.0 --stations 3 --shift-hours 8 --shifts 2 --util 0.85
"""

from __future__ import annotations

import argparse
import sys


def _require_positive(name: str, x: float, *, strict: bool = True) -> None:
    if strict and x <= 0.0:
        print(f"error: {name} must be > 0, got {x}", file=sys.stderr)
        raise SystemExit(2)
    if not strict and x < 0.0:
        print(f"error: {name} must be >= 0, got {x}", file=sys.stderr)
        raise SystemExit(2)


def _verdict(x: float, good: float = 0.85) -> str:
    """A directional read on a 0-1 factor — a guide, not a benchmark to chase."""
    if x >= good:
        return "strong"
    if x >= 0.60:
        return "fair"
    return "weak"


def cmd_oee(args: argparse.Namespace) -> int:
    _require_positive("--scheduled-time", args.scheduled_time)
    _require_positive("--planned-downtime", args.planned_downtime, strict=False)
    _require_positive("--unplanned-downtime", args.unplanned_downtime, strict=False)
    _require_positive("--ideal-cycle-time", args.ideal_cycle_time)
    _require_positive("--total-count", args.total_count)
    _require_positive("--good-count", args.good_count, strict=False)

    if args.good_count > args.total_count:
        print("error: --good-count cannot exceed --total-count", file=sys.stderr)
        return 2

    planned_time = args.scheduled_time - args.planned_downtime
    if planned_time <= 0:
        print("error: planned production time (scheduled - planned downtime) must be > 0",
              file=sys.stderr)
        return 2
    run_time = planned_time - args.unplanned_downtime
    if run_time <= 0:
        print("error: run time (planned - unplanned downtime) must be > 0", file=sys.stderr)
        return 2

    availability = run_time / planned_time
    performance = (args.ideal_cycle_time * args.total_count) / run_time
    quality = args.good_count / args.total_count
    oee = availability * performance * quality

    scrap = args.total_count - args.good_count

    print("OEE — Availability x Performance x Quality")
    print(f"  scheduled time        : {args.scheduled_time:g}")
    print(f"  planned downtime       : {args.planned_downtime:g}  (excluded from the denominator)")
    print(f"  -> planned prod. time  : {planned_time:g}")
    print(f"  unplanned downtime     : {args.unplanned_downtime:g}  (the Availability loss)")
    print(f"  -> run time            : {run_time:g}")
    print(f"  ideal cycle time       : {args.ideal_cycle_time:g}  (MUST be demonstrated best, not a spec)")
    print(f"  total / good count     : {args.total_count:g} / {args.good_count:g}  (scrap+rework {scrap:g})")
    print()
    print(f"  Availability = run/planned       : {availability:.4f}  ({_verdict(availability)})")
    print(f"  Performance  = ideal*count/run   : {performance:.4f}  ({_verdict(performance)})")
    print(f"  Quality      = good/total        : {quality:.4f}  ({_verdict(quality)})")
    print(f"  -> OEE                           : {oee:.4f}  ({oee * 100:.1f}%)")
    if performance > 1.0:
        print("  WARNING: Performance > 1.0 — the ideal cycle time is sandbagged (slower than")
        print("           actual). Re-set it to the demonstrated best repeatable rate.")
    print()
    print("  six big losses:  A = breakdowns + setup/changeover (in unplanned downtime)")
    print("                   P = minor stops + reduced speed   (the Performance gap)")
    print("                   Q = scrap + rework                (the Quality gap)")
    print("  formula: OEE = (run/planned) * (ideal*total/run) * (good/total)")
    print("  reminder: an OEE number with an undefined ideal cycle time or planned/unplanned")
    print("            split is theater — state the denominators (oee-denominators-must-be-defined).")
    return 0


def cmd_takt(args: argparse.Namespace) -> int:
    _require_positive("--available-time", args.available_time)
    _require_positive("--demand", args.demand)

    takt = args.available_time / args.demand
    required_rate = args.demand / args.available_time

    print("Takt — the customer demand drumbeat")
    print(f"  available time        : {args.available_time:g}  (per period, e.g. seconds/shift)")
    print(f"  demand units          : {args.demand:g}")
    print(f"  -> takt time          : {takt:.4f}  (time allowed per unit)")
    print(f"  -> required rate      : {required_rate:.6f}  (units per time)")
    print("  formula: takt = available_time / demand")

    if args.cycle_time is not None:
        _require_positive("--cycle-time", args.cycle_time)
        slack = takt - args.cycle_time
        if args.cycle_time > takt:
            shortfall = args.available_time / args.cycle_time
            print()
            print(f"  measured cycle time   : {args.cycle_time:g}  (SLOWER than takt by {-slack:.4f})")
            print(f"  -> verdict            : MISSES DEMAND — capacity {shortfall:.1f} units < {args.demand:g} demand")
            print("     fix the constraint (TOC: exploit before you buy) or re-time the plan;")
            print("     do NOT just run the machine faster than its sustainable rate.")
        elif args.cycle_time < takt:
            print()
            print(f"  measured cycle time   : {args.cycle_time:g}  (FASTER than takt by {slack:.4f})")
            print("  -> verdict            : AHEAD OF TAKT — running faster makes inventory, not money.")
            print("     Building ahead of demand is over-production, the loss that hides every other.")
            print("     Pace to takt (produce-to-takt-not-to-machine-speed).")
        else:
            print()
            print(f"  measured cycle time   : {args.cycle_time:g}  (matches takt)")
            print("  -> verdict            : ON TAKT — the line is paced to demand.")
        print("  the gap (takt - cycle), not the machine's top speed, is the diagnostic signal.")
    return 0


def cmd_capacity(args: argparse.Namespace) -> int:
    _require_positive("--gross", args.gross)
    _require_positive("--on-hand", args.on_hand, strict=False)
    _require_positive("--scheduled-receipts", args.scheduled_receipts, strict=False)
    _require_positive("--safety-stock", args.safety_stock, strict=False)
    _require_positive("--cycle-time", args.cycle_time)
    _require_positive("--stations", args.stations)
    _require_positive("--shift-hours", args.shift_hours)
    _require_positive("--shifts", args.shifts)
    if not 0.0 < args.util <= 1.0:
        print(f"error: --util must be in (0, 1], got {args.util}", file=sys.stderr)
        return 2

    net = max(0.0, args.gross - args.on_hand - args.scheduled_receipts + args.safety_stock)
    required_capacity = net * args.cycle_time
    # available capacity in the same time unit as cycle_time (minutes by convention)
    available_capacity = args.stations * args.shift_hours * 60.0 * args.shifts * args.util

    print("Capacity — MRP net requirement + load vs the finite rate")
    print(f"  gross requirement     : {args.gross:g}")
    print(f"  on-hand               : {args.on_hand:g}")
    print(f"  scheduled receipts    : {args.scheduled_receipts:g}")
    print(f"  safety stock          : {args.safety_stock:g}  (a stated decision, not a default)")
    print(f"  -> net requirement    : {net:g}")
    print("  formula: net = max(0, gross - on_hand - scheduled_receipts + safety_stock)")
    if net == 0.0:
        print("  net requirement is 0 — on-hand + receipts cover gross + safety; no order needed.")
        return 0

    print()
    print(f"  cycle time / unit     : {args.cycle_time:g}  (same time unit as below; minutes by convention)")
    print(f"  -> required capacity  : {required_capacity:g}  (net * cycle_time — time the work needs)")
    print(f"  stations              : {args.stations:g}")
    print(f"  shift hours x shifts  : {args.shift_hours:g} x {args.shifts:g}")
    print(f"  utilization           : {args.util:g}")
    print(f"  -> available capacity : {available_capacity:g}  (stations * hours * 60 * shifts * util)")

    if available_capacity <= 0:
        print("error: available capacity computed as <= 0", file=sys.stderr)
        return 2
    load_pct = required_capacity / available_capacity
    print()
    print(f"  -> load               : {load_pct:.4f}  ({load_pct * 100:.1f}% of finite capacity)")
    if load_pct > 1.0:
        over = required_capacity - available_capacity
        print("  -> verdict            : OVERLOADED — the plan exceeds the bottleneck's finite rate.")
        print(f"     short by {over:g} capacity-units. Level dates, add capacity, or re-cut the lot;")
        print("     do NOT plan to infinite capacity (plan-to-the-constraint-not-infinite-capacity).")
    else:
        print("  -> verdict            : FEASIBLE on the stated rate — load is within finite capacity.")
        print("     (Feasible != comfortable; state the assumptions behind the rate.)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="mfg_calc.py",
        description="Manufacturing-operations decision calculator (stdlib only). "
        "Decision-support, not a substitute for a floor check — state every denominator.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    oee = sub.add_parser("oee", help="OEE = Availability x Performance x Quality (denominators stated)")
    oee.add_argument("--scheduled-time", type=float, required=True,
                     help="total scheduled time for the period (e.g. minutes/shift)")
    oee.add_argument("--planned-downtime", type=float, default=0.0,
                     help="planned downtime excluded from the denominator (default 0)")
    oee.add_argument("--unplanned-downtime", type=float, default=0.0,
                     help="unplanned downtime — breakdowns + setup/changeover (default 0)")
    oee.add_argument("--ideal-cycle-time", type=float, required=True,
                     help="demonstrated best repeatable time/unit (NOT a marketing spec)")
    oee.add_argument("--total-count", type=float, required=True,
                     help="total units produced (good + scrap/rework)")
    oee.add_argument("--good-count", type=float, required=True,
                     help="good units (first-pass, no rework)")
    oee.set_defaults(func=cmd_oee)

    takt = sub.add_parser("takt", help="takt = available_time / demand, vs measured cycle time")
    takt.add_argument("--available-time", type=float, required=True,
                      help="available production time per period (same unit as --cycle-time)")
    takt.add_argument("--demand", type=float, required=True, help="demand units for the period")
    takt.add_argument("--cycle-time", type=float, default=None,
                      help="measured cycle time/unit — adds the takt-vs-cycle verdict")
    takt.set_defaults(func=cmd_takt)

    cap = sub.add_parser("capacity", help="MRP net requirement + load vs finite capacity")
    cap.add_argument("--gross", type=float, required=True, help="gross requirement")
    cap.add_argument("--on-hand", type=float, default=0.0, help="on-hand inventory (default 0)")
    cap.add_argument("--scheduled-receipts", type=float, default=0.0,
                     help="scheduled receipts / open orders (default 0)")
    cap.add_argument("--safety-stock", type=float, default=0.0,
                     help="safety stock to hold (a stated decision; default 0)")
    cap.add_argument("--cycle-time", type=float, required=True,
                     help="time per unit at the resource (same unit as available capacity)")
    cap.add_argument("--stations", type=float, default=1.0, help="parallel stations/machines (default 1)")
    cap.add_argument("--shift-hours", type=float, default=8.0, help="hours per shift (default 8)")
    cap.add_argument("--shifts", type=float, default=1.0, help="shifts per period (default 1)")
    cap.add_argument("--util", type=float, default=1.0,
                     help="utilization fraction in (0,1] (default 1.0)")
    cap.set_defaults(func=cmd_capacity)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
