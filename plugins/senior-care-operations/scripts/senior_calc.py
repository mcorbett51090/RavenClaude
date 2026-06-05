#!/usr/bin/env python3
"""senior_calc.py — a zero-dependency senior-care operations decision calculator.

Removes arithmetic error from four recurring senior-care operations decisions an
executive director / regional operator / analyst runs constantly:

  ppd-staffing    Acuity-weighted HOURS-PER-RESIDENT-DAY staffing. Converts an
                  acuity census (residents per care tier x care-minutes/day per
                  tier) into required care hours/day, the resulting acuity-based
                  PPD, required FTEs, and the gap vs current staffing. Pairs with
                  knowledge/senior-care-acuity-staffing-ppd-decision-tree.md.

  occupancy-rev   Occupancy as a FLOW, with revenue at stake. Projects month-end
                  census from start census + move-ins - move-outs, the occupancy
                  %, and the monthly revenue gap between current and target
                  occupancy at a given average rate. Pairs with
                  knowledge/senior-care-decision-trees.md ("Why Occupancy ...").

  move-in-funnel  The two-stage sales funnel. Takes inquiries + the two
                  conversion rates (inquiry->tour, tour->move-in), prints
                  projected tours / move-ins / overall conversion, flags the
                  leaking stage against benchmark, and shows cost-per-move-in.
                  Pairs with the move-in-funnel scenario.

  payer-mix       SNF/AL payer-mix margin. Takes resident-days and a per-payer
                  rate + variable cost, prints revenue / margin per payer and
                  blended margin, then the margin delta of shifting N points of
                  mix from one payer to another. Pairs with the payer-mix scenario.

This is a CALCULATOR, not a data source — it does not fetch benchmarks, rates,
or live costs. The user supplies every input; the tool does the arithmetic and
shows the formula. Stdlib only (argparse); runs anywhere Python 3.8+ is present.

IMPORTANT: outputs are decision-support, not clinical, legal, regulatory, or
licensed financial advice (see ../CLAUDE.md SS2). Validate every figure against
the community's actual data and the resident state's current regulation before
any deliverable (CLAUDE.md SS3 #8). Acuity/clinical determinations route to the
qualified clinician; survey/regulatory determinations route to the state agency.

Examples
--------
  # Acuity-based PPD: 20 low (45 min/day), 30 medium (90), 15 high (150);
  # currently staffing 95 caregiver hours/day across 60 residents
  python3 senior_calc.py ppd-staffing \\
      --tier low:20:45 --tier medium:30:90 --tier high:15:150 \\
      --current-hours 95 --fte-hours 8

  # Occupancy as a flow: 76 occupied of 90 units, +6 move-ins, -4 move-outs,
  # target 90% occupancy at $5,676 avg monthly rate
  python3 senior_calc.py occupancy-rev --capacity 90 --start 76 \\
      --move-ins 6 --move-outs 4 --target-occupancy 90% --avg-rate 5676

  # Move-in funnel: 120 inquiries, 22% inquiry->tour, 31% tour->move-in,
  # $2,400 cost per move-in
  python3 senior_calc.py move-in-funnel --inquiries 120 \\
      --inquiry-to-tour 22% --tour-to-move-in 31% --cost-per-move-in 2400

  # Payer mix: shift 5 points of resident-days from medicaid to medicare
  python3 senior_calc.py payer-mix \\
      --payer medicaid:1200:245:210 --payer medicare:300:620:340 \\
      --payer private:200:400:230 --shift-points 5 --shift-from medicaid \\
      --shift-to medicare
"""

from __future__ import annotations

import argparse
import sys


def _parse_rate(s: str) -> float:
    """Parse a rate like '29%' or '0.29' into a fraction (0.29)."""
    s = s.strip()
    try:
        return float(s[:-1]) / 100.0 if s.endswith("%") else float(s)
    except ValueError:
        raise argparse.ArgumentTypeError(f"must be like '29%' or '0.29', got {s!r}")


def _parse_tier(s: str) -> tuple:
    """Parse 'name:count:minutes_per_day' into (name, count, minutes)."""
    parts = s.split(":")
    if len(parts) != 3:
        raise argparse.ArgumentTypeError(
            f"--tier must be name:count:minutes_per_day, got {s!r}"
        )
    name = parts[0].strip()
    try:
        count = float(parts[1])
        minutes = float(parts[2])
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"--tier count and minutes must be numbers, got {s!r}"
        )
    if count < 0 or minutes < 0:
        raise argparse.ArgumentTypeError(f"--tier count/minutes must be >= 0, got {s!r}")
    return (name, count, minutes)


