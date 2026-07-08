#!/usr/bin/env python3
"""production_calc.py — a zero-dependency film/video production decision calculator.

Removes arithmetic error from three recurring production-economics decisions a
line producer / production manager / production-finance analyst runs constantly:

  shoot-day-cost  The all-in cost of a shoot day, built up the way a line
                  producer must: base crew cost + projected OVERTIME (1.5x past
                  the contracted day, 2x past the double-time threshold) + a
                  payroll FRINGE/burden load on every taxable dollar + flat
                  per-day gear/location/catering. Prints the straight-time base,
                  the overtime premium, the fringe load, and the loaded day cost
                  — so a "10-hour day" quote isn't silently a 14-hour spend.
                  Pairs with knowledge/production-economics.md and the
                  overtime/turnaround best-practice rules.

  contingency     The top-sheet contingency math: contingency dollars at a given
                  % of the contingency BASE (the industry convention is a % of
                  below-the-line + post, not the whole budget), the grand total,
                  and — given dollars already drawn — the remaining buffer and
                  the % of the shoot still unprotected. Flags when the burn rate
                  will exhaust the buffer before wrap. Pairs with the
                  budget-to-a-top-sheet and contingency-managed-not-hoped rules.

  overtime-burden The marginal cost of holding the crew past the contracted day:
                  the Nth overtime hour's true cost = hourly rate x OT multiplier
                  x (1 + fringe). Shows the straight-time hour vs the time-and-a-
                  half hour vs the double-time hour, so "just one more hour" is
                  priced before the AD calls it. Pairs with the turnaround-
                  violation and overtime best-practice rules.

This is a CALCULATOR, not a data source — it does NOT fetch union minimums,
fringe rates, day rates, or any market figure. The user supplies every input;
the tool does the arithmetic and shows the formula. Stdlib only (argparse);
runs anywhere Python 3.8+ is present.

IMPORTANT: outputs are decision-support, not union, legal, or licensed financial
advice (see ../CLAUDE.md section 2). Union overtime/turnaround/meal-penalty rules
vary by local, agreement, and year — validate every rate and threshold against
the project's actual deal memos and the governing agreement before any
deliverable (CLAUDE.md section 3 #8).

Examples
--------
  # Shoot-day cost: $18k/hr-equivalent... no — crew base $24,000 for a contracted
  # 10-hour day, projecting 13 worked hours, double-time after 12, 30% fringe,
  # plus $9,000 flat for gear+location+catering on the day
  python3 production_calc.py shoot-day-cost --crew-base 24000 \\
      --contracted-hours 10 --worked-hours 13 --dt-after 12 \\
      --fringe 30% --flat-costs 9000

  # Contingency: 10% of a $1,200,000 below-the-line+post base, $1,350,000 grand
  # total already, $48,000 drawn at day 12 of an 18-day shoot
  python3 production_calc.py contingency --base 1200000 --pct 10% \\
      --pre-contingency-total 1350000 --drawn 48000 \\
      --days-elapsed 12 --days-total 18

  # Overtime burden: a $95/hr crew position, double-time after 12, 28% fringe
  python3 production_calc.py overtime-burden --rate 95 --dt-after 12 --fringe 28%
"""

from __future__ import annotations

import argparse
import sys


def _parse_rate(s: str) -> float:
    """Parse a rate like '30%' or '0.30' into a fraction (0.30)."""
    s = s.strip()
    try:
        return float(s[:-1]) / 100.0 if s.endswith("%") else float(s)
    except ValueError:
        raise argparse.ArgumentTypeError(f"must be like '30%' or '0.30', got {s!r}")


