#!/usr/bin/env python3
"""dental_calc.py — a zero-dependency dental-practice decision calculator.

Removes arithmetic error from three recurring practice-economics decisions a
dental owner / office manager / consultant runs constantly:

  ppo-mix          The EFFECTIVE FEE and write-off impact of a PPO plan, plus
                   what a negotiation lift recovers. effective fee = full UCR
                   fee × (1 − write-off%); shows annual write-off dollars at a
                   given production volume and the dollars a negotiated rate
                   increase puts back. Pairs with the payer-mix decision tree
                   (knowledge/dental-ppo-vs-ffs-decision-tree.md).

  hygiene-capacity The recoverable SCHEDULE FILL hiding in retained patients and
                   under-yielded hours BEFORE expansion/marketing: reappointment
                   gap × visits, plus the overdue-recall pool, plus the per-hour
                   yield gap × booked hours. Pairs with
                   knowledge/dental-hygiene-capacity-decision-tree.md.

  collection-lift  The dollars recovered by moving the COLLECTION RATIO toward
                   target on a given production base — the "no extra chair time"
                   money (CLAUDE.md §3 #2). Pairs with the
                   protect-the-collection-ratio skill.

This is a CALCULATOR, not a data source — it does not fetch benchmarks, fees,
or live costs. The user supplies every input; the tool does the arithmetic and
shows the formula. Stdlib only (argparse); runs anywhere Python 3.8+ is present.

IMPORTANT: outputs are decision-support, not clinical, legal, or licensed
financial advice (see ../CLAUDE.md §2). Validate every figure against the
practice's actual ledger before any deliverable (CLAUDE.md §3 #8).

Examples
--------
  # PPO mix: $1,500 full UCR fee value worth of work, 40% write-off, $600k/yr
  # production through this plan, modeling a 12% negotiated rate increase
  python3 dental_calc.py ppo-mix --ucr 1500 --write-off 40% \\
      --annual-production 600000 --negotiated-lift 12%

  # Hygiene capacity: reappointment 52% vs 88% target across 4,000 hygiene
  # visits/yr, 350 overdue patients, hygiene running $135/hr vs $165 benchmark
  # over 3,000 booked hygiene hours/yr
  python3 dental_calc.py hygiene-capacity --reappt 52% --reappt-target 88% \\
      --hygiene-visits 4000 --avg-hygiene-production 180 --overdue 350 \\
      --actual-rate 135 --benchmark-rate 165 --booked-hours 3000

  # Collection lift: move 92% -> 98% on a $1.2M production base
  python3 dental_calc.py collection-lift --production 1200000 \\
      --current 92% --target 98%
"""

from __future__ import annotations

import argparse
import sys


def _parse_rate(s: str) -> float:
    """Parse a rate like '40%' or '0.40' into a fraction (0.40)."""
    s = s.strip()
    try:
        return float(s[:-1]) / 100.0 if s.endswith("%") else float(s)
    except ValueError:
        raise argparse.ArgumentTypeError(f"must be like '40%' or '0.40', got {s!r}")


def cmd_ppo_mix(args: argparse.Namespace) -> int:
    if not 0.0 <= args.write_off < 1.0:
        print("error: --write-off must be in [0%, 100%)", file=sys.stderr)
        return 2
    if not 0.0 <= args.negotiated_lift < 1.0:
        print("error: --negotiated-lift must be in [0%, 100%)", file=sys.stderr)
        return 2

    effective_fee = args.ucr * (1.0 - args.write_off)
    print("PPO plan — effective fee & write-off impact")
    print(f"  full UCR fee value        : {args.ucr:,.2f}")
    print(f"  write-off rate            : {args.write_off * 100:g}%")
    print(f"  → effective (collected) fee: {effective_fee:,.2f}")
    print(f"    (you bank {(1.0 - args.write_off) * 100:g} cents on every UCR dollar through this plan)")

    if args.annual_production:
        annual_writeoff = args.annual_production * args.write_off
        annual_collected = args.annual_production - annual_writeoff
        print()
        print(f"  at {args.annual_production:,.0f} UCR-value production/yr through this plan:")
        print(f"    annual write-off (lost) : {annual_writeoff:,.0f}")
        print(f"    annual collected        : {annual_collected:,.0f}")

    if args.negotiated_lift > 0:
        # A negotiated rate increase raises the contracted (effective) fee.
        new_effective = effective_fee * (1.0 + args.negotiated_lift)
        new_effective = min(new_effective, args.ucr)  # can't exceed full UCR
        per_unit_gain = new_effective - effective_fee
        new_writeoff_rate = 1.0 - (new_effective / args.ucr) if args.ucr else 0.0
        print()
        print(f"  modeling a {args.negotiated_lift * 100:g}% negotiated rate increase:")
        print(f"    new effective fee       : {new_effective:,.2f} "
              f"(write-off now {new_writeoff_rate * 100:.1f}%)")
        print(f"    per-unit fee recovered  : {per_unit_gain:,.2f}")
        if args.annual_production:
            # Volume of "units" implied by UCR-value production / UCR per unit.
            units = args.annual_production / args.ucr if args.ucr else 0.0
            annual_recovery = per_unit_gain * units
            print(f"    → annual dollars recovered: {annual_recovery:,.0f} "
                  "(no extra chair time)")
    print("  note: re-negotiate stale, high-volume contracts BEFORE dropping a plan;")
    print("        rank plans on effective fee × volume × strategic value (§3 #6).")
    return 0


