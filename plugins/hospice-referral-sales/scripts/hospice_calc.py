#!/usr/bin/env python3
"""hospice_calc.py — a zero-dependency hospice referral-sales decision calculator.

Removes arithmetic error from four recurring numbers a hospice sales / community
liaison and their manager run constantly:

  funnel                 The referral-to-admission funnel. Takes referrals + the
                         admit (conversion) rate, prints projected admissions, the
                         non-converting count, optional time-to-admission context,
                         and optional cost-per-admission. Pairs with
                         skills/admissions-funnel-analytics and the declined-referral
                         decision tree.

  census                 Census as a flow. Projects end-of-period average daily
                         census from start census + admits - discharges, the net
                         change, and (with a per-diem) the patient-day revenue at
                         stake. PER-DIEM IS AN EXAMPLE INPUT — confirm the current
                         CMS rate; this tool does not fetch rates.

  benefit-periods        The Medicare Hospice Benefit period + recertification
                         schedule from an election date: two 90-day periods then
                         unlimited 60-day periods, with the recert and face-to-face
                         (3rd period onward) timing flags. Period lengths follow the
                         published CMS structure; confirm the current rule.

  eligibility-indicators An EDUCATIONAL tally of which published clinical-decline
                         indicators are present in a DE-IDENTIFIED profile (PPS,
                         weight loss, hospitalizations, FAST stage). It DOES NOT
                         certify or determine eligibility. It lists the indicators
                         present and prints the standing "route to the attending
                         physician / hospice medical director for certification"
                         line. No patient-identifying data should ever be passed in.

This is a CALCULATOR, not a data or determination source. It does not fetch CMS
rates, does not certify eligibility, and does not render compliance rulings. The
user supplies every input; the tool does the arithmetic and shows the formula.
Stdlib only (argparse, datetime); runs anywhere Python 3.8+ is present.

IMPORTANT: every output is decision-support, NOT clinical, legal, or regulatory
advice (see ../CLAUDE.md sections 3 and 5). Hospice eligibility is certified by the
attending physician and the hospice medical director; compliance is ruled on by the
agency compliance officer and counsel. Validate every figure against the current
CMS rule, the specific LCD, and your program's data before any deliverable.

Examples
--------
  # Funnel: 80 referrals, 65% admit rate, 1.8-day avg time-to-admit, $1,200/admit
  python3 hospice_calc.py funnel --referrals 80 --admit-rate 65% \\
      --time-to-admit 1.8 --cost-per-admission 1200

  # Census flow: start 120, +22 admits, -18 discharges over 30 days, $225 per-diem
  python3 hospice_calc.py census --start 120 --admits 22 --discharges 18 \\
      --days 30 --per-diem 225

  # Benefit-period schedule from an election date
  python3 hospice_calc.py benefit-periods --election 2026-01-15

  # Educational indicator tally (DE-IDENTIFIED — defers to physician certification)
  python3 hospice_calc.py eligibility-indicators --pps 40 --weight-loss 12% \\
      --hospitalizations 3 --fast 7a
"""

import argparse
import sys
from datetime import date, datetime, timedelta

CERT_LINE = (
    "EDUCATION ONLY — the attending physician and hospice medical director "
    "certify eligibility on clinical judgment. This tool does not certify."
)
ADVICE_LINE = (
    "Decision-support only — not clinical, legal, or regulatory advice. "
    "Confirm every figure against the current CMS rule / LCD and your data."
)


def _pct(value: str) -> float:
    """Parse a percentage that may be written '65%' or '65' or '0.65'."""
    text = value.strip().rstrip("%")
    number = float(text)
    if value.strip().endswith("%") or number > 1:
        return number / 100.0
    return number


def _rule(title: str) -> str:
    return f"\n=== {title} ===\n"


