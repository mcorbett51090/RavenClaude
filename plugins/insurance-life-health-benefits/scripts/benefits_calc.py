#!/usr/bin/env python3
"""benefits_calc.py — a zero-dependency group-benefits decision calculator.

Removes arithmetic error from three recurring group life/health/employee-benefits
decisions a benefits-advisor / underwriting-and-actuarial-analyst /
enrollment-and-compliance-lead runs constantly:

  loss-ratio    The underwriting loss ratio (incurred claims / earned premium)
                AND, separately, the ACA medical-loss-ratio rebate flag against
                the regulatory threshold (default 80% small / large group; 85%
                large group). Prints the loss ratio, whether an MLR rebate is
                indicated, and the gap to the threshold. Pairs with the
                loss-ratio-is-not-the-mlr best-practice — the underwriting loss
                ratio is NOT the ACA MLR test; both are shown, never conflated.

  contribution  The employer/employee premium SPLIT and total cost. Given a
                total monthly premium and an employer contribution (a percent
                like 75% or a flat dollar amount), prints the employer and
                employee monthly + annual shares and the all-in annual cost
                across a head count. Pairs with the
                contribution-strategy-shapes-enrollment best-practice — the split
                drives take-up and the risk pool, not just cost.

  renewal       The projected renewal premium: current premium x (1 + trend) x
                (1 + experience adjustment) x (1 + demographic adjustment).
                Prints each multiplicative step and the composite change, so a
                "+X%" is decomposed into its parts before anyone reacts. Pairs
                with the decompose-every-renewal best-practice.

This is a CALCULATOR, not a data source — it does not fetch ACA thresholds, loss
trends, or carrier rate actions. The user supplies every input; the tool does the
arithmetic and shows the formula. Stdlib only (argparse); runs anywhere
Python 3.8+ is present.

IMPORTANT: outputs are EDUCATIONAL SCAFFOLDING, not legal, tax, or actuarial
advice (see ../CLAUDE.md §4 #1). A licensed broker, credentialed actuary, or
ERISA counsel signs off the actual decision. Every ACA/MLR figure is
`[verify-at-build]` — re-check the current-year IRS/DOL/CMS threshold before
relying on the rebate flag (CLAUDE.md §4 #10).

Examples
--------
  # Loss ratio: 8.2M incurred claims / 10.0M earned premium, 80% MLR threshold
  python3 benefits_calc.py loss-ratio --incurred-claims 8200000 \\
      --earned-premium 10000000 --mlr-threshold 80%

  # ...large-group 85% threshold
  python3 benefits_calc.py loss-ratio --incurred-claims 8200000 \\
      --earned-premium 10000000 --mlr-threshold 85%

  # Contribution: $1,200/mo premium, employer pays 75%, 120 enrolled
  python3 benefits_calc.py contribution --total-premium 1200 \\
      --employer-share 75% --enrolled 120

  # ...employer pays a flat $700/mo instead
  python3 benefits_calc.py contribution --total-premium 1200 \\
      --employer-flat 700 --enrolled 120

  # Renewal: current $1.0M, trend +8%, experience +6%, demographic +2%
  python3 benefits_calc.py renewal --current-premium 1000000 --trend 8% \\
      --experience 6% --demographic 2%
"""

from __future__ import annotations

import argparse
import sys


def _parse_rate(s: str) -> float:
    """Parse a rate like '80%' or '0.80' into a fraction (0.80)."""
    s = s.strip()
    try:
        return float(s[:-1]) / 100.0 if s.endswith("%") else float(s)
    except ValueError:
        raise argparse.ArgumentTypeError(f"must be like '80%' or '0.80', got {s!r}") from None


