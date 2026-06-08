#!/usr/bin/env python3
"""
bh_calc.py — Behavioral & Mental Health Practice Calculator
Stdlib-only. No third-party dependencies.

Modes:
  no-show-rate     Calculate the no-show rate and effective capacity impact.
  utilization      Provider utilization: billable ÷ available hours.
  units-per-session  Convert session minutes to authorized units (15-min units).
  capacity         Effective capacity: slots × providers × show-rate.
  auth-burn        Authorization burn: sessions used / authorized, weeks remaining.

Usage (all modes accept positional or --flag args):
  python3 bh_calc.py no-show-rate --total-scheduled 100 --no-shows 18
  python3 bh_calc.py utilization --billable-hours 28 --available-hours 40
  python3 bh_calc.py units-per-session --minutes 50
  python3 bh_calc.py capacity --slots-per-provider 30 --providers 5 --show-rate 0.80
  python3 bh_calc.py auth-burn --authorized 24 --used 18 --sessions-per-week 2

Not clinical advice. Outputs are decision-support tools for practice operations.
"""

import argparse
import sys


# ---------------------------------------------------------------------------
# Mode 1: No-show rate
# ---------------------------------------------------------------------------

def no_show_rate(total_scheduled: int, no_shows: int) -> dict:
    """
    Calculate no-show rate and the effective session gain from improving it.

    Args:
        total_scheduled: Total sessions scheduled in the period.
        no_shows: Sessions where the patient did not attend and did not cancel.

    Returns:
        dict with rate, effective sessions attended, and projected gain.
    """
    if total_scheduled <= 0:
        raise ValueError("total_scheduled must be > 0")
    if no_shows < 0 or no_shows > total_scheduled:
        raise ValueError("no_shows must be between 0 and total_scheduled")

    rate = no_shows / total_scheduled
    attended = total_scheduled - no_shows
    show_rate = 1.0 - rate

    # Projected gain if no-show rate improves by 5 percentage points
    improved_rate = max(0.0, rate - 0.05)
    improved_no_shows = round(total_scheduled * improved_rate)
    improved_attended = total_scheduled - improved_no_shows
    additional_sessions = improved_attended - attended

    return {
        "total_scheduled": total_scheduled,
        "no_shows": no_shows,
        "no_show_rate_pct": round(rate * 100, 1),
        "show_rate_pct": round(show_rate * 100, 1),
        "sessions_attended": attended,
        "projected_gain_if_5pt_improvement": additional_sessions,
        "improved_show_rate_pct": round((1.0 - improved_rate) * 100, 1),
    }


# ---------------------------------------------------------------------------
# Mode 2: Provider utilization
# ---------------------------------------------------------------------------

def utilization(billable_hours: float, available_hours: float) -> dict:
    """
    Calculate provider utilization (billable ÷ available hours).

    Sustainable outpatient therapy utilization is typically 65–75% of available
    clinical hours. Above ~80% creates burnout risk in behavioral health.

    Args:
        billable_hours: Direct clinical (billable) hours in the period.
        available_hours: Total hours available for clinical work in the period
                         (excluding admin, supervision, documentation time).

    Returns:
        dict with utilization rate and sustainability assessment.
    """
    if available_hours <= 0:
        raise ValueError("available_hours must be > 0")
    if billable_hours < 0:
        raise ValueError("billable_hours must be >= 0")

    rate = billable_hours / available_hours

    if rate < 0.60:
        assessment = "Under-utilized — capacity to grow caseload or reduce available hours"
    elif rate <= 0.75:
        assessment = "Sustainable — within the recommended 65–75% range for outpatient BH"
    elif rate <= 0.85:
        assessment = "High — monitor for burnout; consider admin support or caseload cap"
    else:
        assessment = "Unsustainable — burnout risk is high at this utilization level"

    return {
        "billable_hours": billable_hours,
        "available_hours": available_hours,
        "utilization_pct": round(rate * 100, 1),
        "non_billable_hours": round(available_hours - billable_hours, 1),
        "sustainability_assessment": assessment,
    }