def cmd_funnel(args: argparse.Namespace) -> int:
    referrals = args.referrals
    rate = _pct(args.admit_rate)
    admits = referrals * rate
    non_converting = referrals - admits

    print(_rule("Referral-to-admission funnel"))
    print(f"  Referrals received        : {referrals:,.0f}")
    print(f"  Admit (conversion) rate   : {rate * 100:.1f}%")
    print(f"  Projected admissions      : {admits:,.1f}")
    print(f"  Non-converting referrals  : {non_converting:,.1f}")
    print("  Formula                   : admissions = referrals x admit_rate")

    if args.time_to_admit is not None:
        print(f"  Avg time-to-admission     : {args.time_to_admit:.1f} days")
        print(
            "  Note                      : time-to-admission is a conversion "
            "lever — slow responses lose referrals to faster agencies."
        )
    if args.cost_per_admission is not None:
        total = admits * args.cost_per_admission
        print(f"  Cost per admission        : ${args.cost_per_admission:,.2f}")
        print(f"  Projected acquisition cost: ${total:,.2f}")

    print(
        "\n  Every declined referral needs a root cause and an owner "
        "(see the declined-referral decision tree)."
    )
    print(f"\n{ADVICE_LINE}")
    return 0


def cmd_census(args: argparse.Namespace) -> int:
    start = args.start
    net = args.admits - args.discharges
    end = start + net
    avg_daily = (start + end) / 2.0

    print(_rule("Census as a flow"))
    print(f"  Start census              : {start:,.0f}")
    print(f"  Admissions                : +{args.admits:,.0f}")
    print(f"  Discharges                : -{args.discharges:,.0f}")
    print(f"  Net change                : {net:+,.0f}")
    print(f"  End census                : {end:,.0f}")
    print(f"  Approx average daily census: {avg_daily:,.1f}")
    print(f"  Period length             : {args.days:,.0f} days")
    print(
        "  Formula                   : end = start + admits - discharges; "
        "ADC approx (start + end) / 2"
    )

    if args.per_diem is not None:
        patient_days = avg_daily * args.days
        revenue = patient_days * args.per_diem
        print(f"  Per-diem (EXAMPLE input)  : ${args.per_diem:,.2f}  [confirm CMS rate]")
        print(f"  Approx patient-days       : {patient_days:,.0f}")
        print(f"  Approx period revenue     : ${revenue:,.2f}")

    print(
        "\n  A short average/median length of stay is the signature of LATE "
        "referrals — read it as an upstream education gap, not an intake problem."
    )
    print(f"\n{ADVICE_LINE}")
    return 0


def cmd_benefit_periods(args: argparse.Namespace) -> int:
    try:
        election = datetime.strptime(args.election, "%Y-%m-%d").date()
    except ValueError:
        print("error: --election must be YYYY-MM-DD", file=sys.stderr)
        return 2

    if args.periods < 1:
        print("error: --periods must be >= 1", file=sys.stderr)
        return 2

    # Published MHB structure: two 90-day periods, then unlimited 60-day periods.
    # Slice to the requested count so the printed count always equals --periods
    # (a bare [90, 90] + [60] * (periods - 2) prints 2 periods even for periods=1).
    lengths = ([90, 90] + [60] * max(args.periods - 2, 0))[: args.periods]
    print(_rule("Medicare Hospice Benefit — period & recertification schedule"))
    print(f"  Election date             : {election.isoformat()}")
    print("  Structure                 : two 90-day periods, then 60-day periods")

    cursor: date = election
    for index, length in enumerate(lengths, start=1):
        period_end = cursor + timedelta(days=length)
        f2f = " (face-to-face encounter required before this period)" if index >= 3 else ""
        print(
            f"  Period {index:>2} : {cursor.isoformat()} -> {period_end.isoformat()} "
            f"({length} days) — recertify at start{f2f}"
        )
        cursor = period_end

    print(
        "\n  Recertification of the terminal prognosis is required at the start of "
        "each period; a face-to-face encounter is required before the 3rd period "
        "and each subsequent one.  [confirm the current CMS rule]"
    )
    print(f"\n{ADVICE_LINE}")
    return 0


