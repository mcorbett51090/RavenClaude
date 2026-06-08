#!/usr/bin/env python3
"""hr_calc.py — a zero-dependency People-Ops / HR decision calculator.

Removes arithmetic error from three recurring total-rewards decisions a
total-rewards-analyst / people-ops-generalist / HR leader runs constantly:

  comp-band     Range mechanics for one band from its min/mid/max — the
                range-spread ((max - min) / min), the implied min/max ratios to
                the midpoint, and a compa-ratio (salary / midpoint) when a
                --salary is supplied. Compa-ratio places a person IN the range;
                it is a position diagnostic, NOT a fairness verdict (see
                ../best-practices/compa-ratio-reads-position-not-fairness.md).
                A band with no LEVEL under it has no logic for who lands where —
                level first (../best-practices/level-before-band.md).

  pay-equity    The UNADJUSTED group mean gap between a focal group and a
                reference group — the mean of each, the raw dollar gap, and the
                simple unadjusted ratio (focal mean / reference mean). This is
                deliberately the RAW number: it controls for NOTHING (level,
                tenure, location, performance) and therefore proves NOTHING on
                its own. It is a screening prompt to run the CONTROLLED review,
                never an equal-pay determination — that certification is
                counsel's (../best-practices/pay-equity-controls-for-legitimate
                -factors.md and flag-employment-law-for-counsel-never-opine.md).

  offer         A total-comp build from base + bonus + equity — the cash comp
                (base + target bonus), the annualized equity value (grant / vest
                years), the total target comp, and each component's share. The
                tool builds the NUMBER; it does NOT opine on FLSA exempt status,
                pay-transparency posting duties, or any classification — those
                are flagged for counsel, never answered here.

This is a CALCULATOR, not a data source — it does not fetch market data, pull an
HRIS/ATS, or read a comp survey. The user supplies every input; the tool does the
arithmetic and shows the formula. Stdlib only (argparse); runs anywhere Python
3.8+ is present.

NOT LEGAL ADVICE. No output here is an employment-law determination. Every point
that touches FLSA classification, EEO, equal-pay certification, leave
entitlement, or pay-transparency is flagged for qualified counsel, never opined
on (../CLAUDE.md §4 #1). A raw pay gap the tool prints is a prompt to run the
controlled review, not proof of anything.

Examples
--------
  # Comp band: min 80,000, mid 100,000, max 120,000; place a 92,000 salary.
  python3 hr_calc.py comp-band --min 80000 --mid 100000 --max 120000 \\
      --salary 92000

  # Pay equity: focal-group salaries vs reference-group salaries (raw screen).
  python3 hr_calc.py pay-equity \\
      --focal 88000 --focal 91000 --focal 84000 \\
      --reference 96000 --reference 102000 --reference 99000

  # Offer: 120,000 base, 15% target bonus, a 240,000 equity grant over 4 years.
  python3 hr_calc.py offer --base 120000 --bonus-pct 15% \\
      --equity-grant 240000 --vest-years 4
"""

from __future__ import annotations

import argparse
import sys


def _pct(x: float) -> str:
    return f"{x * 100:.1f}%"


def _parse_rate(s: str) -> float:
    """Parse a rate like '15%' or '0.15' into a fraction (0.15)."""
    s = s.strip()
    try:
        return float(s[:-1]) / 100.0 if s.endswith("%") else float(s)
    except ValueError as err:
        raise argparse.ArgumentTypeError(
            f"must be like '15%' or '0.15', got {s!r}"
        ) from err


def cmd_comp_band(args: argparse.Namespace) -> int:
    lo, mid, hi = args.min, args.mid, args.max
    if not lo < mid < hi:
        print("error: require --min < --mid < --max", file=sys.stderr)
        return 2
    if lo <= 0:
        print("error: --min must be > 0", file=sys.stderr)
        return 2

    # Range spread is the band's width as a fraction of its floor.
    spread = (hi - lo) / lo
    min_to_mid = lo / mid
    max_to_mid = hi / mid

    print("Comp band — range mechanics (level first, then band)")
    print(f"  min / mid / max        : {lo:,.0f} / {mid:,.0f} / {hi:,.0f}")
    print(f"  → range spread         : {_pct(spread)}  ((max - min) / min)")
    print(f"  → min as % of midpoint : {_pct(min_to_mid)}")
    print(f"  → max as % of midpoint : {_pct(max_to_mid)}")

    if spread < 0.20:
        print("  note: a spread under ~20% is tight — little room for in-band")
        print("        growth before someone bumps the ceiling and needs a")
        print("        PROMOTION (a new level), not a raise.")
    elif spread > 0.60:
        print("  note: a spread over ~60% is wide — confirm it is one level, not")
        print("        two levels collapsed into a single band (level first).")

    if args.salary is not None:
        if args.salary <= 0:
            print("error: --salary must be > 0", file=sys.stderr)
            return 2
        compa = args.salary / mid
        print()
        print(f"  salary supplied        : {args.salary:,.0f}")
        print(f"  → compa-ratio          : {compa:.3f}  (salary / midpoint)")
        if compa < 0.80:
            band_pos = "BELOW range start — confirm placement or a correction"
        elif compa < 0.95:
            band_pos = "lower third — typical for new-to-level / still ramping"
        elif compa <= 1.05:
            band_pos = "around midpoint — fully-competent target zone"
        elif compa <= args.max / mid:
            band_pos = "upper third — tenured / strong; watch the ceiling"
        else:
            band_pos = "ABOVE range max — ceiling-bumper; promotion not a raise"
        print(f"  → position read        : {band_pos}")
        print("  reminder: compa-ratio places someone IN the range — it is a")
        print("            POSITION diagnostic, not an equity verdict. Read it")
        print("            against level, tenure, and performance, never alone.")
    print("  NOT legal advice: pay-transparency / posting duties → counsel.")
    return 0


