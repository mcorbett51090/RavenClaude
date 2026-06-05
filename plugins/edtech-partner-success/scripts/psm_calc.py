#!/usr/bin/env python3
"""psm_calc.py - a zero-dependency EdTech Partner-Success decision calculator.

Removes arithmetic error from three recurring PSM decisions a Partner Success
Manager runs constantly across a book of EdTech partners:

  utilization       Seat / license ACTIVATION read. Given provisioned seats and
                    the count with >=N meaningful sessions in the window, prints
                    the activation rate, the dead-seat count, and (optionally) the
                    annualized waste-dollar estimate. Anchors the "which side of
                    the 57/43 line is this partner on?" question MONTHS before
                    renewal. Pairs with knowledge/k12-spend-utilization-43pct.md
                    and the adoption-intervention decision tree.

  renewal-forecast  Book-level renewal/NRR projection. Given per-band partner
                    counts + ARR and per-band assumed gross-retention and
                    expansion rates, prints projected GRR, NRR, and the expected
                    renewed + expanded ARR, with the segment benchmark band for
                    context. Pairs with knowledge/psm-metrics-glossary.md and the
                    renewal-risk decision tree. A FORECAST, not a forecast engine -
                    the user supplies every band assumption.

  ttv               Time-to-first-value check against a calendar dead zone. Given
                    a go-live / first-value target date and a dead-zone window,
                    flags whether the projected first-value date lands inside a
                    suppression window (where a launch reaches no one) and prints
                    the days-to-value. Pairs with the implementation-90-day arc and
                    knowledge/k12-adoption-arc-fall-spring-summer.md.

This is a CALCULATOR, not a data source - it does not fetch benchmarks, usage
telemetry, or contract values. The user supplies every input; the tool does the
arithmetic and shows the formula. Stdlib only (argparse, datetime); runs anywhere
Python 3.8+ is present.

IMPORTANT: outputs are decision-support, not contractual, legal, or financial
advice (see ../CLAUDE.md section 2). FERPA: this tool takes only aggregate,
partner-level counts - never student-level rows or PII. Validate every figure
against the partner's actual data before any deliverable (CLAUDE.md section 3
cite-or-mark rule).

Examples
--------
  # Utilization: 4,000 provisioned seats, 2,150 active in last 90 days,
  # ~$48k annual contract -> activation rate + dead seats + waste estimate
  python3 psm_calc.py utilization --provisioned 4000 --active 2150 \\
      --annual-contract 48000

  # Renewal forecast across a 3-band book (green/yellow/red), each band's
  # partner count, ARR, assumed gross retention and expansion
  python3 psm_calc.py renewal-forecast \\
      --band green:12:600000:0.98:0.12 \\
      --band yellow:7:280000:0.90:0.03 \\
      --band red:3:90000:0.55:0.00 \\
      --segment mid-market

  # Time-to-value: go-live targeted 2026-09-08, first value ~14 days later,
  # district testing dead zone 2026-09-15..2026-09-26
  python3 psm_calc.py ttv --go-live 2026-09-08 --value-lag-days 14 \\
      --dead-zone 2026-09-15:2026-09-26
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, datetime, timedelta

# Public segment benchmark bands (NRR / GRR), retrieved 2026-06-05. These are
# context labels printed alongside the user's computed numbers - NEVER a
# substitute for the partner's own data. [verify-at-use]
#   NRR: enterprise ~118%, mid-market ~108%, SMB ~97% (SaaS Capital 2025);
#        all-B2B median ~106% (Wudpecker 2026).
#   GRR: enterprise ~92-95%, mid-market ~88-92%, all-SaaS median ~90%
#        (SaaS Capital 2025).
_SEGMENT_NRR = {"enterprise": 118.0, "mid-market": 108.0, "smb": 97.0}
_SEGMENT_GRR = {"enterprise": 93.5, "mid-market": 90.0, "smb": 88.0}


def _parse_rate(s: str) -> float:
    """Parse a rate like '57%' or '0.57' into a fraction (0.57)."""
    s = s.strip()
    try:
        return float(s[:-1]) / 100.0 if s.endswith("%") else float(s)
    except ValueError:
        raise argparse.ArgumentTypeError(f"must be like '57%' or '0.57', got {s!r}")


def _parse_date(s: str) -> date:
    try:
        return datetime.strptime(s.strip(), "%Y-%m-%d").date()
    except ValueError:
        raise argparse.ArgumentTypeError(f"must be YYYY-MM-DD, got {s!r}")


def cmd_utilization(args: argparse.Namespace) -> int:
    if args.provisioned <= 0:
        print("error: --provisioned must be > 0", file=sys.stderr)
        return 2
    if not 0 <= args.active <= args.provisioned:
        print("error: --active must be in [0, provisioned]", file=sys.stderr)
        return 2

    rate = args.active / args.provisioned
    dead = args.provisioned - args.active
    dead_frac = dead / args.provisioned

    print("Seat / license utilization read")
    print(f"  provisioned seats        : {args.provisioned:,}")
    print(f"  active (>=N sessions/win) : {args.active:,}")
    print(f"  -> activation rate       : {rate * 100:.1f}%")
    print(f"  -> dead (inactive) seats : {dead:,}  ({dead_frac * 100:.1f}%)")

    # Public anchor: K-12 districts actively use ~57% of tools, wasting ~43%.
    if rate < 0.57:
        print("  context: BELOW the ~57% K-12 active-use benchmark - this partner")
        print("           is trending toward the unused-43% pool. [verify-at-use]")
    else:
        print("  context: at/above the ~57% K-12 active-use benchmark. [verify-at-use]")

    if args.annual_contract is not None:
        if args.annual_contract < 0:
            print("error: --annual-contract must be >= 0", file=sys.stderr)
            return 2
        waste = args.annual_contract * dead_frac
        print(f"  annual contract value    : {args.annual_contract:,.0f}")
        print(f"  -> waste-proxy (dead-frac x contract): {waste:,.0f}/yr")
        print("    note: a PROXY (dead seats x contract), not a refund figure -")
        print("    public mid-district loss runs ~$200K-$400K/yr. [verify-at-use]")
    print("  reminder: utilization is the LEADING renewal-risk indicator - pull it")
    print("            months before renewal, not at the CFO keep/cut review.")
    return 0


def _parse_band(s: str) -> tuple:
    """Parse 'name:count:arr:grr:expansion' into a tuple."""
    parts = s.split(":")
    if len(parts) != 5:
        raise argparse.ArgumentTypeError(
            f"--band must be name:count:arr:grr:expansion, got {s!r}"
        )
    name, count, arr, grr, exp = parts
    try:
        return (name, int(count), float(arr), _parse_rate(grr), _parse_rate(exp))
    except (ValueError, argparse.ArgumentTypeError) as e:
        raise argparse.ArgumentTypeError(f"bad --band {s!r}: {e}")


def cmd_renewal_forecast(args: argparse.Namespace) -> int:
    total_arr = 0.0
    retained_arr = 0.0
    expanded_arr = 0.0
    total_partners = 0

    print("Book-level renewal / NRR forecast")
    print("  band   | partners | starting ARR | GRR  | expansion |   renewed ARR")
    print("  -------+----------+--------------+------+-----------+--------------")
    for name, count, arr, grr, exp in args.band:
        if count < 0 or arr < 0:
            print(f"error: band {name!r} count/arr must be >= 0", file=sys.stderr)
            return 2
        renewed = arr * grr
        expanded = renewed * exp
        total_arr += arr
        retained_arr += renewed
        expanded_arr += expanded
        total_partners += count
        print(
            f"  {name:<6} | {count:>8,} | {arr:>12,.0f} | {grr * 100:>3.0f}% | "
            f"{exp * 100:>8.0f}% | {renewed + expanded:>12,.0f}"
        )

    if total_arr <= 0:
        print("error: total starting ARR must be > 0", file=sys.stderr)
        return 2

    grr_book = retained_arr / total_arr
    nrr_book = (retained_arr + expanded_arr) / total_arr
    print()
    print(f"  total partners           : {total_partners:,}")
    print(f"  total starting ARR       : {total_arr:,.0f}")
    print(f"  -> projected GRR         : {grr_book * 100:.1f}%")
    print(f"  -> projected NRR         : {nrr_book * 100:.1f}%")
    print(f"  -> projected renewed+expanded ARR: {retained_arr + expanded_arr:,.0f}")

    seg = args.segment
    if seg in _SEGMENT_NRR:
        print(
            f"  benchmark ({seg}): NRR ~{_SEGMENT_NRR[seg]:.0f}%, "
            f"GRR ~{_SEGMENT_GRR[seg]:.0f}% (SaaS Capital 2025) [verify-at-use]"
        )
        if nrr_book * 100 < _SEGMENT_NRR[seg]:
            print(f"    -> projected NRR is BELOW the {seg} benchmark.")
    print("  note: every band assumption is YOURS - calibrate GRR/expansion from")
    print("        the partners' actual history, not the defaults (CLAUDE.md s3 #12).")
    return 0


def _parse_window(s: str) -> tuple:
    parts = s.split(":")
    if len(parts) != 2:
        raise argparse.ArgumentTypeError(
            f"--dead-zone must be START:END (YYYY-MM-DD:YYYY-MM-DD), got {s!r}"
        )
    start, end = _parse_date(parts[0]), _parse_date(parts[1])
    if end < start:
        raise argparse.ArgumentTypeError(f"--dead-zone end before start: {s!r}")
    return (start, end)


def cmd_ttv(args: argparse.Namespace) -> int:
    if args.value_lag_days < 0:
        print("error: --value-lag-days must be >= 0", file=sys.stderr)
        return 2
    first_value = args.go_live + timedelta(days=args.value_lag_days)

    print("Time-to-first-value vs. calendar dead zone")
    print(f"  go-live date             : {args.go_live.isoformat()}")
    print(f"  value lag                : {args.value_lag_days} days")
    print(f"  -> projected first-value : {first_value.isoformat()}")

    hit = None
    for start, end in args.dead_zone:
        if start <= first_value <= end:
            hit = (start, end)
            break
        if start <= args.go_live <= end:
            hit = (start, end)
            break

    if hit:
        print(f"  -> WARNING: go-live or first-value lands in dead zone "
              f"{hit[0].isoformat()}..{hit[1].isoformat()}")
        print("     a launch here reaches no one - re-anchor to a live week first.")
        print("     (calendar-dead-zone check is the highest-leverage pre-flight.)")
    else:
        print("  -> clear: neither go-live nor first-value lands in a dead zone.")

    # B2B best-in-class first value ~7 days (public SaaS benchmark) - K-12 runs on
    # the school calendar, so treat the clock as advisory, not a literal target.
    if args.value_lag_days > 7:
        print("  context: >7d exceeds the generic B2B best-in-class first-value")
        print("           window; K-12 is calendar-bound, so judge vs. the school")
        print("           calendar, not a literal 7-day clock. [verify-at-use]")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="psm_calc.py",
        description="EdTech Partner-Success decision calculator (stdlib only). "
        "Decision-support, not contractual/legal/financial advice - validate "
        "every input. FERPA: aggregate partner-level counts only, never PII.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    util = sub.add_parser("utilization", help="Seat/license activation read")
    util.add_argument("--provisioned", type=int, required=True,
                      help="provisioned seats / licenses")
    util.add_argument("--active", type=int, required=True,
                      help="seats with >=N meaningful sessions in the window")
    util.add_argument("--annual-contract", type=float, default=None,
                      help="annual contract value for a waste-proxy estimate (optional)")
    util.set_defaults(func=cmd_utilization)

    ren = sub.add_parser("renewal-forecast", help="Book-level GRR/NRR projection")
    ren.add_argument("--band", type=_parse_band, action="append", required=True,
                     metavar="NAME:COUNT:ARR:GRR:EXPANSION",
                     help="per-band: name, partner count, starting ARR, assumed "
                     "gross retention, assumed expansion (repeatable)")
    ren.add_argument("--segment", choices=sorted(_SEGMENT_NRR), default=None,
                     help="segment for a benchmark-band context line (optional)")
    ren.set_defaults(func=cmd_renewal_forecast)

    ttv = sub.add_parser("ttv", help="Time-to-first-value vs. dead-zone check")
    ttv.add_argument("--go-live", type=_parse_date, required=True,
                     help="go-live date (YYYY-MM-DD)")
    ttv.add_argument("--value-lag-days", type=int, default=0,
                     help="days from go-live to projected first meaningful value")
    ttv.add_argument("--dead-zone", type=_parse_window, action="append", default=[],
                     metavar="START:END",
                     help="a calendar dead-zone window YYYY-MM-DD:YYYY-MM-DD "
                     "(repeatable)")
    ttv.set_defaults(func=cmd_ttv)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