# ---------------------------------------------------------------------------
# Mode 3: Units per session
# ---------------------------------------------------------------------------

def units_per_session(minutes: int) -> dict:
    """
    Convert session duration in minutes to 15-minute billing units, and
    identify the applicable CPT code range for individual psychotherapy.

    Args:
        minutes: Duration of the session in minutes.

    Returns:
        dict with unit count and CPT code framing.
    """
    if minutes <= 0:
        raise ValueError("minutes must be > 0")

    units = (minutes + 14) // 15  # Round up to nearest 15-min unit

    # CPT framing for individual psychotherapy (public CPT descriptions)
    if minutes < 16:
        cpt_framing = "Below 90832 minimum (16 min) — not a standard psychotherapy code"
    elif minutes <= 37:
        cpt_framing = "90832 — Individual psychotherapy, 16–37 minutes"
    elif minutes <= 52:
        cpt_framing = "90834 — Individual psychotherapy, 38–52 minutes"
    else:
        cpt_framing = "90837 — Individual psychotherapy, 53+ minutes"

    return {
        "session_minutes": minutes,
        "billing_units_15min": units,
        "cpt_framing": cpt_framing,
        "note": (
            "CPT code selection is the clinician/biller's determination. "
            "Documented time must match the billed code. "
            "This is public CPT framing, not a billing directive."
        ),
    }


# ---------------------------------------------------------------------------
# Mode 4: Capacity
# ---------------------------------------------------------------------------

def capacity(
    slots_per_provider: int,
    providers: int,
    show_rate: float,
) -> dict:
    """
    Calculate effective clinic capacity: slots × providers × show-rate.

    Args:
        slots_per_provider: Available appointment slots per provider per period
                            (e.g., per week).
        providers: Number of clinical providers.
        show_rate: Expected proportion of scheduled appointments kept (0–1.0).

    Returns:
        dict with raw and effective capacity, and sensitivity to show-rate changes.
    """
    if slots_per_provider <= 0:
        raise ValueError("slots_per_provider must be > 0")
    if providers <= 0:
        raise ValueError("providers must be > 0")
    if not (0.0 < show_rate <= 1.0):
        raise ValueError("show_rate must be between 0 (exclusive) and 1.0 (inclusive)")

    raw_capacity = slots_per_provider * providers
    effective_capacity = raw_capacity * show_rate

    # Sensitivity: what if show rate improves by 5 or 10 points?
    effective_5pt = raw_capacity * min(1.0, show_rate + 0.05)
    effective_10pt = raw_capacity * min(1.0, show_rate + 0.10)

    return {
        "slots_per_provider": slots_per_provider,
        "providers": providers,
        "show_rate_pct": round(show_rate * 100, 1),
        "raw_capacity_slots": raw_capacity,
        "effective_capacity_sessions": round(effective_capacity, 1),
        "effective_if_show_rate_plus_5pt": round(effective_5pt, 1),
        "effective_if_show_rate_plus_10pt": round(effective_10pt, 1),
        "capacity_gap_5pt_improvement": round(effective_5pt - effective_capacity, 1),
    }


# ---------------------------------------------------------------------------
# Mode 5: Authorization burn
# ---------------------------------------------------------------------------

