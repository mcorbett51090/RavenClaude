#!/usr/bin/env python3
"""bh_calc.py — a zero-dependency behavioral-health practice-operations calculator.

Removes arithmetic error from three recurring operations decisions a behavioral-
health practice manager / operations lead / billing lead runs constantly:

  no-show      The no-show / late-cancellation RATE and its revenue impact: the
               share of scheduled sessions lost, the lost-revenue dollars at an
               average rate per session, and — optionally — the dollars a
               waitlist-backfill recovers by re-filling a fraction of the lost
               slots. Pairs with operations-exist-to-protect-the-clinical-hour
               and the no-show scenario.

  caseload     A clinician's CAPACITY vs. their active panel: weekly capacity
               (clinical hours ÷ session length), the target panel at a chosen
               utilization, the gap vs. the current active panel, and the
               utilization the current panel implies. The capacity lens for
               panel balancing, not a clinical-appropriateness call.

  auth-tracking  Sessions AUTHORIZED vs. used: the remaining authorized sessions,
               the burn rate, and how many sessions (or weeks at a cadence) are
               left before a re-authorization is needed — so re-auth happens
               BEFORE the units run out, never after a denied claim.

This is a CALCULATOR, not a data source — it does not fetch payer policy, CPT
fees, or live schedules. The user supplies every input; the tool does the
arithmetic and shows the formula. Stdlib only (argparse); runs anywhere Python
3.8+ is present.

IMPORTANT: outputs are operational decision-support, NOT clinical, medical,
legal, or billing-final advice (see ../CLAUDE.md §1, §4). No PHI belongs in any
input or output — use counts and rates, never client identifiers (§4 #2).
Validate every figure against the practice's actual schedule, the current CPT
code set, and the specific payer's policy before any deliverable.

Examples
--------
  # No-show: 1,200 scheduled sessions/mo, 264 no-showed/late-cancelled,
  # $130 average collected per session, modeling a waitlist that backfills 35%
  python3 bh_calc.py no-show --scheduled 1200 --missed 264 \\
      --revenue-per-session 130 --backfill-rate 35%

  # Caseload: 25 clinical hours/wk, 50-min sessions, target 85% utilization,
  # current active panel of 30 clients seen weekly
  python3 bh_calc.py caseload --clinical-hours 25 --session-minutes 50 \\
      --utilization 85% --active-panel 30

  # Auth tracking: 20 sessions authorized, 14 used, weekly cadence,
  # re-auth lead time of 2 sessions
  python3 bh_calc.py auth-tracking --authorized 20 --used 14 \\
      --cadence-per-week 1 --reauth-lead 2
"""

from __future__ import annotations

import argparse
import sys


def _parse_rate(s: str) -> float:
    """Parse a rate like '35%' or '0.35' into a fraction (0.35)."""
    s = s.strip()
    try:
        return float(s[:-1]) / 100.0 if s.endswith("%") else float(s)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"must be like '35%' or '0.35', got {s!r}"
        ) from None


def cmd_no_show(args: argparse.Namespace) -> int:
    if args.scheduled <= 0:
        print("error: --scheduled must be > 0", file=sys.stderr)
        return 2
    if not 0 <= args.missed <= args.scheduled:
        print("error: --missed must be in [0, --scheduled]", file=sys.stderr)
        return 2
    if not 0.0 <= args.backfill_rate <= 1.0:
        print("error: --backfill-rate must be in [0%, 100%]", file=sys.stderr)
        return 2

    rate = args.missed / args.scheduled
    kept = args.scheduled - args.missed
    print("No-show / late-cancellation rate & revenue impact")
    print(f"  scheduled sessions        : {args.scheduled:,.0f}")
    print(f"  no-showed / late-cancelled: {args.missed:,.0f}")
    print(f"  → no-show rate            : {rate * 100:.1f}%  ({kept:,.0f} kept)")

    if args.revenue_per_session:
        lost = args.missed * args.revenue_per_session
        print()
        print(f"  at {args.revenue_per_session:,.2f} avg collected/session:")
        print(f"    lost revenue          : {lost:,.0f}")
        if args.backfill_rate > 0:
            recovered = lost * args.backfill_rate
            print(
                f"    waitlist backfill @ {args.backfill_rate * 100:g}% "
                f"→ recovers {recovered:,.0f}"
            )
            print(f"    net residual loss     : {lost - recovered:,.0f}")
    print("  note: a no-show program needs BOTH the nudge (reminders) and the")
    print("        consequence (a fair, acknowledged policy) — plus a waitlist so a")
    print("        freed slot isn't lost. Justify by clinician hours returned to")
    print("        care, not a utilization number alone (CLAUDE.md §4 #8).")
    return 0