def cmd_loss_ratio(args: argparse.Namespace) -> int:
    if args.earned_premium <= 0:
        print("error: --earned-premium must be > 0", file=sys.stderr)
        return 2
    if args.incurred_claims < 0:
        print("error: --incurred-claims must be >= 0", file=sys.stderr)
        return 2
    if not 0.0 < args.mlr_threshold <= 1.0:
        print("error: --mlr-threshold must be in (0%, 100%]", file=sys.stderr)
        return 2

    loss_ratio = args.incurred_claims / args.earned_premium

    print("Loss ratio & ACA MLR rebate flag")
    print(f"  incurred claims  : {args.incurred_claims:,.0f}")
    print(f"  earned premium   : {args.earned_premium:,.0f}")
    print(f"  → underwriting LOSS RATIO (claims / premium): {loss_ratio * 100:6.1f}%")
    print(f"  ACA MLR threshold: {args.mlr_threshold * 100:6.1f}%  [verify-at-build]")

    gap = loss_ratio - args.mlr_threshold
    if loss_ratio < args.mlr_threshold:
        print(f"  → ACA MLR REBATE INDICATED: spent {-gap * 100:.1f} pts below the threshold")
        print("    on claims+quality — a rebate may be owed to the policyholder/members.")
    else:
        print(f"  → no MLR rebate indicated: {gap * 100:.1f} pts at/above the threshold.")
    print("  note: the underwriting loss ratio is NOT the ACA MLR test — the MLR")
    print("        numerator adds quality-improvement spend and applies credibility/")
    print("        risk adjustment, so this rebate flag is a SCREEN, not the filing")
    print("        (loss-ratio-is-not-the-mlr). Educational scaffolding; a credentialed")
    print("        actuary confirms the actual MLR and any rebate (§4 #1, #6).")
    return 0


def cmd_contribution(args: argparse.Namespace) -> int:
    if args.total_premium <= 0:
        print("error: --total-premium must be > 0", file=sys.stderr)
        return 2
    if args.enrolled <= 0:
        print("error: --enrolled must be > 0", file=sys.stderr)
        return 2

    if args.employer_flat is not None:
        if args.employer_flat < 0:
            print("error: --employer-flat must be >= 0", file=sys.stderr)
            return 2
        employer_monthly = min(args.employer_flat, args.total_premium)
        basis = f"flat {args.employer_flat:,.2f}/mo"
    else:
        if not 0.0 <= args.employer_share <= 1.0:
            print("error: --employer-share must be in [0%, 100%]", file=sys.stderr)
            return 2
        employer_monthly = args.total_premium * args.employer_share
        basis = f"{args.employer_share * 100:.1f}% of premium"

    employee_monthly = args.total_premium - employer_monthly
    employer_pct = employer_monthly / args.total_premium

    print("Contribution split — employer / employee premium share")
    print(f"  total premium / enrollee : {args.total_premium:,.2f}/mo  ({args.total_premium * 12:,.2f}/yr)")
    print(f"  basis                    : {basis}")
    print(f"  → EMPLOYER share : {employer_monthly:,.2f}/mo  ({employer_monthly * 12:,.2f}/yr)  [{employer_pct * 100:.1f}%]")
    print(f"  → EMPLOYEE share : {employee_monthly:,.2f}/mo  ({employee_monthly * 12:,.2f}/yr)  [{(1 - employer_pct) * 100:.1f}%]")
    print(f"  enrolled         : {args.enrolled:,}")
    print(f"  → employer ANNUAL cost (all enrollees): {employer_monthly * 12 * args.enrolled:,.2f}")
    print(f"  → employee ANNUAL cost (all enrollees): {employee_monthly * 12 * args.enrolled:,.2f}")
    print(f"  → TOTAL ANNUAL premium (all enrollees): {args.total_premium * 12 * args.enrolled:,.2f}")
    print("  note: the split drives take-up and the risk pool, not just cost — a thin")
    print("        employer share suppresses enrollment and can adversely select the pool")
    print("        (contribution-strategy-shapes-enrollment). Educational scaffolding; a")
    print("        broker confirms affordability/ACA-safe-harbor math (§4 #1).")
    return 0


