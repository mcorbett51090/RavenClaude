#!/usr/bin/env python3
"""grc_calc.py — a zero-dependency GRC arithmetic calculator.

Removes guesswork from three recurring quantitative calls a GRC program runs
constantly. It implements the team's house doctrine — see ../CLAUDE.md §4 and
../knowledge/cybersecurity-grc-decision-trees.md:

  risk-score        Likelihood x impact -> an inherent risk score + band, then
                    apply a control's effectiveness (%) to get the RESIDUAL risk
                    score + band. Makes the "risk drives controls / residual is
                    what the control bought" delta explicit and comparable.

  control-coverage  Of a framework's applicable controls, what % have evidence
                    attached -> a coverage % + a readiness band. Surfaces the
                    gap between "we have controls" (design) and "we can show they
                    operate" (evidence), per a-control-has-three-states.

  audit-readiness   For a Type II window, how much of the required observation
                    period is actually covered by an unbroken evidence record ->
                    a coverage % + a verdict (ready / short-window / gap). Mirrors
                    the Type I vs Type II decision tree's evidence-window gate.

This is a CALCULATOR, not a data source — it does not read a GRC platform, a
risk register, or an evidence store. The user supplies every input; the tool
does the arithmetic and shows the rule it applied. Stdlib only (argparse); runs
anywhere Python 3.9+ is present.

IMPORTANT: outputs are decision-support, not an audit verdict. The scope /
attestation / accept-the-residual-risk call routes to the grc-architect and
ravenclaude-core/security-reviewer (see ../CLAUDE.md §3). A score is only as
honest as the inputs — never let the band substitute for a real gap assessment.

Examples
--------
  # A high-likelihood, high-impact risk with a 70%-effective treating control
  python3 grc_calc.py risk-score --likelihood 4 --impact 5 --effectiveness 70

  # 38 of 64 applicable Annex A controls have evidence attached
  python3 grc_calc.py control-coverage --total 64 --evidenced 38

  # Type II needs a 180-day window; evidence runs unbroken for 135 days
  python3 grc_calc.py audit-readiness --period-days 180 --evidenced-days 135
"""

from __future__ import annotations

import argparse
import sys

# --- risk-score: likelihood x impact, then residual after control -----------
# Bands are defaults to tune to the org's risk appetite, not a standard mandate.
# Default assumes a 5x5 matrix (max raw score 25); --scale changes the matrix
# size and the band thresholds scale proportionally.
_RISK_BANDS = (
    # (lower_fraction_of_max_inclusive, band, note)
    (0.64, "critical", "treat now — top of the register"),
    (0.36, "high", "treat this cycle"),
    (0.16, "medium", "treat or document an owned acceptance"),
    (0.0, "low", "monitor / accept with sign-off"),
)


def _band_for(score: float, max_score: float) -> tuple[str, str]:
    """Resolve the band for a score against the matrix maximum."""
    frac = score / max_score if max_score else 0.0
    for lower, band, note in _RISK_BANDS:
        if frac >= lower:
            return band, note
    return "low", "monitor / accept with sign-off"


def cmd_risk_score(a: argparse.Namespace) -> int:
    if a.scale < 2:
        print("error: --scale must be >= 2", file=sys.stderr)
        return 2
    if not 1 <= a.likelihood <= a.scale:
        print(f"error: --likelihood must be 1..{a.scale}", file=sys.stderr)
        return 2
    if not 1 <= a.impact <= a.scale:
        print(f"error: --impact must be 1..{a.scale}", file=sys.stderr)
        return 2
    if not 0.0 <= a.effectiveness <= 100.0:
        print("error: --effectiveness must be 0..100", file=sys.stderr)
        return 2

    max_score = float(a.scale * a.scale)
    inherent = float(a.likelihood * a.impact)
    residual = round(inherent * (1.0 - a.effectiveness / 100.0), 2)
    in_band, in_note = _band_for(inherent, max_score)
    res_band, res_note = _band_for(residual, max_score)

    print("GRC risk score — inherent -> residual")
    print("-" * 54)
    print(f"  Matrix              : {a.scale}x{a.scale} (max raw {int(max_score)})")
    print(f"  Likelihood          : {a.likelihood}")
    print(f"  Impact              : {a.impact}")
    print(f"  Inherent risk       : {int(inherent)}  ({in_band.upper()} — {in_note})")
    print(f"  Control effectiveness: {a.effectiveness:.0f}%")
    print("-" * 54)
    print(f"  RESIDUAL risk       : {residual:g}  ({res_band.upper()} — {res_note})")
    print(f"  Risk reduced by     : {inherent - residual:g} ({a.effectiveness:.0f}% of inherent)")
    print("-" * 54)
    print("  Note: residual is what the control bought. Effectiveness is your")
    print("  honest estimate, not the control's design rating — a written")
    print("  control with no evidence it operates is 0% effective for Type II.")
    print("  The accept-the-residual call routes to grc-architect + sign-off.")
    return 0