def cmd_caseload(args: argparse.Namespace) -> int:
    if args.clinical_hours <= 0:
        print("error: --clinical-hours must be > 0", file=sys.stderr)
        return 2
    if args.session_minutes <= 0:
        print("error: --session-minutes must be > 0", file=sys.stderr)
        return 2
    if not 0.0 < args.utilization <= 1.0:
        print("error: --utilization must be in (0%, 100%]", file=sys.stderr)
        return 2

    sessions_per_hour = 60.0 / args.session_minutes
    weekly_capacity = args.clinical_hours * sessions_per_hour
    target_panel = weekly_capacity * args.utilization
    print("Clinician caseload — capacity vs. active panel (weekly)")
    print(f"  clinical hours / week     : {args.clinical_hours:g}")
    print(
        f"  session length            : {args.session_minutes:g} min "
        f"({sessions_per_hour:.2f} sessions/clinical hour)"
    )
    print(f"  → weekly session capacity : {weekly_capacity:,.1f} sessions")
    print(
        f"  target utilization        : {args.utilization * 100:g}% "
        f"→ target panel {target_panel:,.1f}"
    )

    if args.active_panel is not None:
        gap = target_panel - args.active_panel
        implied_util = (
            args.active_panel / weekly_capacity if weekly_capacity else 0.0
        )
        print()
        print(f"  current active panel      : {args.active_panel:,.0f}")
        print(f"    implied utilization     : {implied_util * 100:.1f}%")
        if gap > 0:
            print(
                f"    headroom                : +{gap:,.1f} sessions of "
                "capacity before target"
            )
        else:
            print(
                f"    OVER target by          : {-gap:,.1f} sessions — "
                "panel exceeds the chosen utilization"
            )
    print("  note: this is the CAPACITY lens for panel balancing, not a clinical-")
    print("        appropriateness call — whether a client fits a panel is the")
    print("        clinician's judgment (CLAUDE.md §1). Protect the clinical hour.")
    return 0


def cmd_auth_tracking(args: argparse.Namespace) -> int:
    if args.authorized <= 0:
        print("error: --authorized must be > 0", file=sys.stderr)
        return 2
    if args.used < 0:
        print("error: --used must be >= 0", file=sys.stderr)
        return 2
    if args.reauth_lead < 0:
        print("error: --reauth-lead must be >= 0", file=sys.stderr)
        return 2

    remaining = args.authorized - args.used
    used_pct = args.used / args.authorized
    print("Authorization tracking — authorized vs. used sessions")
    print(f"  authorized sessions       : {args.authorized:,.0f}")
    print(f"  used sessions             : {args.used:,.0f}  ({used_pct * 100:.0f}% burned)")
    if remaining < 0:
        print(
            f"  → OVER authorization by   : {-remaining:,.0f} sessions — "
            "billed beyond the approved units (denial risk)"
        )
        print("  ACTION: stop scheduling against this auth; reconcile and re-auth now.")
        return 0

    print(f"  → remaining authorized    : {remaining:,.0f}")
    sessions_before_reauth = max(remaining - args.reauth_lead, 0.0)
    print(
        f"  re-auth lead time         : {args.reauth_lead:g} sessions "
        "(start the re-auth this many sessions before the units run out)"
    )
    print(f"  → sessions before re-auth : {sessions_before_reauth:,.0f}")
    if args.cadence_per_week and args.cadence_per_week > 0:
        weeks = sessions_before_reauth / args.cadence_per_week
        print(
            f"    at {args.cadence_per_week:g} session(s)/week "
            f"→ ~{weeks:,.1f} weeks before re-auth is due"
        )
    print("  note: confirm the auth (number + unit count) in writing and re-auth")
    print("        BEFORE the units run out — an assumed/expired auth is a denied")
    print("        claim. Verify units + policy with the payer (CLAUDE.md §4 #4).")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="bh_calc.py",
        description=(
            "Behavioral-health practice-operations calculator (stdlib only). "
            "Operational decision-support, not clinical/legal/billing-final "
            "advice — no PHI in inputs; validate every figure."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    ns = sub.add_parser(
        "no-show", help="No-show / cancellation rate + revenue impact + backfill"
    )
    ns.add_argument(
        "--scheduled", type=float, required=True, help="scheduled sessions in the window"
    )
    ns.add_argument(
        "--missed",
        type=float,
        required=True,
        help="no-showed + late-cancelled sessions in the window",
    )
    ns.add_argument(
        "--revenue-per-session",
        type=float,
        default=0.0,
        help="average collected per session (optional, for revenue impact)",
    )
    ns.add_argument(
        "--backfill-rate",
        type=_parse_rate,
        default=0.0,
        help="share of lost slots a waitlist re-fills, e.g. 35%% (optional)",
    )
    ns.set_defaults(func=cmd_no_show)

    cl = sub.add_parser(
        "caseload", help="Clinician capacity vs. active panel + utilization"
    )
    cl.add_argument(
        "--clinical-hours",
        type=float,
        required=True,
        help="clinical (client-facing) hours per week",
    )
    cl.add_argument(
        "--session-minutes",
        type=float,
        required=True,
        help="typical session length in minutes (e.g. 50)",
    )
    cl.add_argument(
        "--utilization",
        type=_parse_rate,
        required=True,
        help="target utilization of capacity, e.g. 85%%",
    )
    cl.add_argument(
        "--active-panel",
        type=float,
        default=None,
        help="current active clients seen weekly (optional, for the gap)",
    )
    cl.set_defaults(func=cmd_caseload)

    at = sub.add_parser(
        "auth-tracking",
        help="Authorized vs. used sessions; remaining before re-auth",
    )
    at.add_argument(
        "--authorized", type=float, required=True, help="sessions authorized"
    )
    at.add_argument("--used", type=float, required=True, help="sessions used to date")
    at.add_argument(
        "--cadence-per-week",
        type=float,
        default=0.0,
        help="sessions per week (optional, to convert remaining to weeks)",
    )
    at.add_argument(
        "--reauth-lead",
        type=float,
        default=0.0,
        help="sessions of lead time to start the re-auth before units run out",
    )
    at.set_defaults(func=cmd_auth_tracking)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
