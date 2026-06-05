#!/usr/bin/env python3
"""pm_calc.py - a zero-dependency product-management prioritization calculator.

Removes arithmetic error from three recurring product-management decisions a
PM / product lead / head of product runs constantly:

  rice          The RICE score for one or many backlog items:
                  (Reach x Impact x Confidence) / Effort.
                Impact takes Intercom's published 3/2/1/0.5/0.25 scale
                (massive/high/medium/low/minimal) or a raw multiplier;
                Confidence is a percent (100/80/50% per the scale) or a
                fraction. Prints the score and, with several items, a ranked
                table so the meeting argues the INPUTS, not the math.
                Pairs with knowledge/prioritization-method-selection-decision-tree.md.

  wsjf          The SAFe Weighted Shortest Job First score:
                  Cost of Delay / Job Size, where
                  CoD = Business Value + Time Criticality + Risk Reduction /
                  Opportunity Enablement (the three published CoD inputs).
                Inputs are relative (modified-Fibonacci 1-2-3-5-8-13-20 is the
                SAFe convention). Use when time-sensitivity dominates and RICE
                buries the deadline-driven items.
                Pairs with the same decision tree.

  opportunity   A bottoms-up opportunity SIZE for a single opportunity:
                  reachable users x adoption rate x value per adopting user
                  x confidence. Prints the point estimate plus a low/expected/
                  high band from an optional confidence haircut, so the number
                  is argued as a RANGE, never a single false-precision figure.
                This is a sizing HELPER, not a market study.

This is a CALCULATOR, not a data source - it does not fetch benchmarks,
reach data, or live metrics. The user supplies every input; the tool does the
arithmetic and shows the formula. Stdlib only (argparse); runs anywhere
Python 3.8+ is present.

IMPORTANT: outputs are decision-support, not a substitute for evidence. A RICE
or WSJF score is only as good as the inputs - its value is making reach /
impact / confidence / effort (or cost-of-delay) EXPLICIT AND ARGUABLE, not the
decimal (see ../CLAUDE.md SS2 #3). Calibrate every input to the team's own data
and mark unverified figures (CLAUDE.md SS2; the cross-plugin claim-grounding rule).

Examples
--------
  # One RICE item: reach 8000 users/quarter, "high" impact, 80% confidence,
  # 5 person-weeks of effort
  python3 pm_calc.py rice --reach 8000 --impact high --confidence 80% --effort 5

  # Compare several RICE items from a CSV-ish inline spec (name:reach:impact:confidence:effort)
  python3 pm_calc.py rice \\
      --item "SSO:8000:high:80%:5" \\
      --item "Bulk export:3000:medium:100%:2" \\
      --item "Dark mode:12000:low:50%:3"

  # WSJF: business value 8, time-criticality 13, risk/opp-enablement 5, job size 5
  python3 pm_calc.py wsjf --business-value 8 --time-criticality 13 \\
      --risk-opportunity 5 --job-size 5

  # Opportunity size: 50k reachable users, 20% expected adoption,
  # $120/yr value per adopter, 60% confidence -> point + band
  python3 pm_calc.py opportunity --reachable 50000 --adoption 20% \\
      --value-per-user 120 --confidence 60%
"""

from __future__ import annotations

import argparse
import sys

# Intercom's published RICE impact scale (massive/high/medium/low/minimal).
# Source: https://www.intercom.com/blog/rice-simple-prioritization-for-product-managers/
_IMPACT_SCALE = {
    "massive": 3.0,
    "high": 2.0,
    "medium": 1.0,
    "low": 0.5,
    "minimal": 0.25,
}


def _parse_rate(s: str) -> float:
    """Parse a rate like '80%' or '0.8' into a fraction (0.8)."""
    s = s.strip()
    try:
        return float(s[:-1]) / 100.0 if s.endswith("%") else float(s)
    except ValueError:
        raise argparse.ArgumentTypeError(f"must be like '80%' or '0.8', got {s!r}")


