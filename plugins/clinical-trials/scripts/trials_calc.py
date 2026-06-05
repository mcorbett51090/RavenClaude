#!/usr/bin/env python3
"""trials_calc.py — a zero-dependency clinical-trial decision calculator.

Removes arithmetic error from three recurring clinical-operations decisions a
sponsor / CRO / clinical-ops lead runs constantly:

  enrollment-feasibility  Can the (current or expanded) site footprint hit the
                          randomization target on time?
                              projected = active_sites x rate_per_site_per_month
                                          x months_remaining
                          Prints projected enrollment, the gap to target, and
                          the breakeven (rate-per-site OR added-sites) needed to
                          close it. Pairs with the enrollment-shortfall-recovery
                          decision tree (knowledge/trials-enrollment-shortfall-
                          recovery-decision-tree.md).

  recruitment-funnel      The costed funnel: how many must you SCREEN to hit the
                          enrolled target given a screen-fail rate, and what the
                          recruitment spend is at a per-patient cost. Flags the
                          screen-to-enroll ratio. Pairs with knowledge/trials-
                          kpi-glossary.md and the plan-recruitment-funnel skill.

  retention-roi           Retain vs re-recruit: the cost of replacing the
                          patients you expect to lose at a given dropout rate,
                          vs the cost of a per-patient retention intervention.
                          Prints the breakeven dropout-reduction the intervention
                          must achieve to pay for itself. Pairs with knowledge/
                          trials-operations-economics.md and the design-for-
                          retention skill.

This is a CALCULATOR, not a data source — it does not fetch benchmarks, costs,
or live trial data. The user supplies every input; the tool does the arithmetic
and shows the formula. Stdlib only (argparse); runs anywhere Python 3.8+ is
present.

IMPORTANT: outputs are decision-support, not clinical, regulatory, or statistical
advice (see ../CLAUDE.md §2). It makes no eligibility, safety, or approvability
determination. Validate every figure against the trial's actual data and a
qualified biostatistician before any deliverable (CLAUDE.md §3 #8). For a
statistically rigorous sample-size / power calculation, use a validated
statistical package and a biostatistician — this tool does operational feasibility
arithmetic, NOT inferential sample-size estimation.

Examples
--------
  # Enrollment feasibility: 25 active sites, 0.8 randomizations/site/month,
  # 9 months left, target 300 randomized
  python3 trials_calc.py enrollment-feasibility --active-sites 25 \\
      --rate-per-site 0.8 --months-remaining 9 --target 300

  # Recruitment funnel: need 300 enrolled at a 40% screen-fail rate,
  # ~$6,533 to recruit each enrolled patient
  python3 trials_calc.py recruitment-funnel --target-enrolled 300 \\
      --screen-fail-rate 40% --cost-per-patient 6533

  # Retention ROI: 300 enrolled, expected 30% dropout, $19,533 to replace one,
  # a $400/patient retention program
  python3 trials_calc.py retention-roi --enrolled 300 --dropout-rate 30% \\
      --replacement-cost 19533 --intervention-cost-per-patient 400
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


def cmd_enrollment_feasibility(args: argparse.Namespace) -> int:
    if args.active_sites < 0 or args.rate_per_site < 0 or args.months_remaining < 0:
        print("error: sites, rate, and months must be >= 0", file=sys.stderr)
        return 2
    if args.target <= 0:
        print("error: --target must be > 0", file=sys.stderr)
        return 2

    projected = args.active_sites * args.rate_per_site * args.months_remaining
    gap = args.target - projected

    print("Enrollment feasibility — sites x rate x months vs target")
    print(f"  active sites            : {args.active_sites:g}")
    print(f"  rate / site / month     : {args.rate_per_site:g}")
    print(f"  months remaining        : {args.months_remaining:g}")
    print(f"  target (randomized)      : {args.target:,.0f}")
    print(f"  → projected enrollment   : {projected:,.1f}")

    if gap <= 0:
        print(f"  → on track: projected exceeds target by {-gap:,.1f}")
        return 0

    print(f"  → SHORT by               : {gap:,.1f}")
    # Breakeven rate per site (holding sites + months constant)
    denom_rate = args.active_sites * args.months_remaining
    if denom_rate > 0:
        needed_rate = args.target / denom_rate
        print(f"  → rate/site/month needed : {needed_rate:,.3f} "
              f"(current {args.rate_per_site:g})")
    # Breakeven added sites (holding rate + months constant)
    denom_sites = args.rate_per_site * args.months_remaining
    if denom_sites > 0:
        needed_sites = args.target / denom_sites
        added = max(needed_sites - args.active_sites, 0.0)
        print(f"  → total sites needed     : {needed_sites:,.1f} "
              f"(add ~{added:,.1f}; remember each carries an activation long pole)")
    print("  note: a low RATE is a funnel/eligibility problem (fix upstream FIRST);")
    print("        too few SITES at a healthy rate is the case expansion fits (§3 #4, #5).")
    return 0


def cmd_recruitment_funnel(args: argparse.Namespace) -> int:
    if not 0.0 <= args.screen_fail_rate < 1.0:
        print("error: --screen-fail-rate must be in [0%, 100%)", file=sys.stderr)
        return 2
    if args.target_enrolled <= 0:
        print("error: --target-enrolled must be > 0", file=sys.stderr)
        return 2

    enroll_rate = 1.0 - args.screen_fail_rate  # fraction of screened who enroll
    screens_needed = args.target_enrolled / enroll_rate
    screen_to_enroll = screens_needed / args.target_enrolled

    print("Recruitment funnel — screens needed + recruitment spend")
    print(f"  target enrolled         : {args.target_enrolled:,.0f}")
    print(f"  screen-fail rate        : {args.screen_fail_rate * 100:g}%")
    print(f"  → screens needed         : {screens_needed:,.0f}")
    print(f"  → screen-to-enroll ratio : {screen_to_enroll:,.2f} screened per 1 enrolled")

    if args.cost_per_patient is not None:
        spend = args.cost_per_patient * args.target_enrolled
        print(f"  cost per enrolled patient: {args.cost_per_patient:,.0f}")
        print(f"  → recruitment spend      : {spend:,.0f}")
    print("  note: a high screen-to-enroll ratio is an eligibility-criteria signal —")
    print("        restrictive criteria are the biggest enrollment killer (§3 #1).")
    return 0


def cmd_retention_roi(args: argparse.Namespace) -> int:
    if not 0.0 <= args.dropout_rate <= 1.0:
        print("error: --dropout-rate must be in [0%, 100%]", file=sys.stderr)
        return 2
    if args.enrolled <= 0:
        print("error: --enrolled must be > 0", file=sys.stderr)
        return 2

    expected_dropouts = args.enrolled * args.dropout_rate
    replacement_spend = expected_dropouts * args.replacement_cost
    intervention_spend = args.intervention_cost_per_patient * args.enrolled

    print("Retention ROI — replace-the-lost vs retain-up-front")
    print(f"  enrolled                 : {args.enrolled:,.0f}")
    print(f"  expected dropout rate    : {args.dropout_rate * 100:g}%")
    print(f"  → expected dropouts      : {expected_dropouts:,.1f}")
    print(f"  cost to replace one      : {args.replacement_cost:,.0f}")
    print(f"  → replacement spend      : {replacement_spend:,.0f}")
    print(f"  retention program / pt   : {args.intervention_cost_per_patient:,.0f}")
    print(f"  → retention program spend: {intervention_spend:,.0f} (applied to all enrolled)")

    # Breakeven: how many fewer dropouts must the program produce to pay for itself?
    if args.replacement_cost > 0:
        dropouts_to_avert = intervention_spend / args.replacement_cost
        # As a reduction in the dropout RATE:
        rate_reduction = dropouts_to_avert / args.enrolled
        print(f"  → breakeven: program must avert {dropouts_to_avert:,.1f} dropouts")
        print(f"    = a {rate_reduction * 100:.1f} percentage-point cut in the dropout rate")
        print("    (below that it pays for itself; above it, retain beats re-recruit — §3 #3)")
    print("  note: model the dropout rate from REAL trial/indication data, not a guess;")
    print("        replacement is far costlier than retention by design (§3 #2, #3).")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="trials_calc.py",
        description="Clinical-trial operations decision calculator (stdlib only). "
        "Decision-support, not clinical/regulatory/statistical advice — validate every "
        "input; NOT a sample-size/power tool.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    ef = sub.add_parser("enrollment-feasibility",
                        help="Sites x rate x months vs the randomization target")
    ef.add_argument("--active-sites", type=float, required=True,
                    help="number of actively-enrolling sites")
    ef.add_argument("--rate-per-site", type=float, required=True,
                    help="randomizations per site per month")
    ef.add_argument("--months-remaining", type=float, required=True,
                    help="months left in the enrollment window")
    ef.add_argument("--target", type=float, required=True,
                    help="enrollment / randomization target")
    ef.set_defaults(func=cmd_enrollment_feasibility)

    rf = sub.add_parser("recruitment-funnel",
                        help="Screens needed + recruitment spend for an enrolled target")
    rf.add_argument("--target-enrolled", type=float, required=True,
                    help="number of patients to enroll")
    rf.add_argument("--screen-fail-rate", type=_parse_rate, required=True,
                    help="fraction of screened patients who fail screening (e.g. 40%%)")
    rf.add_argument("--cost-per-patient", type=float, default=None,
                    help="recruitment cost per enrolled patient (optional, for spend)")
    rf.set_defaults(func=cmd_recruitment_funnel)

    rr = sub.add_parser("retention-roi",
                        help="Replace-the-lost vs retain-up-front breakeven")
    rr.add_argument("--enrolled", type=float, required=True,
                    help="number of patients enrolled")
    rr.add_argument("--dropout-rate", type=_parse_rate, required=True,
                    help="expected fraction lost to dropout (e.g. 30%%)")
    rr.add_argument("--replacement-cost", type=float, required=True,
                    help="cost to recruit a replacement for one lost patient")
    rr.add_argument("--intervention-cost-per-patient", type=float, required=True,
                    help="per-patient cost of the retention program (applied to all enrolled)")
    rr.set_defaults(func=cmd_retention_roi)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
