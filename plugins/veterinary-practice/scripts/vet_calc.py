#!/usr/bin/env python3
"""vet_calc.py — a zero-dependency veterinary-practice decision calculator.

Removes arithmetic error from three recurring practice-economics decisions a
veterinary owner / medical director / consultant runs constantly:

  associate-roi   The ramp J-CURVE for hiring an associate DVM. Models monthly
                  net contribution = ramped incremental production − associate
                  compensation − the support/COGS load that scales with added
                  production. Prints the monthly trough, its depth, and the
                  cumulative-breakeven month. Pairs with the capacity decision
                  tree (knowledge/vet-add-associate-vs-extend-capacity-decision-tree.md).

  lab-breakeven   The monthly-VOLUME breakeven where an IN-HOUSE analyzer beats
                  SEND-OUT for a test panel: per-test cost = analyzer
                  amortization/volume + consumables/test + tech-time/test, vs a
                  flat send-out per-test cost. Prints the breakeven volume and
                  the verdict at your projected volume. Pairs with
                  knowledge/vet-in-house-vs-send-out-lab-decision-tree.md.

  wellness-margin The monthly MARGIN of a wellness/preventive-care plan tier:
                  monthly fee − (Σ bundled services at cost × expected
                  redemption rate). Flags the redemption rate at which the tier
                  goes underwater. Pairs with knowledge/vet-practice-economics.md
                  and the lift-care-compliance skill.

This is a CALCULATOR, not a data source — it does not fetch benchmarks, fees,
or live costs. The user supplies every input; the tool does the arithmetic and
shows the formula. Stdlib only (argparse); runs anywhere Python 3.8+ is present.

IMPORTANT: outputs are decision-support, not clinical, legal, or licensed
financial advice (see ../CLAUDE.md §2). Validate every figure against the
practice's actual data before any deliverable (CLAUDE.md §3 #8).

Examples
--------
  # Associate ROI: 12-month linear ramp to $40k/mo production, $9k/mo comp,
  # 35% of incremental production eaten by scaling support + COGS
  python3 vet_calc.py associate-roi --ramp-months 12 --target-production 40000 \\
      --monthly-comp 9000 --variable-load 35%

  # In-house lab breakeven: $24k analyzer over 5 years, $6 consumables/test,
  # $4 tech time/test, vs $18 send-out/test; projecting 250 tests/month
  python3 vet_calc.py lab-breakeven --analyzer-cost 24000 --amortize-years 5 \\
      --consumables 6 --tech-time 4 --sendout 18 --volume 250

  # Wellness-plan tier margin: $55/mo fee, services that cost the practice
  # $40/mo at full use, expected 70% redemption
  python3 vet_calc.py wellness-margin --fee 55 --service-cost 40 --redemption 70%
"""

from __future__ import annotations

import argparse
import sys


def _parse_rate(s: str) -> float:
    """Parse a rate like '35%' or '0.35' into a fraction (0.35)."""
    s = s.strip()
    try:
        return float(s[:-1]) / 100.0 if s.endswith("%") else float(s)
    except ValueError:
        raise argparse.ArgumentTypeError(f"must be like '35%' or '0.35', got {s!r}")


def cmd_associate_roi(args: argparse.Namespace) -> int:
    if args.ramp_months < 1:
        print("error: --ramp-months must be >= 1", file=sys.stderr)
        return 2
    if not 0.0 <= args.variable_load < 1.0:
        print("error: --variable-load must be in [0%, 100%)", file=sys.stderr)
        return 2

    horizon = max(args.horizon_months, args.ramp_months)
    print("Associate DVM ROI — ramp J-curve")
    print(f"  ramp to full production : {args.ramp_months} months (linear)")
    print(f"  target production/mo    : {args.target_production:,.0f}")
    print(f"  associate comp/mo       : {args.monthly_comp:,.0f}")
    print(f"  variable load on prod   : {args.variable_load * 100:g}% (scaling support + COGS)")
    print(f"  horizon                 : {horizon} months")
    print("  month | production | net contribution | cumulative")
    print("  ------+------------+------------------+-----------")

    cumulative = 0.0
    trough = None  # (month, cumulative)
    breakeven_month = None
    for m in range(1, horizon + 1):
        frac = min(m / args.ramp_months, 1.0)
        production = args.target_production * frac
        net = production * (1.0 - args.variable_load) - args.monthly_comp
        cumulative += net
        if trough is None or cumulative < trough[1]:
            trough = (m, cumulative)
        if breakeven_month is None and cumulative >= 0:
            breakeven_month = m
        print(f"  {m:>5} | {production:>10,.0f} | {net:>16,.0f} | {cumulative:>10,.0f}")

    print()
    print(f"  → deepest cumulative trough : {trough[1]:,.0f} at month {trough[0]}")
    if breakeven_month:
        print(f"  → cumulative breakeven      : month {breakeven_month}")
    else:
        print(f"  → cumulative breakeven      : NOT reached within {horizon} months")
    print("  note: the trough is the cash the practice must fund. Demand-check FIRST")
    print("        (production thresholds + new-client flow) before trusting this model.")
    return 0