def _parse_impact(s: str) -> float:
    """Parse an impact: a named tier (Intercom scale) or a raw multiplier."""
    s = s.strip().lower()
    if s in _IMPACT_SCALE:
        return _IMPACT_SCALE[s]
    try:
        return float(s)
    except ValueError:
        names = "/".join(_IMPACT_SCALE)
        raise argparse.ArgumentTypeError(
            f"impact must be one of {names} or a number, got {s!r}"
        )


def _rice_score(reach: float, impact: float, confidence: float, effort: float) -> float:
    if effort <= 0:
        raise ValueError("effort must be > 0")
    return (reach * impact * confidence) / effort


def cmd_rice(args: argparse.Namespace) -> int:
    rows = []  # (name, reach, impact, confidence, effort, score)

    if args.item:
        for spec in args.item:
            parts = spec.split(":")
            if len(parts) != 5:
                print(
                    f"error: --item must be name:reach:impact:confidence:effort, got {spec!r}",
                    file=sys.stderr,
                )
                return 2
            name, reach_s, impact_s, conf_s, effort_s = parts
            try:
                reach = float(reach_s)
                impact = _parse_impact(impact_s)
                confidence = _parse_rate(conf_s)
                effort = float(effort_s)
                score = _rice_score(reach, impact, confidence, effort)
            except (ValueError, argparse.ArgumentTypeError) as e:
                print(f"error in --item {spec!r}: {e}", file=sys.stderr)
                return 2
            rows.append((name.strip(), reach, impact, confidence, effort, score))
    else:
        if args.reach is None or args.impact is None or args.effort is None:
            print(
                "error: provide either --item specs OR --reach/--impact/--effort "
                "(and optionally --confidence)",
                file=sys.stderr,
            )
            return 2
        try:
            score = _rice_score(args.reach, args.impact, args.confidence, args.effort)
        except ValueError as e:
            print(f"error: {e}", file=sys.stderr)
            return 2
        rows.append(("(item)", args.reach, args.impact, args.confidence, args.effort, score))

    print("RICE score = (Reach x Impact x Confidence) / Effort")
    print("  (Intercom impact scale: massive 3 / high 2 / medium 1 / low 0.5 / minimal 0.25)")
    print()
    rows_sorted = sorted(rows, key=lambda r: r[5], reverse=True)
    print("  rank | item                 |    reach | impact | conf | effort |    RICE")
    print("  -----+----------------------+----------+--------+------+--------+--------")
    for i, (name, reach, impact, conf, effort, score) in enumerate(rows_sorted, 1):
        print(
            f"  {i:>4} | {name[:20]:<20} | {reach:>8,.0f} | {impact:>6.2f} | "
            f"{conf * 100:>3.0f}% | {effort:>6.1f} | {score:>7,.1f}"
        )
    print()
    print("  note: the score's value is making the inputs explicit and arguable - calibrate")
    print("        reach to instrumented data, not a guess; a >2x disagreement on any one")
    print("        factor is a 'go get information' signal, not a negotiation (CLAUDE.md SS2 #3).")
    return 0


def cmd_wsjf(args: argparse.Namespace) -> int:
    if args.job_size <= 0:
        print("error: --job-size must be > 0", file=sys.stderr)
        return 2
    cod = args.business_value + args.time_criticality + args.risk_opportunity
    score = cod / args.job_size

    print("WSJF = Cost of Delay / Job Size")
    print("  Cost of Delay = Business Value + Time Criticality + Risk Reduction/Opportunity Enablement")
    print("  (SAFe convention: score each on the modified-Fibonacci scale 1-2-3-5-8-13-20)")
    print()
    print(f"  business value                  : {args.business_value:g}")
    print(f"  time criticality                : {args.time_criticality:g}")
    print(f"  risk reduction / opp enablement : {args.risk_opportunity:g}")
    print(f"  --> cost of delay               : {cod:g}")
    print(f"  job size                        : {args.job_size:g}")
    print(f"  --> WSJF score                  : {score:,.2f}")
    print()
    print("  note: WSJF inputs are RELATIVE, not absolute - rank items against each other in")
    print("        one sitting. Use WSJF when time-sensitivity dominates (a deadline, a closing")
    print("        window); it stops urgent items being buried the way RICE can (CLAUDE.md SS2 #3).")
    return 0


