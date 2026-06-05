#!/usr/bin/env python3
"""cs_calc.py — a zero-dependency customer-success-analytics decision calculator.

Removes arithmetic error from three recurring CS-analytics decisions a
cs-analytics-architect / churn-signal-analyst / CS leader runs constantly:

  retention      NRR and GRR from a cohort's revenue movement (starting MRR/ARR
                 + expansion - contraction - churn). Prints both rates AND the
                 NRR-minus-GRR expansion gap, because **NRR alone hides logo /
                 dollar churn** — a 110% NRR can sit on top of a 6-figure churn
                 number masked by a few expanding whales. GRR caps at 100% and
                 is the honest retention floor. Pairs with the new
                 knowledge/cs-retention-metrics.md and the NRR-vs-GRR tree.

  health-score   The transparent WEIGHTED health score from a set of named
                 signals, each with a 0-1 normalized value, a weight, and a
                 leading/lagging flag. Prints the composite, the per-signal
                 contribution (the explainability contract — every Red shows
                 why), the share of score driven by LAGGING signals (a design
                 smell the plugin flags), and the tier from caller-supplied
                 Green/Yellow cut-points. Pairs with knowledge/
                 cs-health-metrics-and-churn-indicators.md and the health-tier-
                 design skill.

  renewal-risk   A renewal-risk score = proximity-gate x engagement-shortfall,
                 the plugin's central rule (risk = proximity X engagement, never
                 proximity alone). Prints the proximity gate, the engagement
                 shortfall, the product, and the call-priority bucket. Pairs
                 with knowledge/renewal-and-account-lifecycle.md and the
                 renewal-workflow-design skill.

This is a CALCULATOR, not a data source — it does not fetch benchmarks, pull a
CS platform, or read a warehouse. The user supplies every input; the tool does
the arithmetic and shows the formula. Stdlib only (argparse); runs anywhere
Python 3.8+ is present.

IMPORTANT: outputs are decision-support, not a substitute for back-testing a
signal against actual churn outcomes (see ../CLAUDE.md and the
back-test-signals-before-adding-to-tier-rule best practice). Validate every
input and every threshold against the team's real renewal-cycle data before any
deliverable. A weight or threshold the tool accepts is still a hypothesis until
it is back-tested.

Examples
--------
  # Retention: a cohort started the period at 1,000,000 ARR, expanded 180,000,
  # contracted 40,000, and churned 90,000.
  python3 cs_calc.py retention --starting 1000000 --expansion 180000 \\
      --contraction 40000 --churn 90000

  # Health score from four signals (name:value:weight[:lagging]); value is the
  # 0-1 normalized signal level (1 = healthiest). Mark lagging signals so the
  # tool can flag how much of the score they drive.
  python3 cs_calc.py health-score \\
      --signal usage_trend:0.3:0.35 \\
      --signal health_trend:0.4:0.25 \\
      --signal support_p1p2:0.5:0.20 \\
      --signal closed_lost:0.0:0.20:lagging \\
      --green 0.7 --yellow 0.4

  # Renewal risk: 45 days to renewal (cap 120), engagement 0.35 on a 0-1 scale
  # (1 = fully engaged), so the shortfall is 0.65.
  python3 cs_calc.py renewal-risk --days-to-renewal 45 --renewal-horizon 120 \\
      --engagement 0.35
"""

from __future__ import annotations

import argparse
import sys


def _pct(x: float) -> str:
    return f"{x * 100:.1f}%"


def _parse_rate(s: str) -> float:
    """Parse a rate like '35%' or '0.35' into a fraction (0.35)."""
    s = s.strip()
    try:
        return float(s[:-1]) / 100.0 if s.endswith("%") else float(s)
    except ValueError:
        raise argparse.ArgumentTypeError(f"must be like '35%' or '0.35', got {s!r}")