# --- control-coverage: % of applicable controls with evidence ---------------
_COVERAGE_BANDS = (
    (95.0, "audit-ready", "evidence depth supports fieldwork"),
    (80.0, "near-ready", "close the named evidence gaps before fieldwork"),
    (50.0, "in-progress", "design exists; evidence is the gap — not Type II ready"),
    (0.0, "early", "controls are mostly design-only; stand up evidence first"),
)


def _coverage_band(pct: float) -> tuple[str, str]:
    for lower, band, note in _COVERAGE_BANDS:
        if pct >= lower:
            return band, note
    return "early", "controls are mostly design-only; stand up evidence first"


def cmd_control_coverage(a: argparse.Namespace) -> int:
    if a.total <= 0:
        print("error: --total must be > 0", file=sys.stderr)
        return 2
    if not 0 <= a.evidenced <= a.total:
        print("error: --evidenced must be 0..--total", file=sys.stderr)
        return 2

    pct = round(100.0 * a.evidenced / a.total, 1)
    band, note = _coverage_band(pct)
    missing = a.total - a.evidenced

    print("Control evidence coverage")
    print("-" * 54)
    print(f"  Applicable controls : {a.total}")
    print(f"  With evidence       : {a.evidenced}")
    print(f"  Missing evidence    : {missing}")
    print("-" * 54)
    print(f"  COVERAGE            : {pct:g}%  ({band.upper()})")
    print(f"  Read                : {note}")
    print("-" * 54)
    print("  Note: coverage counts controls with evidence the control OPERATED,")
    print("  not controls that merely exist on paper (a-control-has-three-states).")
    print("  Exclude any control scoped out in the SoA from --total, with a")
    print("  justification — don't inflate coverage by dropping hard controls.")
    return 0


# --- audit-readiness: Type II observation-period evidence coverage ----------
def cmd_audit_readiness(a: argparse.Namespace) -> int:
    if a.period_days <= 0:
        print("error: --period-days must be > 0", file=sys.stderr)
        return 2
    if a.evidenced_days < 0:
        print("error: --evidenced-days must be >= 0", file=sys.stderr)
        return 2

    capped = min(a.evidenced_days, a.period_days)
    pct = round(100.0 * capped / a.period_days, 1)
    shortfall = a.period_days - capped

    if pct >= 100.0:
        verdict = "ready"
        note = "the observation window is fully covered by evidence"
    elif pct >= 90.0:
        verdict = "short-window"
        note = f"close the {shortfall}-day shortfall or move the report date to the window"
    else:
        verdict = "gap"
        note = "evidence does not span the period — a back-fill is not evidence; expect an exception"

    over = a.evidenced_days - a.period_days
    print("Type II audit readiness — observation-period coverage")
    print("-" * 60)
    print(f"  Required period     : {a.period_days} days")
    print(f"  Evidenced (unbroken): {a.evidenced_days} days" + (f" (capped at {a.period_days})" if over > 0 else ""))
    print(f"  Shortfall           : {shortfall} days")
    print("-" * 60)
    print(f"  COVERAGE            : {pct:g}%")
    print(f"  VERDICT             : {verdict.upper()}")
    print(f"  Read                : {note}")
    print("-" * 60)
    print("  Note: evidence created after the fact for a past period is not")
    print("  evidence the control operated then. Set the report date to the")
    print("  evidence window, not the sales calendar (evidence-is-a-system).")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="grc_calc.py",
        description="GRC arithmetic calculator (decision-support, not an audit verdict).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="command", required=True)

    rs = sub.add_parser("risk-score", help="likelihood x impact -> inherent + residual risk band")
    rs.add_argument("--likelihood", type=int, required=True, help="likelihood 1..scale")
    rs.add_argument("--impact", type=int, required=True, help="impact 1..scale")
    rs.add_argument(
        "--effectiveness",
        type=float,
        default=0.0,
        help="treating-control effectiveness 0..100 (default 0 = inherent only)",
    )
    rs.add_argument("--scale", type=int, default=5, help="matrix size, e.g. 5 for a 5x5 (default 5)")
    rs.set_defaults(func=cmd_risk_score)

    cc = sub.add_parser("control-coverage", help="% of applicable controls with evidence")
    cc.add_argument("--total", type=int, required=True, help="count of applicable (in-scope) controls")
    cc.add_argument("--evidenced", type=int, required=True, help="count with operating evidence attached")
    cc.set_defaults(func=cmd_control_coverage)

    ar = sub.add_parser("audit-readiness", help="Type II observation-period evidence coverage")
    ar.add_argument("--period-days", type=int, required=True, help="required observation period in days")
    ar.add_argument("--evidenced-days", type=int, required=True, help="days of unbroken evidence collected")
    ar.set_defaults(func=cmd_audit_readiness)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