def auth_burn(authorized: int, used: int, sessions_per_week: float) -> dict:
    """
    Calculate authorization burn rate, sessions remaining, and weeks of coverage.

    Args:
        authorized: Total sessions authorized.
        used: Sessions already used against this authorization.
        sessions_per_week: Average sessions per week for this patient.

    Returns:
        dict with sessions remaining, weeks remaining, and renewal trigger alert.
    """
    if authorized <= 0:
        raise ValueError("authorized must be > 0")
    if used < 0 or used > authorized:
        raise ValueError("used must be between 0 and authorized")
    if sessions_per_week <= 0:
        raise ValueError("sessions_per_week must be > 0")

    remaining = authorized - used
    weeks_remaining = remaining / sessions_per_week
    utilization_pct = (used / authorized) * 100

    # Renewal trigger: flag when <= 20% remaining or <= 3 sessions remaining
    trigger_threshold = max(3, round(authorized * 0.20))
    renewal_needed = remaining <= trigger_threshold

    if remaining == 0:
        status = "EXHAUSTED — do not schedule sessions without a new authorization"
    elif renewal_needed:
        status = f"RENEWAL NEEDED NOW — {remaining} sessions remain (at or below trigger threshold of {trigger_threshold})"
    else:
        status = f"Active — {remaining} sessions remaining (~{weeks_remaining:.1f} weeks at current rate)"

    return {
        "authorized_sessions": authorized,
        "sessions_used": used,
        "sessions_remaining": remaining,
        "utilization_pct": round(utilization_pct, 1),
        "weeks_of_coverage_remaining": round(weeks_remaining, 1),
        "renewal_trigger_threshold": trigger_threshold,
        "renewal_action_needed": renewal_needed,
        "status": status,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _print_result(result: dict) -> None:
    for k, v in result.items():
        print(f"  {k}: {v}")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Behavioral & Mental Health Practice Calculator (stdlib only)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="mode", required=True)

    # no-show-rate
    p_nsr = subparsers.add_parser("no-show-rate", help="Calculate no-show rate and capacity impact")
    p_nsr.add_argument("--total-scheduled", type=int, required=True)
    p_nsr.add_argument("--no-shows", type=int, required=True)

    # utilization
    p_util = subparsers.add_parser("utilization", help="Provider utilization (billable / available hours)")
    p_util.add_argument("--billable-hours", type=float, required=True)
    p_util.add_argument("--available-hours", type=float, required=True)

    # units-per-session
    p_units = subparsers.add_parser("units-per-session", help="Session minutes to 15-min units + CPT framing")
    p_units.add_argument("--minutes", type=int, required=True)

    # capacity
    p_cap = subparsers.add_parser("capacity", help="Effective capacity: slots × providers × show-rate")
    p_cap.add_argument("--slots-per-provider", type=int, required=True)
    p_cap.add_argument("--providers", type=int, required=True)
    p_cap.add_argument("--show-rate", type=float, required=True,
                       help="Show rate as a decimal, e.g. 0.80 for 80%%")

    # auth-burn
    p_auth = subparsers.add_parser("auth-burn", help="Authorization burn: sessions remaining and weeks of coverage")
    p_auth.add_argument("--authorized", type=int, required=True)
    p_auth.add_argument("--used", type=int, required=True)
    p_auth.add_argument("--sessions-per-week", type=float, required=True)

    args = parser.parse_args(argv)

    try:
        if args.mode == "no-show-rate":
            result = no_show_rate(args.total_scheduled, args.no_shows)
        elif args.mode == "utilization":
            result = utilization(args.billable_hours, args.available_hours)
        elif args.mode == "units-per-session":
            result = units_per_session(args.minutes)
        elif args.mode == "capacity":
            result = capacity(args.slots_per_provider, args.providers, args.show_rate)
        elif args.mode == "auth-burn":
            result = auth_burn(args.authorized, args.used, args.sessions_per_week)
        else:
            parser.error(f"Unknown mode: {args.mode}")
            return 1

        print(f"\n[bh_calc: {args.mode}]")
        _print_result(result)
        return 0

    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