def cmd_retention(args: argparse.Namespace) -> int:
    if args.starting <= 0:
        print("error: --starting must be > 0", file=sys.stderr)
        return 2
    for name, val in (
        ("--expansion", args.expansion),
        ("--contraction", args.contraction),
        ("--churn", args.churn),
    ):
        if val < 0:
            print(f"error: {name} must be >= 0", file=sys.stderr)
            return 2

    start = args.starting
    # GRR excludes expansion and is capped at 100% by construction (you cannot
    # retain more than you started with from the existing base alone).
    grr = (start - args.contraction - args.churn) / start
    grr = min(grr, 1.0)
    # NRR includes expansion and can exceed 100%.
    nrr = (start + args.expansion - args.contraction - args.churn) / start
    gap = nrr - grr

    print("Retention — NRR and GRR")
    print(f"  starting revenue (period base) : {start:,.0f}")
    print(f"  + expansion                    : {args.expansion:,.0f}")
    print(f"  - contraction (downgrades)     : {args.contraction:,.0f}")
    print(f"  - churn (lost logos/dollars)   : {args.churn:,.0f}")
    print()
    print(f"  → GRR (excludes expansion, capped at 100%) : {_pct(grr)}")
    print(f"  → NRR (includes expansion)                 : {_pct(nrr)}")
    print(f"  → NRR - GRR expansion gap                  : {_pct(gap)}")
    print()
    if nrr >= 1.0 and grr < 0.9:
        print("  ⚠ NRR is >= 100% but GRR is below 90% — expansion is MASKING")
        print("    real churn/contraction. NRR alone hides logo loss; GRR is the")
        print("    honest retention floor. Surface BOTH, never NRR on its own.")
    elif gap >= 0.10:
        print("  note: a wide NRR-GRR gap means expansion is carrying retention.")
        print("        Healthy if broad-based; a risk if a few whales drive it —")
        print("        check expansion concentration before celebrating NRR.")
    else:
        print("  note: NRR and GRR are close — retention is not expansion-propped.")
    print("  reminder: GRR caps at 100% and exposes the true churn the headline")
    print("            NRR can hide. Validate the movement amounts against the")
    print("            mart, not the CS-platform dashboard (single source rule).")
    return 0


def _parse_signal(s: str) -> tuple:
    """Parse 'name:value:weight[:lagging]' into (name, value, weight, lagging)."""
    parts = s.split(":")
    if len(parts) < 3:
        raise argparse.ArgumentTypeError(
            f"signal must be name:value:weight[:lagging], got {s!r}"
        )
    name = parts[0]
    try:
        value = float(parts[1])
        weight = float(parts[2])
    except ValueError:
        raise argparse.ArgumentTypeError(f"value and weight must be numbers in {s!r}")
    lagging = len(parts) >= 4 and parts[3].strip().lower() in ("lagging", "lag", "true")
    if not 0.0 <= value <= 1.0:
        raise argparse.ArgumentTypeError(
            f"signal value must be a 0-1 normalized level, got {value} in {s!r}"
        )
    if weight < 0:
        raise argparse.ArgumentTypeError(f"weight must be >= 0 in {s!r}")
    return (name, value, weight, lagging)


def cmd_health_score(args: argparse.Namespace) -> int:
    signals = args.signal
    n = len(signals)
    if n < 1:
        print("error: at least one --signal is required", file=sys.stderr)
        return 2
    total_weight = sum(w for _, _, w, _ in signals)
    if total_weight <= 0:
        print("error: signal weights sum to 0", file=sys.stderr)
        return 2
    if not 0.0 <= args.yellow <= args.green <= 1.0:
        print("error: require 0 <= --yellow <= --green <= 1", file=sys.stderr)
        return 2

    print("Health score — transparent weighted composite")
    if n < 5 or n > 7:
        print(f"  ⚠ {n} signals — the plugin's phase-one discipline is 5-7 signals")
        print("    (fewer is fragile, more is unexplainable). Revisit the set.")
    print("  signal           |  value | weight | contribution | kind")
    print("  -----------------+--------+--------+--------------+--------")

    score = 0.0
    lagging_contribution = 0.0
    for name, value, weight, lagging in signals:
        norm_w = weight / total_weight
        contribution = value * norm_w
        score += contribution
        if lagging:
            lagging_contribution += contribution
        kind = "LAGGING" if lagging else "leading"
        print(
            f"  {name[:16]:<16} | {value:>6.2f} | {norm_w:>6.2f} "
            f"| {contribution:>12.3f} | {kind}"
        )

    if score >= args.green:
        tier = "GREEN"
    elif score >= args.yellow:
        tier = "YELLOW"
    else:
        tier = "RED"

    print()
    print(f"  → composite health score : {score:.3f}  (0 = worst, 1 = best)")
    print(f"  → tier                   : {tier}  "
          f"(green >= {args.green:g}, yellow >= {args.yellow:g})")
    lag_share = lagging_contribution / score if score > 0 else 0.0
    if lagging_contribution > 0:
        print(f"  → lagging-signal share   : {_pct(lag_share)} of the score")
        print("    ⚠ lagging signals (closed-lost, cancellation) CONFIRM churn,")
        print("      they do not predict it. A score driven by lagging signals")
        print("      reacts after the window has closed — move them to context.")
    print("  reminder: every Red must show its 2-3 driving signals with value /")
    print("            threshold / window. This table IS that explainability")
    print("            contract. A weight is a hypothesis until back-tested.")
    return 0