def cmd_shoot_day_cost(args: argparse.Namespace) -> int:
    if args.contracted_hours <= 0:
        print("error: --contracted-hours must be > 0", file=sys.stderr)
        return 2
    if args.worked_hours <= 0:
        print("error: --worked-hours must be > 0", file=sys.stderr)
        return 2
    if args.dt_after <= args.contracted_hours:
        print("error: --dt-after must be > --contracted-hours", file=sys.stderr)
        return 2
    if not 0.0 <= args.fringe < 2.0:
        print("error: --fringe must be in [0%, 200%)", file=sys.stderr)
        return 2

    # The crew base is the straight-time cost of the contracted day, so the
    # implied blended straight-time hourly is base / contracted hours.
    st_hourly = args.crew_base / args.contracted_hours

    worked = args.worked_hours
    st_hours = min(worked, args.contracted_hours)
    ot_15_hours = max(0.0, min(worked, args.dt_after) - args.contracted_hours)
    ot_2_hours = max(0.0, worked - args.dt_after)

    st_cost = st_hourly * st_hours
    ot_15_cost = st_hourly * 1.5 * ot_15_hours
    ot_2_cost = st_hourly * 2.0 * ot_2_hours
    labor = st_cost + ot_15_cost + ot_2_cost
    ot_premium = labor - st_hourly * worked  # the premium over flat-rate hours

    fringe_load = labor * args.fringe  # fringe is on labor only, not flat costs
    loaded = labor + fringe_load + args.flat_costs

    print("Shoot-day cost — loaded build-up")
    print(
        f"  crew base (straight-time day)  : {args.crew_base:>12,.0f}  ({args.contracted_hours:g}h contracted)"
    )
    print(f"  implied straight-time hourly   : {st_hourly:>12,.2f}")
    print(
        f"  worked hours                   : {worked:>12g}  (ST {st_hours:g} / OT1.5 {ot_15_hours:g} / OT2 {ot_2_hours:g})"
    )
    print("  ------------------------------------------")
    print(f"  straight-time labor            : {st_cost:>12,.0f}")
    print(f"  overtime @1.5x                 : {ot_15_cost:>12,.0f}")
    print(f"  overtime @2.0x (double-time)   : {ot_2_cost:>12,.0f}")
    print(f"  = labor subtotal               : {labor:>12,.0f}")
    print(f"  overtime premium (over flat)   : {ot_premium:>12,.0f}")
    print(f"  fringe/burden @{args.fringe * 100:g}% on labor   : {fringe_load:>12,.0f}")
    print(f"  flat (gear/location/catering)  : {args.flat_costs:>12,.0f}")
    print("  ==========================================")
    print(f"  => LOADED SHOOT-DAY COST       : {loaded:>12,.0f}")
    if worked > args.contracted_hours:
        contracted_day_spend = (
            st_hourly * args.contracted_hours * (1 + args.fringe) + args.flat_costs
        )
        extra = ot_premium + ot_premium * args.fringe
        over_hours = worked - args.contracted_hours
        if contracted_day_spend > 0:
            overrun_pct = (loaded / contracted_day_spend - 1) * 100
            print(
                f"  note: running {over_hours:g}h past the contracted day cost an extra "
                f"{extra:,.0f} (premium+fringe) — ~{overrun_pct:.0f}% over the contracted-day spend."
            )
        else:
            # A zero contracted-day spend (e.g. --crew-base 0 and no flat costs) has
            # no meaningful percentage — report the dollar premium without the ratio.
            print(
                f"  note: running {over_hours:g}h past the contracted day cost an extra "
                f"{extra:,.0f} (premium+fringe)."
            )
    print("  reminder: OT thresholds, multipliers, and fringe rates are deal-memo +")
    print("            governing-agreement specific — validate before any deliverable (sec 3 #8).")
    return 0


def cmd_contingency(args: argparse.Namespace) -> int:
    if args.base < 0:
        print("error: --base must be >= 0", file=sys.stderr)
        return 2
    if not 0.0 <= args.pct < 1.0:
        print("error: --pct must be in [0%, 100%)", file=sys.stderr)
        return 2

    contingency = args.base * args.pct
    grand_total = (
        args.pre_contingency_total if args.pre_contingency_total is not None else args.base
    ) + contingency

    print("Top-sheet contingency")
    print(f"  contingency base (BTL + post)  : {args.base:>12,.0f}")
    print(f"  contingency rate               : {args.pct * 100:g}%")
    print(f"  => contingency reserve         : {contingency:>12,.0f}")
    if args.pre_contingency_total is not None:
        print(f"  pre-contingency grand total    : {args.pre_contingency_total:>12,.0f}")
    print(f"  => GRAND TOTAL (with reserve)  : {grand_total:>12,.0f}")

    if args.drawn is not None:
        if args.drawn < 0:
            print("error: --drawn must be >= 0", file=sys.stderr)
            return 2
        remaining = contingency - args.drawn
        drawn_pct = (args.drawn / contingency * 100) if contingency else 0.0
        print()
        print(
            f"  drawn to date                  : {args.drawn:>12,.0f}  ({drawn_pct:.0f}% of reserve)"
        )
        print(f"  => remaining buffer            : {remaining:>12,.0f}")
        if remaining < 0:
            print(
                "  => CONTINGENCY EXHAUSTED — overage is now unfunded; escalate to EP/financier (sec 3 #4)."
            )

        if args.days_elapsed is not None and args.days_total is not None:
            if (
                args.days_elapsed <= 0
                or args.days_total <= 0
                or args.days_elapsed > args.days_total
            ):
                print("  (skip burn projection: need 0 < days-elapsed <= days-total)")
                return 0
            burn_per_day = args.drawn / args.days_elapsed
            days_left = args.days_total - args.days_elapsed
            projected_draw = burn_per_day * args.days_total
            print()
            print(
                f"  burn rate                      : {burn_per_day:>12,.0f} / shoot-day "
                f"(day {args.days_elapsed:g} of {args.days_total:g})"
            )
            print(f"  projected total draw @ wrap    : {projected_draw:>12,.0f}")
            if projected_draw > contingency and burn_per_day > 0:
                exhaust_day = contingency / burn_per_day
                print(
                    f"  => AT THIS BURN, RESERVE EXHAUSTS at day ~{exhaust_day:.1f} "
                    f"— {days_left:g} shoot-days still ahead. Re-forecast NOW (sec 3 #4)."
                )
            else:
                print(
                    f"  => at this burn, reserve holds to wrap ({remaining - burn_per_day * days_left:,.0f} "
                    "projected to spare). Keep tracking — overage is managed, not hoped."
                )
    print("  reminder: contingency convention is % of BTL+post, not whole budget — financiers/")
    print("            bond companies expect to see it. Validate the base + rate (sec 3 #1, #4).")
    return 0