# ---------------------------------------------------------------------------
# Self-test (__main__)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # CLI mode
        sys.exit(main())

    # Self-test mode — run when called as: python3 bh_calc.py
    print("=== bh_calc.py self-test ===\n")

    errors = []

    # --- no_show_rate ---
    print("[1] no_show_rate(total_scheduled=100, no_shows=18)")
    r = no_show_rate(100, 18)
    _print_result(r)
    assert r["no_show_rate_pct"] == 18.0, f"Expected 18.0, got {r['no_show_rate_pct']}"
    assert r["show_rate_pct"] == 82.0
    assert r["sessions_attended"] == 82
    assert r["projected_gain_if_5pt_improvement"] == 5
    print("  PASS\n")

    print("[2] no_show_rate(total_scheduled=40, no_shows=0)")
    r2 = no_show_rate(40, 0)
    _print_result(r2)
    assert r2["no_show_rate_pct"] == 0.0
    assert r2["sessions_attended"] == 40
    print("  PASS\n")

    # --- utilization ---
    print("[3] utilization(billable_hours=28, available_hours=40)")
    r3 = utilization(28, 40)
    _print_result(r3)
    assert r3["utilization_pct"] == 70.0
    assert "Sustainable" in r3["sustainability_assessment"]
    print("  PASS\n")

    print("[4] utilization(billable_hours=36, available_hours=40)")
    r4 = utilization(36, 40)
    _print_result(r4)
    assert r4["utilization_pct"] == 90.0
    assert "Unsustainable" in r4["sustainability_assessment"]
    print("  PASS\n")

    # --- units_per_session ---
    print("[5] units_per_session(minutes=50)")
    r5 = units_per_session(50)
    _print_result(r5)
    assert r5["billing_units_15min"] == 4  # ceil(50/15) = ceil(3.33) = 4
    assert "90834" in r5["cpt_framing"]
    print("  PASS\n")

    print("[6] units_per_session(minutes=53)")
    r6 = units_per_session(53)
    _print_result(r6)
    assert r6["billing_units_15min"] == 4  # ceil(53/15) = ceil(3.53) = 4
    assert "90837" in r6["cpt_framing"]
    print("  PASS\n")

    print("[7] units_per_session(minutes=30)")
    r7 = units_per_session(30)
    _print_result(r7)
    assert r7["billing_units_15min"] == 2
    assert "90832" in r7["cpt_framing"]
    print("  PASS\n")

    # --- capacity ---
    print("[8] capacity(slots_per_provider=30, providers=5, show_rate=0.80)")
    r8 = capacity(30, 5, 0.80)
    _print_result(r8)
    assert r8["raw_capacity_slots"] == 150
    assert r8["effective_capacity_sessions"] == 120.0
    assert r8["effective_if_show_rate_plus_5pt"] == 127.5
    assert r8["capacity_gap_5pt_improvement"] == 7.5
    print("  PASS\n")

    # --- auth_burn ---
    print("[9] auth_burn(authorized=24, used=18, sessions_per_week=2)")
    r9 = auth_burn(24, 18, 2)
    _print_result(r9)
    # trigger_threshold = max(3, round(24*0.20)) = max(3, round(4.8)) = max(3,5) = 5
    # remaining=6 > 5 → renewal_action_needed = False
    assert r9["sessions_remaining"] == 6
    assert r9["weeks_of_coverage_remaining"] == 3.0
    assert r9["renewal_trigger_threshold"] == 5
    assert r9["renewal_action_needed"] is False, (
        f"Expected False (6 > 5 trigger threshold), got {r9['renewal_action_needed']}"
    )
    print("  PASS\n")

    print("[10] auth_burn(authorized=24, used=20, sessions_per_week=2)")
    r10 = auth_burn(24, 20, 2)
    _print_result(r10)
    # remaining=4, trigger_threshold=5, 4 <= 5 → renewal_action_needed = True
    assert r10["sessions_remaining"] == 4
    assert r10["renewal_action_needed"] is True
    print("  PASS\n")

    print("[11] auth_burn(authorized=10, used=10, sessions_per_week=1)")
    r11 = auth_burn(10, 10, 1)
    _print_result(r11)
    assert r11["sessions_remaining"] == 0
    assert "EXHAUSTED" in r11["status"]
    print("  PASS\n")

    if errors:
        print(f"\n{len(errors)} FAILURES:")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)
    else:
        print("=== All self-tests passed ===")
        sys.exit(0)