def _mean(xs: list[float]) -> float:
    return sum(xs) / len(xs)


def cmd_pay_equity(args: argparse.Namespace) -> int:
    focal, ref = args.focal, args.reference
    if len(focal) < 1 or len(ref) < 1:
        print("error: need >= 1 --focal and >= 1 --reference value", file=sys.stderr)
        return 2
    if any(v <= 0 for v in focal + ref):
        print("error: every salary must be > 0", file=sys.stderr)
        return 2

    focal_mean = _mean(focal)
    ref_mean = _mean(ref)
    gap = ref_mean - focal_mean
    ratio = focal_mean / ref_mean

    print("Pay equity — UNADJUSTED raw screen (controls for NOTHING)")
    print(f"  focal group     : n={len(focal)}, mean {focal_mean:,.0f}")
    print(f"  reference group : n={len(ref)}, mean {ref_mean:,.0f}")
    print(f"  → raw mean gap  : {gap:,.0f}  (reference mean - focal mean)")
    print(f"  → unadjusted ratio : {ratio:.4f}  ({_pct(ratio)} of reference)")
    print()
    print("  ⚠ THIS NUMBER PROVES NOTHING ON ITS OWN. It is the raw, uncontrolled")
    print("    gap — it does NOT control for level, tenure, location, or")
    print("    performance, so a difference here may be entirely legitimate")
    print("    (e.g. a seniority mix) or may hide real inequity. Use it ONLY as a")
    print("    screening prompt to run the CONTROLLED review and surface the")
    print("    UNEXPLAINED residual (pay-equity-controls-for-legitimate-factors).")
    print("  NOT legal advice: the equal-pay compliance certification is")
    print("    COUNSEL'S, never the analyst's. Do NOT self-certify compliant.")
    return 0


def cmd_offer(args: argparse.Namespace) -> int:
    base = args.base
    if base <= 0:
        print("error: --base must be > 0", file=sys.stderr)
        return 2
    if args.bonus_pct < 0:
        print("error: --bonus-pct must be >= 0", file=sys.stderr)
        return 2
    if args.equity_grant < 0:
        print("error: --equity-grant must be >= 0", file=sys.stderr)
        return 2
    if args.vest_years <= 0:
        print("error: --vest-years must be > 0", file=sys.stderr)
        return 2

    bonus = base * args.bonus_pct
    cash = base + bonus
    equity_annual = args.equity_grant / args.vest_years
    total = cash + equity_annual

    print("Offer — total target comp build (base + bonus + equity)")
    print(f"  base salary              : {base:,.0f}")
    print(f"  + target bonus           : {bonus:,.0f}  ({_pct(args.bonus_pct)} of base)")
    print(f"  = cash comp              : {cash:,.0f}")
    print(f"  + annualized equity      : {equity_annual:,.0f}  "
          f"({args.equity_grant:,.0f} grant / {args.vest_years:g} yr)")
    print(f"  = TOTAL TARGET COMP      : {total:,.0f}")
    print()
    if total > 0:
        print("  component mix:")
        print(f"    base   : {_pct(base / total)}")
        print(f"    bonus  : {_pct(bonus / total)}")
        print(f"    equity : {_pct(equity_annual / total)}")
    print("  reminder: present the band POSITION + market posture, not a bare")
    print("            number — an offer with no level/band logic behind it is a")
    print("            pay-equity risk (level-before-band, separate budgets).")
    print("  NOT legal advice: FLSA exempt/non-exempt classification and any")
    print("    pay-transparency posting duty are flagged for COUNSEL, never")
    print("    decided here.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="hr_calc.py",
        description="People-Ops / HR decision calculator (stdlib only). NOT legal "
        "advice — every FLSA / EEO / equal-pay / pay-transparency point is flagged "
        "for counsel, never opined on. A raw pay gap is a prompt to run the "
        "controlled review, not proof of anything.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    cb = sub.add_parser(
        "comp-band",
        help="range mechanics: spread + min/max-to-mid + optional compa-ratio",
    )
    cb.add_argument("--min", type=float, required=True, help="band minimum")
    cb.add_argument("--mid", type=float, required=True, help="band midpoint (market posture)")
    cb.add_argument("--max", type=float, required=True, help="band maximum")
    cb.add_argument("--salary", type=float, default=None,
                    help="optional salary to place in the band (compa-ratio)")
    cb.set_defaults(func=cmd_comp_band)

    pe = sub.add_parser(
        "pay-equity",
        help="UNADJUSTED group mean gap + raw ratio (a screen, NOT a verdict)",
    )
    pe.add_argument("--focal", type=float, action="append", default=[],
                    metavar="SALARY",
                    help="a focal-group salary (repeatable)")
    pe.add_argument("--reference", type=float, action="append", default=[],
                    metavar="SALARY",
                    help="a reference-group salary (repeatable)")
    pe.set_defaults(func=cmd_pay_equity)

    of = sub.add_parser(
        "offer",
        help="total target comp from base + target bonus + annualized equity",
    )
    of.add_argument("--base", type=float, required=True, help="annual base salary")
    of.add_argument("--bonus-pct", type=_parse_rate, default=0.0,
                    help="target bonus as a fraction or percent of base (e.g. 15%% or 0.15)")
    of.add_argument("--equity-grant", type=float, default=0.0,
                    help="total equity grant value (0 if none)")
    of.add_argument("--vest-years", type=float, default=4.0,
                    help="vesting period in years to annualize the grant (default 4)")
    of.set_defaults(func=cmd_offer)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
