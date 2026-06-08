#!/usr/bin/env python3
"""clm_calc.py — a zero-dependency contract-lifecycle (CLM) date/SLA calculator.

Removes arithmetic error from three recurring legal-ops / CLM date checks. The
math is boring and easy to get wrong by a day — and a day is the difference
between giving notice inside the window and being locked into another term:

  renewal-window   From an EFFECTIVE date + a term + a notice-period, computes
                   the expiry date, the notice DEADLINE (the actionable date —
                   the last day to give non-renewal notice), and the tiered
                   auto-renew alert dates (90/60/30 days before that deadline,
                   tiers configurable). Flags whether today is already past the
                   deadline. Pairs with best-practices/track-the-notice-window-
                   not-just-expiry.md and the renew/renegotiate/exit tree.

  cycle-time       From an INTAKE date to a SIGNED date, the contract cycle time
                   in BUSINESS days (weekends excluded, optional --holidays), and
                   a PASS/BREACH flag against a per-class SLA. Pairs with best-
                   practices/cycle-time-is-measured-in-business-days.md.

  obligation-aging Buckets a set of obligation due-dates into days-to-due aging
                   buckets (overdue / 0-30 / 31-60 / 61-90 / 90+) relative to a
                   reference date, so what's coming due is visible at a glance.
                   Pairs with best-practices/signature-is-the-start-not-the-end.md
                   and the obligation-extraction tree.

This is a CALCULATOR, not a data source — it does not read a CLM, fetch a
contract, or know your real dates. The user supplies every input; the tool does
the date arithmetic and shows the formula. Stdlib only (argparse + datetime);
runs anywhere Python 3.8+ is present.

IMPORTANT: outputs are operational decision-support, NOT legal advice (see
../CLAUDE.md SS4 #1). A renewal-window deadline is an arithmetic projection from
the dates you supply — the binding notice terms (how notice must be given, what
counts as "before expiry", time zones, cure periods) are a legal-judgement call
a qualified lawyer owns. Validate every date against the executed contract and a
lawyer's read before acting (CLAUDE.md SS4 #1, SS4 #9, SS4 #12).

Examples
--------
  # Renewal window: 1-year term from 2025-07-01, 60-day notice window,
  # default 90/60/30 alert tiers, "today" = 2026-06-08
  python3 clm_calc.py renewal-window --effective 2025-07-01 --term-months 12 \\
      --notice-days 60 --today 2026-06-08

  # Cycle time: intake 2026-05-01 -> signed 2026-05-20, 10-business-day SLA,
  # excluding a holiday
  python3 clm_calc.py cycle-time --intake 2026-05-01 --signed 2026-05-20 \\
      --sla-days 10 --holidays 2026-05-11

  # Obligation aging: three due dates bucketed relative to 2026-06-08
  python3 clm_calc.py obligation-aging --as-of 2026-06-08 \\
      --due 2026-06-01 --due 2026-06-20 --due 2026-09-15
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, datetime, timedelta


def _parse_date(s: str) -> date:
    """Parse an ISO date (YYYY-MM-DD)."""
    try:
        return datetime.strptime(s.strip(), "%Y-%m-%d").date()
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"must be an ISO date YYYY-MM-DD, got {s!r}"
        ) from None


def _add_months(d: date, months: int) -> date:
    """Add a whole number of months to a date, clamping the day to month end."""
    total = (d.year * 12 + (d.month - 1)) + months
    year, month = divmod(total, 12)
    month += 1
    # Clamp day to the last valid day of the target month (e.g. Jan 31 + 1mo).
    next_month_first = date(year + (month // 12), (month % 12) + 1, 1)
    last_day = (next_month_first - timedelta(days=1)).day
    return date(year, month, min(d.day, last_day))


def _business_days_between(start: date, end: date, holidays: set[date]) -> int:
    """Inclusive business-day count from start to end (Mon-Fri minus holidays).

    Counts both endpoints when they are business days, matching how a legal-ops
    cycle-time clock reads "intake day 1 .. signed day N".
    """
    if end < start:
        start, end = end, start
    count = 0
    cur = start
    while cur <= end:
        if cur.weekday() < 5 and cur not in holidays:
            count += 1
        cur += timedelta(days=1)
    return count


def cmd_renewal_window(args: argparse.Namespace) -> int:
    if args.term_months <= 0:
        print("error: --term-months must be > 0", file=sys.stderr)
        return 2
    if args.notice_days < 0:
        print("error: --notice-days must be >= 0", file=sys.stderr)
        return 2

    tiers = sorted({t for t in args.alert_tiers if t >= 0}, reverse=True)
    today = args.today or date.today()

    expiry = _add_months(args.effective, args.term_months)
    notice_deadline = expiry - timedelta(days=args.notice_days)
    days_to_deadline = (notice_deadline - today).days

    print("Renewal notice window + tiered auto-renew alerts")
    print(f"  effective date          : {args.effective.isoformat()}")
    print(f"  term                    : {args.term_months} months")
    print(f"  expiry date             : {expiry.isoformat()}  (effective + term)")
    print(f"  notice period           : {args.notice_days} days before expiry")
    print(f"  -> NOTICE DEADLINE      : {notice_deadline.isoformat()}  (expiry - notice)")
    print("     (last day to give non-renewal notice)")
    print(f"  today                   : {today.isoformat()}")
    print("  ----")
    if days_to_deadline < 0:
        print(f"  -> WINDOW CLOSED        : deadline was {-days_to_deadline} day(s) ago")
        print("     if this auto-renews, you may already be committed to another term")
    elif days_to_deadline == 0:
        print("  -> ACT TODAY            : the notice deadline is today")
    else:
        print(f"  -> days to deadline     : {days_to_deadline} day(s) remaining")
    print("  ----")
    print("  alert dates (give the renew/renegotiate/exit decision room):")
    for t in tiers:
        alert = notice_deadline - timedelta(days=t)
        marker = "" if alert >= today else "  (past)"
        print(f"    T-{t:<3d} : {alert.isoformat()}{marker}")
    print()
    print("  read: the NOTICE DEADLINE is the actionable date, not the expiry - an")
    print("        auto-renew fires unless notice lands inside the window. Assign a")
    print("        named owner and tier the alerts. The BINDING notice terms (how /")
    print("        what counts as 'before expiry' / time zone) are a lawyer's call,")
    print("        not this arithmetic (CLAUDE.md SS4 #9, SS4 #1). Not legal advice.")
    return 0


def cmd_cycle_time(args: argparse.Namespace) -> int:
    if args.signed < args.intake:
        print("error: --signed must be on or after --intake", file=sys.stderr)
        return 2

    holidays = set(args.holidays or [])
    business_days = _business_days_between(args.intake, args.signed, holidays)
    calendar_days = (args.signed - args.intake).days

    print("Contract cycle time (business days) + SLA check")
    print(f"  intake date             : {args.intake.isoformat()}")
    print(f"  signed date             : {args.signed.isoformat()}")
    if args.contract_class:
        print(f"  contract class          : {args.contract_class}")
    print(f"  calendar days           : {calendar_days} (raw, for reference)")
    if holidays:
        print(f"  holidays excluded       : {len(holidays)}")
    print(f"  -> CYCLE TIME           : {business_days} business day(s)")
    print("     (Mon-Fri, inclusive of intake & signed days, minus holidays)")
    print("  ----")
    if args.sla_days is not None:
        if args.sla_days <= 0:
            print("error: --sla-days must be > 0", file=sys.stderr)
            return 2
        breach = business_days > args.sla_days
        verdict = "BREACH" if breach else "WITHIN SLA"
        over = business_days - args.sla_days
        print(f"  SLA (per class)         : {args.sla_days} business day(s)")
        print(f"  -> {verdict:<14s}     : {'+' + str(over) + ' over' if breach else str(-over) + ' to spare'}")
    print()
    print("  read: measure cycle time in BUSINESS days per request class - a standard")
    print("        NDA and a negotiated MSA have different clocks. A breach is a signal")
    print("        to add capacity, simplify the playbook, or widen self-serve, not just")
    print("        a redder cell (best-practices/cycle-time-is-measured-in-business-days).")
    print("        Faster never means looser - pair with a risk signal. Not legal advice.")
    return 0


def cmd_obligation_aging(args: argparse.Namespace) -> int:
    as_of = args.as_of or date.today()
    # Bucket edges in days-to-due; obligations are bucketed by (due - as_of).
    buckets = {
        "overdue (< 0)": [],
        "due 0-30": [],
        "due 31-60": [],
        "due 61-90": [],
        "due 90+": [],
    }
    for due in args.due:
        delta = (due - as_of).days
        if delta < 0:
            buckets["overdue (< 0)"].append((due, delta))
        elif delta <= 30:
            buckets["due 0-30"].append((due, delta))
        elif delta <= 60:
            buckets["due 31-60"].append((due, delta))
        elif delta <= 90:
            buckets["due 61-90"].append((due, delta))
        else:
            buckets["due 90+"].append((due, delta))

    print("Obligation aging — days-to-due buckets")
    print(f"  as-of date              : {as_of.isoformat()}")
    print(f"  obligations tracked     : {len(args.due)}")
    print("  ----")
    for label, items in buckets.items():
        print(f"  {label:<16s} : {len(items)}")
        for due, delta in sorted(items, key=lambda x: x[1]):
            when = f"{delta} day(s)" if delta >= 0 else f"{-delta} day(s) OVERDUE"
            print(f"      {due.isoformat()}  ({when})")
    print()
    overdue = len(buckets["overdue (< 0)"])
    soon = len(buckets["due 0-30"])
    if overdue:
        print(f"  -> {overdue} obligation(s) OVERDUE — these have no future alert tier left;")
        print("     route to the named owner now (signature is the start, not the end).")
    if soon:
        print(f"  -> {soon} obligation(s) due within 30 days — confirm owner + readiness.")
    print()
    print("  read: every obligation needs a named owner and a trigger, or it leaks")
    print("        (best-practices/signature-is-the-start-not-the-end). A genuinely")
    print("        ambiguous due date is flagged for the lawyer, never guessed")
    print("        (ambiguity-is-a-flag-not-a-guess). Not legal advice.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="clm_calc.py",
        description="Contract-lifecycle date/SLA calculator (stdlib only). "
        "Operational decision-support, NOT legal advice.",
    )
    sub = p.add_subparsers(dest="command", required=True)

    rw = sub.add_parser(
        "renewal-window",
        help="notice deadline + auto-renew alert dates from effective + term + notice",
    )
    rw.add_argument("--effective", type=_parse_date, required=True, help="effective date YYYY-MM-DD")
    rw.add_argument("--term-months", type=int, required=True, help="term length in months")
    rw.add_argument("--notice-days", type=int, required=True, help="notice window in days before expiry")
    rw.add_argument("--today", type=_parse_date, default=None, help="reference date (default: system today)")
    rw.add_argument(
        "--alert-tiers",
        type=int,
        nargs="+",
        default=[90, 60, 30],
        metavar="DAYS",
        help="alert tiers in days before the notice deadline (default: 90 60 30)",
    )
    rw.set_defaults(func=cmd_renewal_window)

    ct = sub.add_parser(
        "cycle-time",
        help="intake->signed business-day duration + SLA breach flag",
    )
    ct.add_argument("--intake", type=_parse_date, required=True, help="intake date YYYY-MM-DD")
    ct.add_argument("--signed", type=_parse_date, required=True, help="signed date YYYY-MM-DD")
    ct.add_argument("--sla-days", type=int, default=None, help="per-class SLA in business days (optional)")
    ct.add_argument("--contract-class", type=str, default=None, help="request class label (optional)")
    ct.add_argument(
        "--holidays",
        type=_parse_date,
        nargs="+",
        default=None,
        metavar="DATE",
        help="non-business holiday dates to exclude (optional)",
    )
    ct.set_defaults(func=cmd_cycle_time)

    oa = sub.add_parser(
        "obligation-aging",
        help="bucket obligation due-dates into days-to-due aging buckets",
    )
    oa.add_argument("--as-of", type=_parse_date, default=None, help="reference date (default: system today)")
    oa.add_argument(
        "--due",
        type=_parse_date,
        action="append",
        required=True,
        metavar="DATE",
        help="an obligation due-date YYYY-MM-DD (repeatable)",
    )
    oa.set_defaults(func=cmd_obligation_aging)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