def cmd_renewal_risk(args: argparse.Namespace) -> int:
    if args.renewal_horizon <= 0:
        print("error: --renewal-horizon must be > 0", file=sys.stderr)
        return 2
    if args.days_to_renewal < 0:
        print("error: --days-to-renewal must be >= 0", file=sys.stderr)
        return 2
    if not 0.0 <= args.engagement <= 1.0:
        print("error: --engagement must be a 0-1 level", file=sys.stderr)
        return 2

    # Proximity gate: 1.0 at renewal day, decaying to 0 at/after the horizon.
    # This is the "context, not risk" multiplier — it scales urgency, it is
    # never risk on its own.
    proximity = max(0.0, 1.0 - args.days_to_renewal / args.renewal_horizon)
    # Engagement shortfall: 1.0 = fully disengaged, 0.0 = fully engaged.
    shortfall = 1.0 - args.engagement
    # Risk is the PRODUCT — proximity alone or shortfall alone is not risk.
    risk = proximity * shortfall

    print("Renewal risk — proximity x engagement (never proximity alone)")
    print(f"  days to renewal     : {args.days_to_renewal:g} "
          f"(horizon {args.renewal_horizon:g})")
    print(f"  engagement level    : {args.engagement:.2f} (1 = fully engaged)")
    print(f"  → proximity gate    : {proximity:.3f} (urgency multiplier, not risk)")
    print(f"  → engagement shortfall : {shortfall:.3f}")
    print(f"  → RISK = proximity x shortfall : {risk:.3f}")
    print()

    if risk >= 0.5:
        bucket = "CALL NOW — near renewal AND disengaged (top of the call list)"
    elif risk >= 0.25:
        bucket = "THIS WEEK — meaningful proximity x shortfall"
    elif proximity >= 0.5 and shortfall < 0.3:
        bucket = "CONFIRM-AND-EXPAND — near renewal but engaged (not a risk)"
    elif shortfall >= 0.5 and proximity < 0.25:
        bucket = "RECOVERY PROJECT — disengaged but distant renewal (runway to fix)"
    else:
        bucket = "MONITOR — neither gate is tripped hard"
    print(f"  → call priority     : {bucket}")
    print("  reminder: proximity is the GATE, not the risk. A near renewal on an")
    print("            engaged account is a confirm-and-expand, not an emergency.")
    print("            Confirm the decision-maker is alive in role before any call.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cs_calc.py",
        description="Customer-success-analytics decision calculator (stdlib only). "
        "Decision-support, not a back-test — validate every weight/threshold "
        "against real churn outcomes.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    ret = sub.add_parser("retention", help="NRR + GRR + the expansion-gap masking check")
    ret.add_argument("--starting", type=float, required=True,
                     help="starting revenue for the period (MRR or ARR base)")
    ret.add_argument("--expansion", type=float, default=0.0,
                     help="expansion revenue from the existing base (upsell/cross-sell)")
    ret.add_argument("--contraction", type=float, default=0.0,
                     help="contraction revenue (downgrades, seat reductions)")
    ret.add_argument("--churn", type=float, default=0.0,
                     help="churned revenue (lost logos / cancellations)")
    ret.set_defaults(func=cmd_retention)

    hs = sub.add_parser("health-score",
                        help="transparent weighted health score + tier + lagging-share flag")
    hs.add_argument("--signal", type=_parse_signal, action="append", default=[],
                    metavar="NAME:VALUE:WEIGHT[:lagging]",
                    help="a signal: 0-1 value, a weight, optional 'lagging' flag "
                    "(repeatable; weights are normalized to sum to 1)")
    hs.add_argument("--green", type=_parse_rate, default=0.7,
                    help="composite >= this is GREEN (default 0.7)")
    hs.add_argument("--yellow", type=_parse_rate, default=0.4,
                    help="composite >= this is YELLOW, else RED (default 0.4)")
    hs.set_defaults(func=cmd_health_score)

    rr = sub.add_parser("renewal-risk",
                        help="renewal risk = proximity gate x engagement shortfall")
    rr.add_argument("--days-to-renewal", type=float, required=True,
                    help="days until the renewal date")
    rr.add_argument("--renewal-horizon", type=float, default=120.0,
                    help="proximity horizon in days; risk gate is 0 beyond it (default 120)")
    rr.add_argument("--engagement", type=_parse_rate, required=True,
                    help="0-1 engagement level (1 = fully engaged); shortfall = 1 - this")
    rr.set_defaults(func=cmd_renewal_risk)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