def cmd_lab_breakeven(args: argparse.Namespace) -> int:
    if args.amortize_years <= 0:
        print("error: --amortize-years must be > 0", file=sys.stderr)
        return 2
    months = args.amortize_years * 12
    monthly_amort = args.analyzer_cost / months
    marginal = args.consumables + args.tech_time  # per-test variable cost in-house

    print("In-house lab vs send-out — volume breakeven")
    print(f"  analyzer capital     : {args.analyzer_cost:,.0f} over {args.amortize_years:g}y "
          f"= {monthly_amort:,.0f}/mo")
    print(f"  in-house per-test var: {marginal:,.2f} (consumables {args.consumables:g} + tech {args.tech_time:g})")
    print(f"  send-out per-test    : {args.sendout:,.2f}")

    per_test_gap = args.sendout - marginal
    if per_test_gap <= 0:
        print()
        print("  → send-out is cheaper PER TEST even before capital — in-house never breaks even")
        print("    on cost alone. Justify in-house only on CLINICAL turnaround value, not cost.")
        return 0

    breakeven_volume = monthly_amort / per_test_gap
    print(f"  per-test variable saving (send-out − in-house): {per_test_gap:,.2f}")
    print(f"  → BREAKEVEN volume   : {breakeven_volume:,.1f} tests/month")
    print("    (above this monthly volume, in-house beats send-out on cost)")

    if args.volume is not None:
        in_house_total = monthly_amort + marginal * args.volume
        sendout_total = args.sendout * args.volume
        verdict = "IN-HOUSE" if in_house_total < sendout_total else "SEND-OUT"
        print()
        print(f"  at your projected {args.volume:g} tests/month:")
        print(f"    in-house monthly cost : {in_house_total:,.0f}")
        print(f"    send-out monthly cost : {sendout_total:,.0f}")
        print(f"    → cheaper on cost     : {verdict}")
        print("    reminder: turnaround/clinical value can justify in-house BELOW breakeven.")
    return 0


def cmd_wellness_margin(args: argparse.Namespace) -> int:
    if not 0.0 <= args.redemption <= 1.0:
        print("error: --redemption must be in [0%, 100%]", file=sys.stderr)
        return 2
    expected_cost = args.service_cost * args.redemption
    margin = args.fee - expected_cost
    margin_pct = (margin / args.fee * 100.0) if args.fee else 0.0

    print("Wellness-plan tier — monthly margin")
    print(f"  monthly fee              : {args.fee:,.2f}")
    print(f"  bundled service cost     : {args.service_cost:,.2f} (at full use, practice COST not retail)")
    print(f"  expected redemption rate : {args.redemption * 100:g}%")
    print(f"  expected service cost/mo : {expected_cost:,.2f}")
    print(f"  → MARGIN/mo              : {margin:,.2f}  ({margin_pct:.1f}% of fee)")

    if args.service_cost > 0:
        underwater_redemption = args.fee / args.service_cost
        if underwater_redemption <= 1.0:
            print(f"  → underwater at redemption >= {underwater_redemption * 100:.0f}% "
                  "(fee no longer covers service cost)")
        else:
            print("  → fee covers full-use cost even at 100% redemption (conservative tier)")
    print("  note: model redemption from REAL past-patient data, not a guess — assume")
    print("        too high and margin collapses; too low and pricing won't hold (§3 #6).")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="vet_calc.py",
        description="Veterinary-practice decision calculator (stdlib only). "
        "Decision-support, not clinical/legal/financial advice — validate every input.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    roi = sub.add_parser("associate-roi", help="Associate DVM hiring ROI J-curve")
    roi.add_argument("--ramp-months", type=int, required=True,
                     help="months to reach full production (linear ramp)")
    roi.add_argument("--target-production", type=float, required=True,
                     help="full monthly production once ramped")
    roi.add_argument("--monthly-comp", type=float, required=True,
                     help="associate total monthly compensation (salary or production floor)")
    roi.add_argument("--variable-load", type=_parse_rate, default=0.30,
                     help="fraction of incremental production consumed by scaling "
                     "support + COGS (default 30%%)")
    roi.add_argument("--horizon-months", type=int, default=24,
                     help="months to project (default 24; min = ramp-months)")
    roi.set_defaults(func=cmd_associate_roi)

    lab = sub.add_parser("lab-breakeven", help="In-house lab vs send-out volume breakeven")
    lab.add_argument("--analyzer-cost", type=float, required=True, help="analyzer capital cost")
    lab.add_argument("--amortize-years", type=float, default=5.0,
                     help="amortization period in years (default 5)")
    lab.add_argument("--consumables", type=float, required=True, help="consumables cost per test")
    lab.add_argument("--tech-time", type=float, default=0.0, help="tech-time cost per test")
    lab.add_argument("--sendout", type=float, required=True, help="send-out cost per test")
    lab.add_argument("--volume", type=float, default=None,
                     help="projected tests/month for a verdict (optional)")
    lab.set_defaults(func=cmd_lab_breakeven)

    well = sub.add_parser("wellness-margin", help="Wellness-plan tier monthly margin")
    well.add_argument("--fee", type=float, required=True, help="monthly plan fee")
    well.add_argument("--service-cost", type=float, required=True,
                      help="bundled-service cost to the practice at full use (cost, not retail)")
    well.add_argument("--redemption", type=_parse_rate, required=True,
                      help="expected redemption/utilization rate (e.g. 70%%)")
    well.set_defaults(func=cmd_wellness_margin)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