def cmd_eligibility_indicators(args: argparse.Namespace) -> int:
    print(_rule("Eligibility-indicator tally  (EDUCATIONAL — NOT a certification)"))
    print(f"  {CERT_LINE}\n")

    present: list[str] = []
    if args.pps is not None:
        flag = " <- supports a decline picture" if args.pps <= 40 else ""
        print(f"  PPS (Palliative Performance Scale): {args.pps:.0f}%{flag}")
        if args.pps <= 40:
            present.append("low/declining PPS (<= 40%)")
    if args.weight_loss is not None:
        loss = _pct(args.weight_loss) * 100
        flag = " <- supports nutritional decline" if loss >= 10 else ""
        print(f"  Recent unintentional weight loss  : {loss:.1f}%{flag}")
        if loss >= 10:
            present.append("significant weight loss (>= 10%)")
    if args.hospitalizations is not None:
        flag = " <- supports recurrent acute events" if args.hospitalizations >= 2 else ""
        print(f"  Hospitalizations / ED visits      : {args.hospitalizations:.0f}{flag}")
        if args.hospitalizations >= 2:
            present.append("multiple recent hospitalizations (>= 2)")
    if args.fast is not None:
        anchor = args.fast.lower().startswith("7")
        flag = " <- dementia LCD anchor (with a complication)" if anchor else ""
        print(f"  FAST stage (dementia)             : {args.fast}{flag}")
        if anchor:
            present.append("FAST stage 7 (dementia anchor)")
    if args.recurrent_infection:
        print("  Recurrent infection               : yes <- supports decline")
        present.append("recurrent infection")

    print("\n  Indicators present in this profile:")
    if present:
        for item in present:
            print(f"    - {item}")
        print(
            "\n  Read: this DE-IDENTIFIED picture shows published decline indicators "
            "and WARRANTS AN ATTENDING-PHYSICIAN CONVERSATION. It does NOT mean the "
            "patient is eligible — that is the physician's and medical director's "
            "certification."
        )
    else:
        print("    - none of the screened indicators met the example thresholds")
        print(
            "\n  Read: educate the source on the decline picture and re-screen as the "
            "trajectory develops. Thresholds here are EXAMPLES — confirm against the "
            "current LCD."
        )

    print(f"\n  {CERT_LINE}")
    print(f"{ADVICE_LINE}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hospice_calc.py",
        description="Hospice referral-sales calculator (decision-support only).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_funnel = sub.add_parser("funnel", help="referral-to-admission funnel")
    p_funnel.add_argument("--referrals", type=float, required=True)
    p_funnel.add_argument("--admit-rate", required=True, help="e.g. 65% or 0.65")
    p_funnel.add_argument("--time-to-admit", type=float, default=None, help="days")
    p_funnel.add_argument("--cost-per-admission", type=float, default=None)
    p_funnel.set_defaults(func=cmd_funnel)

    p_census = sub.add_parser("census", help="census as a flow + revenue at per-diem")
    p_census.add_argument("--start", type=float, required=True)
    p_census.add_argument("--admits", type=float, required=True)
    p_census.add_argument("--discharges", type=float, required=True)
    p_census.add_argument("--days", type=float, default=30)
    p_census.add_argument("--per-diem", type=float, default=None, help="EXAMPLE input")
    p_census.set_defaults(func=cmd_census)

    p_bp = sub.add_parser("benefit-periods", help="benefit-period & recert schedule")
    p_bp.add_argument("--election", required=True, help="YYYY-MM-DD")
    p_bp.add_argument("--periods", type=int, default=5, help="how many to project")
    p_bp.set_defaults(func=cmd_benefit_periods)

    p_elig = sub.add_parser(
        "eligibility-indicators",
        help="EDUCATIONAL decline-indicator tally (defers to physician)",
    )
    p_elig.add_argument("--pps", type=float, default=None, help="PPS percent, e.g. 40")
    p_elig.add_argument("--weight-loss", default=None, help="e.g. 12% or 0.12")
    p_elig.add_argument("--hospitalizations", type=float, default=None)
    p_elig.add_argument("--fast", default=None, help="FAST stage, e.g. 7a")
    p_elig.add_argument("--recurrent-infection", action="store_true")
    p_elig.set_defaults(func=cmd_eligibility_indicators)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