def cmd_renewal(args: argparse.Namespace) -> int:
    if args.current_premium <= 0:
        print("error: --current-premium must be > 0", file=sys.stderr)
        return 2
    for name, val in (("--trend", args.trend), ("--experience", args.experience),
                      ("--demographic", args.demographic)):
        if val < -1.0:
            print(f"error: {name} must be >= -100%", file=sys.stderr)
            return 2

    after_trend = args.current_premium * (1 + args.trend)
    after_experience = after_trend * (1 + args.experience)
    projected = after_experience * (1 + args.demographic)
    composite = projected / args.current_premium - 1.0

    print("Renewal projection — decomposed multiplicative build-up")
    print(f"  current premium            : {args.current_premium:,.0f}")
    print(f"  × trend            ({args.trend * 100:+.1f}%) : {after_trend:,.0f}")
    print(f"  × experience adj   ({args.experience * 100:+.1f}%) : {after_experience:,.0f}")
    print(f"  × demographic adj  ({args.demographic * 100:+.1f}%) : {projected:,.0f}")
    print(f"  → PROJECTED RENEWAL PREMIUM : {projected:,.0f}")
    print(f"  → composite change          : {composite * 100:+.1f}%")
    print("  note: a renewal is a SUM OF PARTS — trend, own experience, pooling,")
    print("        demographic drift, plan changes. '+X%' is not a finding; decompose")
    print("        it (decompose-every-renewal). In a low-credibility group a single")
    print("        large claim in 'experience' is mostly noise pooling smooths.")
    print("        Educational scaffolding; an actuary/broker signs the rate (§4 #1, #4).")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="benefits_calc.py",
        description="Group life/health/employee-benefits decision calculator (stdlib only). "
        "Educational scaffolding, not legal/tax/actuarial advice — verify every figure.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    lr = sub.add_parser(
        "loss-ratio",
        help="Underwriting loss ratio (claims/premium) + ACA MLR rebate flag",
    )
    lr.add_argument("--incurred-claims", type=float, required=True,
                    help="incurred claims for the period")
    lr.add_argument("--earned-premium", type=float, required=True,
                    help="earned premium for the period")
    lr.add_argument("--mlr-threshold", type=_parse_rate, default=0.80,
                    help="ACA MLR threshold, e.g. 80%% small/85%% large (default 80%%) [verify-at-build]")
    lr.set_defaults(func=cmd_loss_ratio)

    ct = sub.add_parser(
        "contribution",
        help="Employer/employee premium split + total cost across enrollees",
    )
    ct.add_argument("--total-premium", type=float, required=True,
                    help="total monthly premium per enrollee")
    ct.add_argument("--employer-share", type=_parse_rate, default=0.0,
                    help="employer contribution as a percent of premium, e.g. 75%% (default 0%%)")
    ct.add_argument("--employer-flat", type=float, default=None,
                    help="employer contribution as a flat monthly dollar amount (overrides --employer-share)")
    ct.add_argument("--enrolled", type=int, required=True,
                    help="number of enrolled employees")
    ct.set_defaults(func=cmd_contribution)

    rn = sub.add_parser(
        "renewal",
        help="Projected renewal premium = current × trend × experience × demographic",
    )
    rn.add_argument("--current-premium", type=float, required=True,
                    help="current annual (or monthly) premium")
    rn.add_argument("--trend", type=_parse_rate, required=True,
                    help="medical/Rx trend, e.g. 8%%")
    rn.add_argument("--experience", type=_parse_rate, default=0.0,
                    help="own-experience adjustment, e.g. 6%% (default 0%%)")
    rn.add_argument("--demographic", type=_parse_rate, default=0.0,
                    help="demographic-drift adjustment, e.g. 2%% (default 0%%)")
    rn.set_defaults(func=cmd_renewal)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
