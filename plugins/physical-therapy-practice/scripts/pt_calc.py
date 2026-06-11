#!/usr/bin/env python3
"""
pt_calc.py — Physical Therapy practice calculator (stdlib only).

Nine functions covering the core PT decision metrics:
  - eight_minute_rule_units  : timed minutes → billable units (Medicare 8-minute rule)
  - units_per_visit          : average billable units per delivered visit
  - visit_utilization        : delivered visits ÷ available slots
  - cancellation_rate        : (cancellations + no-shows) ÷ scheduled
  - plan_of_care_adherence   : visits delivered ÷ visits prescribed (per episode)
  - referral_conversion_rate : evaluated (POC started) ÷ referrals received
  - clinic_contribution_margin: net collections − (direct labor + other direct cost)
  - outcome_change_vs_mcid   : functional-outcome change vs. the MCID threshold
  - net_collection_per_visit : collected ÷ delivered visits

All functions are pure (no I/O) and return a dict with the result plus the input
assumptions so callers can audit the calculation.

DISCLAIMER: outputs are decision-support only, not coding, billing, clinical, or
compliance advice. The Medicare 8-minute-rule thresholds are encoded for
orientation; verify against CURRENT CMS/payer policy and a certified coder. Some
commercial payers use the rule-of-eights / AMA variant. The caller supplies every
input; this script does not source data.
"""

from __future__ import annotations


def eight_minute_rule_units(total_timed_minutes: float) -> dict:
    """
    Convert total timed treatment minutes to billable units under the Medicare
    8-minute rule: 8-22→1, 23-37→2, 38-52→3, 53-67→4, then +1 per additional 15.

    NOTE: orientation only — verify against current CMS/payer policy. Untimed
    (service-based) codes are billed 1 unit per service and are NOT handled here.
    """
    m = float(total_timed_minutes)
    if m < 8:
        units = 0
    else:
        # Each unit "owns" a 15-minute block; the rule grants the first unit at 8 min.
        units = int((m + 7) // 15)
        # Guard the canonical boundaries explicitly.
        thresholds = [(8, 1), (23, 2), (38, 3), (53, 4), (68, 5), (83, 6)]
        units = 0
        for lo, u in thresholds:
            if m >= lo:
                units = u
        if m >= 83:
            # Extend the +15/unit pattern beyond the table.
            units = 6 + int((m - 83) // 15)
    return {
        "total_timed_minutes": m,
        "billable_units": units,
        "rule": "Medicare 8-minute rule (verify current CMS/payer policy)",
    }


def units_per_visit(total_units: int, visits: int) -> dict:
    """Average billable units per delivered visit."""
    if visits <= 0:
        return {"units_per_visit": None, "note": "visits must be > 0"}
    return {
        "units_per_visit": round(total_units / visits, 2),
        "total_units": total_units,
        "visits": visits,
    }


def visit_utilization(delivered_visits: int, available_slots: int) -> dict:
    """Visit utilization = delivered visits ÷ available slots."""
    if available_slots <= 0:
        return {"utilization": None, "note": "available_slots must be > 0"}
    r = delivered_visits / available_slots
    return {
        "utilization": round(r, 4),
        "utilization_pct": round(r * 100, 2),
        "delivered_visits": delivered_visits,
        "available_slots": available_slots,
    }


def cancellation_rate(cancellations: int, no_shows: int, scheduled: int) -> dict:
    """Combined cancellation + no-show rate ÷ scheduled visits."""
    if scheduled <= 0:
        return {"cancellation_rate": None, "note": "scheduled must be > 0"}
    missed = cancellations + no_shows
    r = missed / scheduled
    return {
        "cancellation_rate": round(r, 4),
        "cancellation_pct": round(r * 100, 2),
        "missed": missed,
        "cancellations": cancellations,
        "no_shows": no_shows,
        "scheduled": scheduled,
    }


def plan_of_care_adherence(visits_delivered: int, visits_prescribed: int) -> dict:
    """Plan-of-care adherence = visits delivered ÷ visits prescribed (per episode)."""
    if visits_prescribed <= 0:
        return {"adherence": None, "note": "visits_prescribed must be > 0"}
    r = visits_delivered / visits_prescribed
    return {
        "adherence": round(r, 4),
        "adherence_pct": round(r * 100, 2),
        "dropout_pct": round((1 - r) * 100, 2),
        "visits_delivered": visits_delivered,
        "visits_prescribed": visits_prescribed,
    }


def referral_conversion_rate(evaluated: int, referrals_received: int) -> dict:
    """Referral → evaluation conversion = evaluated (POC started) ÷ referrals received."""
    if referrals_received <= 0:
        return {"referral_conversion": None, "note": "referrals_received must be > 0"}
    r = evaluated / referrals_received
    return {
        "referral_conversion": round(r, 4),
        "referral_conversion_pct": round(r * 100, 2),
        "lost_pct": round((1 - r) * 100, 2),
        "evaluated": evaluated,
        "referrals_received": referrals_received,
    }


def clinic_contribution_margin(
    net_collection_total: float,
    direct_labor_cost: float,
    other_direct_cost: float = 0.0,
) -> dict:
    """Clinic contribution margin = net collections − (direct labor + other direct cost)."""
    margin = net_collection_total - direct_labor_cost - other_direct_cost
    base = net_collection_total if net_collection_total > 0 else None
    return {
        "contribution_margin": round(margin, 2),
        "contribution_margin_pct": round(margin / base * 100, 2) if base else None,
        "net_collection_total": net_collection_total,
        "direct_labor_cost": direct_labor_cost,
        "other_direct_cost": other_direct_cost,
    }


def outcome_change_vs_mcid(
    baseline_score: float, latest_score: float, mcid: float, higher_is_better: bool = True
) -> dict:
    """
    Judge a functional-outcome change against the MCID (minimal clinically important
    difference). Returns the change and whether it meets the MCID threshold.
    """
    change = latest_score - baseline_score
    directional = change if higher_is_better else -change
    return {
        "change": round(change, 2),
        "directional_improvement": round(directional, 2),
        "mcid": mcid,
        "meets_mcid": directional >= mcid,
        "note": "meaningful change (>= MCID)"
        if directional >= mcid
        else "below MCID — not yet a clinically meaningful change",
    }


def net_collection_per_visit(total_collected: float, delivered_visits: int) -> dict:
    """Net collection per delivered visit."""
    if delivered_visits <= 0:
        return {"net_collection_per_visit": None, "note": "delivered_visits must be > 0"}
    return {
        "net_collection_per_visit": round(total_collected / delivered_visits, 2),
        "total_collected": total_collected,
        "delivered_visits": delivered_visits,
    }


if __name__ == "__main__":
    for mins in (7, 8, 22, 23, 37, 53, 68, 83, 98):
        print(f"{mins} min ->", eight_minute_rule_units(mins)["billable_units"], "unit(s)")
    print("utilization:", visit_utilization(132, 160))
    print("cancellation:", cancellation_rate(12, 6, 160))
    print("adherence:", plan_of_care_adherence(9, 12))
    print("referral_conv:", referral_conversion_rate(68, 100))
    print("clinic_margin:", clinic_contribution_margin(13200, 8000, 1500))
    print("outcome_vs_mcid:", outcome_change_vs_mcid(40, 54, 8)["note"])
    print("net/visit:", net_collection_per_visit(13200, 132))