def cmd_hygiene_capacity(args: argparse.Namespace) -> int:
    for name, val in (("--reappt", args.reappt), ("--reappt-target", args.reappt_target)):
        if not 0.0 <= val <= 1.0:
            print(f"error: {name} must be in [0%, 100%]", file=sys.stderr)
            return 2
    if args.reappt_target < args.reappt:
        print("note: target reappointment is below current — no reappointment gap to recover.",
              file=sys.stderr)

    print("Hygiene capacity — recoverable fill BEFORE expansion/marketing")

    reappt_gap = max(args.reappt_target - args.reappt, 0.0)
    reappt_recoverable_visits = reappt_gap * args.hygiene_visits
    reappt_dollars = reappt_recoverable_visits * args.avg_hygiene_production
    print(f"  reappointment gap         : {reappt_gap * 100:g}pp "
          f"({args.reappt * 100:g}% → {args.reappt_target * 100:g}%)")
    print(f"    recoverable visits/yr   : {reappt_recoverable_visits:,.0f}")
    print(f"    @ {args.avg_hygiene_production:,.0f}/visit → {reappt_dollars:,.0f}/yr")

    overdue_dollars = args.overdue * args.avg_hygiene_production
    print(f"  overdue-recall pool       : {args.overdue:,.0f} patients")
    print(f"    one-visit reactivation  : {overdue_dollars:,.0f} (one-time, recurring if retained)")

    yield_dollars = 0.0
    if args.benchmark_rate is not None and args.actual_rate is not None and args.booked_hours:
        yield_gap = max(args.benchmark_rate - args.actual_rate, 0.0)
        yield_dollars = yield_gap * args.booked_hours
        print(f"  per-hour yield gap        : {yield_gap:,.2f}/hr "
              f"({args.actual_rate:g} → {args.benchmark_rate:g}) over {args.booked_hours:,.0f} hrs")
        print(f"    recoverable yield/yr    : {yield_dollars:,.0f}")

    total = reappt_dollars + overdue_dollars + yield_dollars
    print()
    print(f"  → total recoverable fill  : ~{total:,.0f} "
          "(retained-patient + reactivation + yield)")
    print("  note: exhaust this BEFORE adding days/operatory or new-patient marketing —")
    print("        it's the cheapest capacity you already paid to acquire (§3 #4, #5).")
    return 0


def cmd_collection_lift(args: argparse.Namespace) -> int:
    for name, val in (("--current", args.current), ("--target", args.target)):
        if not 0.0 <= val <= 1.0:
            print(f"error: {name} must be in [0%, 100%]", file=sys.stderr)
            return 2
    if args.target < args.current:
        print("note: target collection ratio is below current — no lift to model.",
              file=sys.stderr)

    current_collected = args.production * args.current
    target_collected = args.production * args.target
    lift = max(target_collected - current_collected, 0.0)
    print("Collection-ratio lift — banked dollars on the same production")
    print(f"  production base           : {args.production:,.0f}")
    print(f"  current collection ratio  : {args.current * 100:g}% → collected {current_collected:,.0f}")
    print(f"  target collection ratio   : {args.target * 100:g}% → collected {target_collected:,.0f}")
    print(f"  → dollars recovered       : {lift:,.0f}  (no extra chair time)")
    print("  note: collections, not production, pay the bills (§3 #2). This is the cheapest")
    print("        revenue there is — banked dollars you already produced.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="dental_calc.py",
        description="Dental-practice decision calculator (stdlib only). "
        "Decision-support, not clinical/legal/financial advice — validate every input.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    ppo = sub.add_parser("ppo-mix", help="PPO effective fee, write-off impact, negotiation lift")
    ppo.add_argument("--ucr", type=float, required=True,
                     help="full UCR (office) fee value of the work")
    ppo.add_argument("--write-off", type=_parse_rate, required=True,
                     help="contractual write-off rate for this plan (e.g. 40%%)")
    ppo.add_argument("--annual-production", type=float, default=0.0,
                     help="annual UCR-value production through this plan (optional)")
    ppo.add_argument("--negotiated-lift", type=_parse_rate, default=0.0,
                     help="modeled negotiated rate increase on the contracted fee (e.g. 12%%)")
    ppo.set_defaults(func=cmd_ppo_mix)

    hyg = sub.add_parser("hygiene-capacity",
                         help="Recoverable hygiene schedule fill before expansion")
    hyg.add_argument("--reappt", type=_parse_rate, required=True,
                     help="current hygiene reappointment rate (e.g. 52%%)")
    hyg.add_argument("--reappt-target", type=_parse_rate, required=True,
                     help="target reappointment rate (e.g. 88%%)")
    hyg.add_argument("--hygiene-visits", type=float, required=True,
                     help="annual hygiene visits")
    hyg.add_argument("--avg-hygiene-production", type=float, required=True,
                     help="average production per hygiene visit")
    hyg.add_argument("--overdue", type=float, default=0.0,
                     help="count of overdue/unscheduled active patients")
    hyg.add_argument("--actual-rate", type=float, default=None,
                     help="actual hygiene production per hour (optional, for yield gap)")
    hyg.add_argument("--benchmark-rate", type=float, default=None,
                     help="benchmark hygiene production per hour (optional, for yield gap)")
    hyg.add_argument("--booked-hours", type=float, default=0.0,
                     help="annual booked hygiene hours (optional, for yield gap)")
    hyg.set_defaults(func=cmd_hygiene_capacity)

    col = sub.add_parser("collection-lift", help="Dollars recovered by raising the collection ratio")
    col.add_argument("--production", type=float, required=True, help="production base")
    col.add_argument("--current", type=_parse_rate, required=True,
                     help="current collection ratio (e.g. 92%%)")
    col.add_argument("--target", type=_parse_rate, required=True,
                     help="target collection ratio (e.g. 98%%)")
    col.set_defaults(func=cmd_collection_lift)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