def _parse_payer(s: str) -> tuple:
    """Parse 'name:days:rate_per_day:variable_cost_per_day' into a tuple."""
    parts = s.split(":")
    if len(parts) != 4:
        raise argparse.ArgumentTypeError(
            f"--payer must be name:days:rate_per_day:var_cost_per_day, got {s!r}"
        )
    name = parts[0].strip()
    try:
        days = float(parts[1])
        rate = float(parts[2])
        var_cost = float(parts[3])
    except ValueError:
        raise argparse.ArgumentTypeError(f"--payer numbers invalid, got {s!r}")
    if days < 0:
        raise argparse.ArgumentTypeError(f"--payer days must be >= 0, got {s!r}")
    return (name, days, rate, var_cost)


def cmd_ppd_staffing(args: argparse.Namespace) -> int:
    if args.fte_hours <= 0:
        print("error: --fte-hours must be > 0", file=sys.stderr)
        return 2
    residents = sum(t[1] for t in args.tier)
    if residents <= 0:
        print("error: total residents across --tier must be > 0", file=sys.stderr)
        return 2

    total_minutes = sum(t[1] * t[2] for t in args.tier)
    required_hours = total_minutes / 60.0
    ppd = required_hours / residents
    required_ftes = required_hours / args.fte_hours

    print("Acuity-based PPD staffing")
    print(f"  residents (all tiers)   : {residents:,.0f}")
    print("  tier     | residents | min/day | care-hours/day")
    print("  ---------+-----------+---------+---------------")
    for name, count, minutes in args.tier:
        print(f"  {name:<8} | {count:>9,.0f} | {minutes:>7,.0f} | {count * minutes / 60.0:>13,.1f}")
    print()
    print(f"  required care-hours/day : {required_hours:,.1f}")
    print(f"  -> acuity-based PPD     : {ppd:,.2f} care-hours per resident-day")
    print(f"  -> required FTEs        : {required_ftes:,.2f} (at {args.fte_hours:g}h/FTE-day)")

    if args.current_hours is not None:
        gap_hours = required_hours - args.current_hours
        current_ppd = args.current_hours / residents
        print()
        print(f"  current care-hours/day  : {args.current_hours:,.1f} (PPD {current_ppd:,.2f})")
        if gap_hours > 0:
            print(f"  -> UNDERSTAFFED by      : {gap_hours:,.1f} care-hours/day "
                  f"({gap_hours / args.fte_hours:,.2f} FTE)")
            print("     close the gap before adding net headcount: reallocate over-staffed")
            print("     halls to acuity first, then size the residual hire vs the agency rate.")
        elif gap_hours < 0:
            print(f"  -> OVER-STAFFED by      : {-gap_hours:,.1f} care-hours/day "
                  f"({-gap_hours / args.fte_hours:,.2f} FTE) — reallocate to higher-acuity need")
        else:
            print("  -> staffing matches acuity-based requirement")
    print("  note: acuity tiers/care-minutes are YOUR clinical inputs; validate against the")
    print("        resident state's staffing rule (AL is state-set; the federal SNF 3.48-HPRD")
    print("        rule is currently rescinded). Clinical acuity routes to the clinician.")
    return 0


def cmd_occupancy_rev(args: argparse.Namespace) -> int:
    if args.capacity <= 0:
        print("error: --capacity must be > 0", file=sys.stderr)
        return 2
    if not 0.0 < args.target_occupancy <= 1.0:
        print("error: --target-occupancy must be in (0%, 100%]", file=sys.stderr)
        return 2

    end_census = args.start + args.move_ins - args.move_outs
    end_occupancy = end_census / args.capacity
    target_census = args.target_occupancy * args.capacity
    net_flow = args.move_ins - args.move_outs

    print("Occupancy as a flow + revenue at stake")
    print(f"  capacity (units)        : {args.capacity:,.0f}")
    print(f"  start census            : {args.start:,.0f} ({args.start / args.capacity * 100:.1f}%)")
    print(f"  + move-ins              : {args.move_ins:,.0f}")
    print(f"  - move-outs             : {args.move_outs:,.0f}")
    print(f"  = net flow              : {net_flow:+,.0f}")
    print(f"  -> end census           : {end_census:,.0f} ({end_occupancy * 100:.1f}%)")
    print(f"  target occupancy        : {args.target_occupancy * 100:.1f}% "
          f"= {target_census:,.1f} units")

    if args.avg_rate is not None:
        units_to_target = target_census - end_census
        monthly_gap = units_to_target * args.avg_rate
        print()
        print(f"  avg monthly rate/unit   : {args.avg_rate:,.0f}")
        if units_to_target > 0:
            print(f"  -> units below target   : {units_to_target:,.1f}")
            print(f"  -> monthly revenue gap  : {monthly_gap:,.0f} "
                  f"(annualized {monthly_gap * 12:,.0f})")
            print("     decompose the gap by SEGMENT and split move-ins vs move-outs before")
            print("     pricing: a community-wide discount is the lowest-precision lever.")
        else:
            print("  -> at or above target occupancy")
    print("  note: occupancy is a flow, not a point. Net flow < 0 means move-outs are")
    print("        outrunning move-ins — split avoidable vs unavoidable before acting.")
    return 0


