#!/usr/bin/env python3
"""compliance_calc.py — a zero-dependency compliance risk-scoring calculator.

Removes arithmetic error from three recurring risk/compliance computations a
second-line risk-and-controls or AML analyst runs constantly. It is a
CALCULATOR, not a data source and not a rulebook — it does not fetch ratings,
thresholds, or regulator figures, and it bakes in NO legal advice and NO
regulatory threshold. The user supplies every input (their own firm's scale,
their own weights, their own appetite); the tool does the arithmetic and shows
the formula so the result is auditable.

  risk-score    Inherent and RESIDUAL risk on a likelihood x impact rubric, with
                a control-effectiveness reduction. Prints inherent score,
                residual score, and how residual compares to a risk-appetite
                threshold you supply (within / outside appetite). Pairs with
                knowledge/risk-rating-and-escalation-decision-tree.md and the
                risk-register-build skill.

  customer-risk A WEIGHTED customer/entity risk score from factor scores you
                provide (e.g. geography, product, channel, ownership) each with
                a weight. Prints the weighted score and the band it falls in
                against bands you define. This computes YOUR model; it does not
                decide CDD vs EDD (that is the decision tree + the regime's
                rules). Pairs with knowledge/compliance-decision-trees.md.

  sample-size   A simple attribute-sampling helper for control testing: given a
                population size and a desired sample, prints the coverage, and
                given a control frequency, prints a reference sample count from
                a frequency->count table YOU pass in (no standard is hardcoded).
                Pairs with skills/control-testing and the design-vs-operating
                scenario. Sample sizes are auditor/standard-specific
                [verify-at-use] — this only does the arithmetic you direct.

This is decision-support, NOT legal, regulatory, or audit advice (see
../CLAUDE.md sections 3 #10 and 6). Every scale, weight, threshold, and band is
the FIRM's own and is [verify-at-use] against the firm's documented methodology,
its board-approved risk-appetite statement, and the applicable regulator's
primary source before any deliverable. Stdlib only; runs anywhere Python 3.8+.

Examples
--------
  # Inherent likelihood 4 x impact 5 = 20; controls cut residual by 60%;
  # appetite threshold for this category is 10
  python3 compliance_calc.py risk-score --likelihood 4 --impact 5 \\
      --control-effectiveness 60% --appetite-threshold 10

  # Weighted customer risk: geography 4 (w 0.4), product 2 (w 0.3),
  # channel 3 (w 0.2), ownership 5 (w 0.1); bands low<2, standard<3.5, else high
  python3 compliance_calc.py customer-risk \\
      --factor geography=4:0.4 --factor product=2:0.3 \\
      --factor channel=3:0.2 --factor ownership=5:0.1 \\
      --band low=2 --band standard=3.5

  # Sampling: population 1200, sample 30; reference table for a daily control
  python3 compliance_calc.py sample-size --population 1200 --sample 30 \\
      --frequency daily --freq-table daily=25 --freq-table quarterly=2
"""

from __future__ import annotations

import argparse
import sys


def _parse_rate(s: str) -> float:
    """Parse a rate like '60%' or '0.6' into a fraction (0.6)."""
    s = s.strip()
    try:
        return float(s[:-1]) / 100.0 if s.endswith("%") else float(s)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"must be like '60%' or '0.6', got {s!r}"
        ) from exc


def _parse_factor(s: str) -> tuple[str, float, float]:
    """Parse 'name=score:weight' into (name, score, weight)."""
    try:
        name, rest = s.split("=", 1)
        score_s, weight_s = rest.split(":", 1)
        return name.strip(), float(score_s), float(weight_s)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"must be like 'geography=4:0.4' (name=score:weight), got {s!r}"
        ) from exc


def _parse_band(s: str) -> tuple[str, float]:
    """Parse 'name=upper' into (name, upper_bound)."""
    try:
        name, upper = s.split("=", 1)
        return name.strip(), float(upper)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"must be like 'low=2' (name=upper_bound), got {s!r}"
        ) from exc


def _parse_freq(s: str) -> tuple[str, float]:
    """Parse 'frequency=count' into (frequency, count)."""
    try:
        name, count = s.split("=", 1)
        return name.strip(), float(count)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"must be like 'daily=25' (frequency=count), got {s!r}"
        ) from exc


def cmd_risk_score(args: argparse.Namespace) -> int:
    if not 0.0 <= args.control_effectiveness <= 1.0:
        print("error: --control-effectiveness must be in [0%, 100%]", file=sys.stderr)
        return 2

    inherent = args.likelihood * args.impact
    residual = inherent * (1.0 - args.control_effectiveness)

    print("Risk score — inherent and residual (likelihood x impact)")
    print(f"  likelihood              : {args.likelihood:g}")
    print(f"  impact                  : {args.impact:g}")
    print(f"  INHERENT score          : {inherent:g}")
    print(f"  control effectiveness   : {args.control_effectiveness * 100:g}% reduction")
    print(f"  RESIDUAL score          : {residual:g}")

    if args.appetite_threshold is not None:
        within = residual <= args.appetite_threshold
        verdict = "WITHIN appetite" if within else "OUTSIDE appetite — escalate"
        print(f"  appetite threshold      : {args.appetite_threshold:g}")
        print(f"  -> residual vs appetite : {verdict}")
        if not within:
            print("     route via the risk-rating-and-escalation decision tree to the")
            print("     right authority tier (board / senior-mgmt / line).")
    print("  note: the scale, the control-effectiveness estimate, and the appetite")
    print("        threshold are the FIRM's own — [verify-at-use] against the firm's")
    print("        documented rubric + board-approved appetite statement (CLAUDE.md 3#4).")
    return 0