def cmd_overtime_burden(args: argparse.Namespace) -> int:
    if args.rate <= 0:
        print("error: --rate must be > 0", file=sys.stderr)
        return 2
    if not 0.0 <= args.fringe < 2.0:
        print("error: --fringe must be in [0%, 200%)", file=sys.stderr)
        return 2

    st = args.rate * (1 + args.fringe)
    ot15 = args.rate * 1.5 * (1 + args.fringe)
    ot2 = args.rate * 2.0 * (1 + args.fringe)

    print("Overtime burden — true marginal cost of one held hour")
    print(f"  base hourly rate               : {args.rate:>10,.2f}")
    print(f"  fringe/burden                  : {args.fringe * 100:g}%")
    print(f"  double-time threshold          : after {args.dt_after:g} worked hours")
    print("  ----------------------------------------")
    print(f"  straight-time hour (loaded)    : {st:>10,.2f}")
    print(f"  time-and-a-half hour (loaded)  : {ot15:>10,.2f}  ({ot15 / st:.2f}x the ST hour)")
    print(f"  double-time hour (loaded)      : {ot2:>10,.2f}  ({ot2 / st:.2f}x the ST hour)")
    print()
    print(
        f"  => one DT hour costs {ot2 - st:,.2f} more than one straight-time hour, per crew member."
    )
    print("  multiply by crew headcount before the AD calls 'one more hour'. And remember the")
    print("  hidden second cost: a short turnaround tomorrow can force a forced-call premium too.")
    print(
        "  reminder: multipliers + thresholds + meal penalties are agreement-specific (sec 3 #8)."
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="production_calc.py",
        description="Film/video production decision calculator (stdlib only). "
        "Decision-support, not union/legal/financial advice — validate every input.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sd = sub.add_parser("shoot-day-cost", help="Loaded shoot-day cost with overtime + fringe")
    sd.add_argument(
        "--crew-base",
        type=float,
        required=True,
        help="straight-time crew cost for the contracted day",
    )
    sd.add_argument(
        "--contracted-hours",
        type=float,
        required=True,
        help="contracted straight-time day length (hours)",
    )
    sd.add_argument(
        "--worked-hours",
        type=float,
        required=True,
        help="hours actually worked (or projected) on the day",
    )
    sd.add_argument(
        "--dt-after",
        type=float,
        default=12.0,
        help="worked hours after which double-time applies (default 12)",
    )
    sd.add_argument(
        "--fringe",
        type=_parse_rate,
        default=0.30,
        help="payroll fringe/burden as a fraction of labor (default 30%%)",
    )
    sd.add_argument(
        "--flat-costs",
        type=float,
        default=0.0,
        help="flat per-day non-labor costs (gear/location/catering)",
    )
    sd.set_defaults(func=cmd_shoot_day_cost)

    ct = sub.add_parser("contingency", help="Top-sheet contingency reserve + burn projection")
    ct.add_argument(
        "--base",
        type=float,
        required=True,
        help="contingency base (convention: below-the-line + post)",
    )
    ct.add_argument(
        "--pct",
        type=_parse_rate,
        default=0.10,
        help="contingency rate as a fraction (default 10%%)",
    )
    ct.add_argument(
        "--pre-contingency-total",
        type=float,
        default=None,
        help="grand total before contingency (default: use --base)",
    )
    ct.add_argument(
        "--drawn", type=float, default=None, help="contingency dollars drawn to date (optional)"
    )
    ct.add_argument(
        "--days-elapsed",
        type=float,
        default=None,
        help="shoot-days elapsed, for a burn projection (optional)",
    )
    ct.add_argument(
        "--days-total",
        type=float,
        default=None,
        help="total shoot-days, for a burn projection (optional)",
    )
    ct.set_defaults(func=cmd_contingency)

    ot = sub.add_parser("overtime-burden", help="Marginal loaded cost of an overtime hour")
    ot.add_argument("--rate", type=float, required=True, help="base hourly rate for the position")
    ot.add_argument(
        "--dt-after",
        type=float,
        default=12.0,
        help="worked hours after which double-time applies (default 12)",
    )
    ot.add_argument(
        "--fringe",
        type=_parse_rate,
        default=0.30,
        help="payroll fringe/burden as a fraction (default 30%%)",
    )
    ot.set_defaults(func=cmd_overtime_burden)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