def cmd_move_in_funnel(args: argparse.Namespace) -> int:
    if args.inquiries < 0:
        print("error: --inquiries must be >= 0", file=sys.stderr)
        return 2
    for label, val in (("--inquiry-to-tour", args.inquiry_to_tour),
                       ("--tour-to-move-in", args.tour_to_move_in)):
        if not 0.0 <= val <= 1.0:
            print(f"error: {label} must be in [0%, 100%]", file=sys.stderr)
            return 2

    tours = args.inquiries * args.inquiry_to_tour
    move_ins = tours * args.tour_to_move_in
    overall = args.inquiry_to_tour * args.tour_to_move_in

    # Benchmark midpoints (dated 2026; [verify-at-use] — see scenarios/knowledge).
    bench_i2t = 0.29       # inquiry->tour ~29%
    bench_t2m = 0.315      # tour->move-in ~29-34% midpoint
    bench_overall = 0.135  # overall ~12-15% midpoint

    print("Move-in funnel — two-stage conversion")
    print(f"  inquiries               : {args.inquiries:,.0f}")
    print(f"  inquiry -> tour         : {args.inquiry_to_tour * 100:.1f}% "
          f"(benchmark ~{bench_i2t * 100:.0f}%) -> {tours:,.1f} tours")
    print(f"  tour -> move-in         : {args.tour_to_move_in * 100:.1f}% "
          f"(benchmark ~{bench_t2m * 100:.0f}%) -> {move_ins:,.1f} move-ins")
    print(f"  -> overall conversion   : {overall * 100:.2f}% "
          f"(benchmark ~{bench_overall * 100:.0f}%)")

    leaks = []
    if args.inquiry_to_tour < bench_i2t:
        leaks.append("inquiry->tour (fix lead-response speed + follow-up cadence first)")
    if args.tour_to_move_in < bench_t2m:
        leaks.append("tour->move-in (fix tour experience + post-tour close process)")
    print()
    if leaks:
        print("  -> LEAKING STAGE(S) below benchmark:")
        for leak in leaks:
            print(f"       - {leak}")
        print("     fix the measured leak before buying more inquiries — volume into a")
        print("     leaking funnel just raises cost-per-move-in.")
    else:
        print("  -> both stages at/above benchmark — volume growth is the lever, not conversion.")

    if args.cost_per_move_in is not None and move_ins > 0:
        total_spend = args.cost_per_move_in * move_ins
        print()
        print(f"  cost per move-in        : {args.cost_per_move_in:,.0f}")
        print(f"  implied spend for {move_ins:,.0f} move-ins : {total_spend:,.0f}")
        print("     reminder: owned-channel CPMI is far below referral-agency CPMI — check the")
        print("     channel mix, not just the volume (memory-care referral fees can top $7-12k).")
    return 0