def cmd_customer_risk(args: argparse.Namespace) -> int:
    total_weight = sum(w for _, _, w in args.factor)
    if total_weight <= 0:
        print("error: factor weights must sum to > 0", file=sys.stderr)
        return 2

    weighted = sum(score * weight for _, score, weight in args.factor)
    normalized = weighted / total_weight

    print("Customer/entity risk — weighted factor score")
    print("  factor        | score | weight | contribution")
    print("  --------------+-------+--------+-------------")
    for name, score, weight in args.factor:
        print(f"  {name:<13} | {score:>5g} | {weight:>6g} | {score * weight:>11.3f}")
    print(f"  sum of weights          : {total_weight:g}")
    print(f"  weighted score          : {weighted:.3f}")
    if abs(total_weight - 1.0) > 1e-9:
        print(f"  normalized (weighted/sum): {normalized:.3f}")
    score_for_band = weighted if abs(total_weight - 1.0) <= 1e-9 else normalized

    if args.band:
        bands = sorted(args.band, key=lambda b: b[1])
        band_name = None
        for name, upper in bands:
            if score_for_band < upper:
                band_name = name
                break
        if band_name is None:
            band_name = f"above {bands[-1][1]:g} (highest band)"
        print(f"  -> band                 : {band_name}")
    print("  note: weights and bands are the FIRM's own model; this computes it, it does")
    print("        NOT decide CDD/EDD depth — that is the regime's rules + the decision")
    print("        tree (CLAUDE.md 3#1, 3#12). [verify-at-use] against the firm's model.")
    return 0


def cmd_sample_size(args: argparse.Namespace) -> int:
    if args.population <= 0:
        print("error: --population must be > 0", file=sys.stderr)
        return 2

    print("Control-testing sampling helper")
    print(f"  population              : {args.population:g}")
    if args.sample is not None:
        if args.sample < 0:
            print("error: --sample must be >= 0", file=sys.stderr)
            return 2
        coverage = (args.sample / args.population) * 100.0
        print(f"  sample                  : {args.sample:g}")
        print(f"  -> coverage             : {coverage:.2f}% of population")

    if args.frequency is not None:
        table = dict(args.freq_table)
        if not table:
            print("  (no --freq-table supplied; cannot look up a reference count)")
        elif args.frequency in table:
            print(f"  frequency               : {args.frequency}")
            print(f"  -> reference count      : {table[args.frequency]:g} "
                  "(from YOUR table — [verify-at-use])")
        else:
            print(f"  frequency '{args.frequency}' not in supplied table "
                  f"{sorted(table)}")
    print("  note: sample sizes are auditor/standard-specific. No standard is hardcoded;")
    print("        this only does the arithmetic you direct. [verify-at-use] against the")
    print("        applicable auditing standard + the firm's testing methodology.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="compliance_calc.py",
        description="Compliance risk-scoring calculator (stdlib only). "
        "Decision-support, NOT legal/regulatory/audit advice — every scale, "
        "weight, and threshold is the firm's own; validate every input.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    rs = sub.add_parser("risk-score", help="Inherent + residual risk score")
    rs.add_argument("--likelihood", type=float, required=True,
                    help="likelihood rating on the firm's scale")
    rs.add_argument("--impact", type=float, required=True,
                    help="impact rating on the firm's scale")
    rs.add_argument("--control-effectiveness", type=_parse_rate, default=0.0,
                    help="fraction by which controls reduce inherent to residual "
                    "(e.g. 60%%; default 0%%)")
    rs.add_argument("--appetite-threshold", type=float, default=None,
                    help="firm's residual-risk appetite threshold for this category "
                    "(optional; enables the within/outside-appetite verdict)")
    rs.set_defaults(func=cmd_risk_score)

    cr = sub.add_parser("customer-risk", help="Weighted customer/entity risk score")
    cr.add_argument("--factor", type=_parse_factor, action="append", required=True,
                    metavar="NAME=SCORE:WEIGHT",
                    help="a risk factor, e.g. 'geography=4:0.4' (repeatable)")
    cr.add_argument("--band", type=_parse_band, action="append", default=[],
                    metavar="NAME=UPPER",
                    help="a band upper-bound, e.g. 'low=2' (repeatable; optional)")
    cr.set_defaults(func=cmd_customer_risk)

    ss = sub.add_parser("sample-size", help="Control-testing sampling helper")
    ss.add_argument("--population", type=float, required=True,
                    help="population the sample is drawn from")
    ss.add_argument("--sample", type=float, default=None,
                    help="sample count, to compute coverage (optional)")
    ss.add_argument("--frequency", type=str, default=None,
                    help="control frequency to look up in --freq-table (optional)")
    ss.add_argument("--freq-table", type=_parse_freq, action="append", default=[],
                    metavar="FREQ=COUNT",
                    help="a frequency->reference-count entry, e.g. 'daily=25' "
                    "(repeatable; no standard is hardcoded)")
    ss.set_defaults(func=cmd_sample_size)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