def cmd_opportunity(args: argparse.Namespace) -> int:
    point = (
        args.reachable * args.adoption * args.value_per_user * args.confidence
    )
    # Symmetric band from the confidence haircut: confidence c -> [c*point ... point/c-ish].
    # Use a simple, transparent +/- band driven by (1 - confidence) so the range is honest
    # about uncertainty without pretending to a statistical interval.
    spread = (1.0 - args.confidence)
    low = point * (1.0 - spread)
    high = point * (1.0 + spread)

    print("Opportunity size = reachable users x adoption x value/user x confidence")
    print()
    print(f"  reachable users         : {args.reachable:,.0f}")
    print(f"  expected adoption rate  : {args.adoption * 100:g}%")
    print(f"  value per adopting user : {args.value_per_user:,.2f}")
    print(f"  confidence              : {args.confidence * 100:g}%")
    print(f"  --> expected size       : {point:,.0f}")
    print(f"  --> honest band         : {low:,.0f}  ..  {high:,.0f}")
    print(f"      (band = +/- (1 - confidence) = +/-{spread * 100:g}% - NOT a statistical interval)")
    print()
    print("  note: this is a bottoms-up SIZING HELPER, not a market study. Argue the number as")
    print("        a RANGE; each input is a [verify-at-use] assumption - source reachable users")
    print("        and value/user from data, not a top-down TAM% (CLAUDE.md SS2 #3, claim-grounding).")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="pm_calc.py",
        description="Product-management prioritization calculator (stdlib only). "
        "Decision-support, not a substitute for evidence - calibrate every input.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    rice = sub.add_parser("rice", help="RICE score (Reach x Impact x Confidence / Effort)")
    rice.add_argument("--reach", type=float, default=None,
                      help="users/events affected per time period (single-item mode)")
    rice.add_argument("--impact", type=_parse_impact, default=None,
                      help="massive/high/medium/low/minimal (3/2/1/0.5/0.25) or a raw multiplier")
    rice.add_argument("--confidence", type=_parse_rate, default=0.8,
                      help="confidence as a percent or fraction (default 80%%)")
    rice.add_argument("--effort", type=float, default=None,
                      help="effort in person-time units (person-weeks/months); must be > 0")
    rice.add_argument("--item", action="append", default=None,
                      help="repeatable: name:reach:impact:confidence:effort (ranked table mode)")
    rice.set_defaults(func=cmd_rice)

    wsjf = sub.add_parser("wsjf", help="WSJF score (Cost of Delay / Job Size, SAFe)")
    wsjf.add_argument("--business-value", type=float, required=True,
                      help="relative business value (Fibonacci 1-20)")
    wsjf.add_argument("--time-criticality", type=float, required=True,
                      help="relative time criticality / value decay (Fibonacci 1-20)")
    wsjf.add_argument("--risk-opportunity", type=float, required=True,
                      help="relative risk reduction / opportunity enablement (Fibonacci 1-20)")
    wsjf.add_argument("--job-size", type=float, required=True,
                      help="relative job size / effort (Fibonacci 1-20); must be > 0")
    wsjf.set_defaults(func=cmd_wsjf)

    opp = sub.add_parser("opportunity", help="Bottoms-up opportunity size + honest band")
    opp.add_argument("--reachable", type=float, required=True,
                     help="reachable users in the target segment")
    opp.add_argument("--adoption", type=_parse_rate, required=True,
                     help="expected adoption rate (percent or fraction)")
    opp.add_argument("--value-per-user", type=float, required=True,
                     help="annual value per adopting user (revenue/retention proxy)")
    opp.add_argument("--confidence", type=_parse_rate, default=0.6,
                     help="confidence in the estimate (percent or fraction; default 60%%)")
    opp.set_defaults(func=cmd_opportunity)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