def cmd_payer_mix(args: argparse.Namespace) -> int:
    payers = {p[0]: p for p in args.payer}
    if len(payers) != len(args.payer):
        print("error: duplicate --payer name", file=sys.stderr)
        return 2
    total_days = sum(p[1] for p in args.payer)
    if total_days <= 0:
        print("error: total resident-days across --payer must be > 0", file=sys.stderr)
        return 2

    print("Payer-mix margin")
    print("  payer    | days | mix%  | rate/day | margin/day | revenue   | margin")
    print("  ---------+------+-------+----------+------------+-----------+----------")
    total_rev = 0.0
    total_margin = 0.0
    for name, days, rate, var_cost in args.payer:
        mix = days / total_days
        margin_day = rate - var_cost
        rev = rate * days
        margin = margin_day * days
        total_rev += rev
        total_margin += margin
        print(f"  {name:<8} | {days:>4,.0f} | {mix * 100:>4.1f}% | {rate:>8,.0f} | "
              f"{margin_day:>10,.0f} | {rev:>9,.0f} | {margin:>8,.0f}")
    blended_margin_day = total_margin / total_days
    print()
    print(f"  total resident-days     : {total_days:,.0f}")
    print(f"  total revenue           : {total_rev:,.0f}")
    print(f"  total margin            : {total_margin:,.0f}")
    print(f"  -> blended margin/day   : {blended_margin_day:,.2f}")

    if args.shift_points is not None:
        if args.shift_from not in payers or args.shift_to not in payers:
            print("error: --shift-from/--shift-to must match a --payer name", file=sys.stderr)
            return 2
        shift_days = (args.shift_points / 100.0) * total_days
        from_p = payers[args.shift_from]
        to_p = payers[args.shift_to]
        if shift_days > from_p[1]:
            print(f"error: cannot shift {shift_days:,.1f} days from {args.shift_from} "
                  f"(only {from_p[1]:,.0f} days)", file=sys.stderr)
            return 2
        from_margin_day = from_p[2] - from_p[3]
        to_margin_day = to_p[2] - to_p[3]
        delta = shift_days * (to_margin_day - from_margin_day)
        print()
        print(f"  shift {args.shift_points:g} pts of days: {args.shift_from} -> {args.shift_to} "
              f"({shift_days:,.1f} days)")
        print(f"    {args.shift_from} margin/day : {from_margin_day:,.0f}")
        print(f"    {args.shift_to} margin/day : {to_margin_day:,.0f}")
        print(f"  -> margin delta         : {delta:+,.0f} "
              f"(total margin would be {total_margin + delta:,.0f})")
        print("     mix drives margin: a small shift toward higher-reimbursement days can beat")
        print("     a larger any-payer occupancy bump. Use payer-SPECIFIC rates (MA != FFS).")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="senior_calc.py",
        description="Senior-care operations decision calculator (stdlib only). "
        "Decision-support, not clinical/legal/regulatory/financial advice — validate every input.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    ppd = sub.add_parser("ppd-staffing", help="Acuity-weighted hours-per-resident-day staffing")
    ppd.add_argument("--tier", type=_parse_tier, action="append", required=True,
                     metavar="NAME:COUNT:MIN_PER_DAY",
                     help="an acuity tier (repeatable): name:residents:care-minutes-per-day")
    ppd.add_argument("--fte-hours", type=float, default=8.0,
                     help="productive care hours per FTE per day (default 8)")
    ppd.add_argument("--current-hours", type=float, default=None,
                     help="current total caregiver care-hours/day, for the gap (optional)")
    ppd.set_defaults(func=cmd_ppd_staffing)

    occ = sub.add_parser("occupancy-rev", help="Occupancy as a flow + revenue at stake")
    occ.add_argument("--capacity", type=float, required=True, help="total units/beds")
    occ.add_argument("--start", type=float, required=True, help="starting occupied units")
    occ.add_argument("--move-ins", type=float, default=0.0, help="move-ins in the period")
    occ.add_argument("--move-outs", type=float, default=0.0, help="move-outs in the period")
    occ.add_argument("--target-occupancy", type=_parse_rate, default=0.90,
                     help="target occupancy (default 90%%)")
    occ.add_argument("--avg-rate", type=float, default=None,
                     help="avg monthly rate per unit, for the revenue gap (optional)")
    occ.set_defaults(func=cmd_occupancy_rev)

    fun = sub.add_parser("move-in-funnel", help="Two-stage move-in funnel conversion")
    fun.add_argument("--inquiries", type=float, required=True, help="inquiries in the period")
    fun.add_argument("--inquiry-to-tour", type=_parse_rate, required=True,
                     help="inquiry-to-tour conversion rate (e.g. 29%%)")
    fun.add_argument("--tour-to-move-in", type=_parse_rate, required=True,
                     help="tour-to-move-in conversion rate (e.g. 31%%)")
    fun.add_argument("--cost-per-move-in", type=float, default=None,
                     help="cost per move-in, for implied spend (optional)")
    fun.set_defaults(func=cmd_move_in_funnel)

    pay = sub.add_parser("payer-mix", help="Payer-mix margin + mix-shift sensitivity")
    pay.add_argument("--payer", type=_parse_payer, action="append", required=True,
                     metavar="NAME:DAYS:RATE:VAR_COST",
                     help="a payer (repeatable): name:resident-days:rate/day:variable-cost/day")
    pay.add_argument("--shift-points", type=float, default=None,
                     help="percentage points of resident-days to shift (optional)")
    pay.add_argument("--shift-from", type=str, default=None, help="payer to shift days FROM")
    pay.add_argument("--shift-to", type=str, default=None, help="payer to shift days TO")
    pay.set_defaults(func=cmd_payer_mix)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
