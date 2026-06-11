#!/usr/bin/env python3
"""
devrel_calc.py — Developer Relations / DX metrics calculator (stdlib only).

Eight functions covering the core DevRel decision metrics:
  - time_to_first_value          : median sign-up → first-success time
  - activation_rate              : first-success ÷ sign-ups
  - funnel_conversion            : stage-to-stage conversion across the activation funnel
  - content_roi                  : activations attributable ÷ content effort (hours)
  - community_health             : active ratio, answer rate, contributor conversion
  - cost_per_activation          : program spend ÷ activations attributable
  - program_activations_per_dollar: rank a program by expected activations per dollar
  - vanity_pairing_check         : flag a vanity input reported without an outcome

All functions are pure (no I/O) and return a dict with the result plus the input
assumptions so callers can audit the calculation.

DISCLAIMER: outputs are decision-support only. The caller supplies every input;
this script does not source data.
"""

from __future__ import annotations

import statistics
from collections.abc import Sequence


def time_to_first_value(signup_to_success_minutes: Sequence[float]) -> dict:
    """Median time (minutes) from sign-up to first success — the core TTFV metric."""
    vals = [float(v) for v in signup_to_success_minutes if v is not None]
    if not vals:
        return {"ttfv_minutes": None, "n": 0, "note": "no data"}
    return {
        "ttfv_minutes": round(statistics.median(vals), 2),
        "mean_minutes": round(statistics.fmean(vals), 2),
        "n": len(vals),
        "p90_minutes": round(sorted(vals)[max(0, int(0.9 * len(vals)) - 1)], 2),
    }


def activation_rate(first_success: int, sign_ups: int) -> dict:
    """Activation rate = developers reaching first success ÷ sign-ups."""
    if sign_ups <= 0:
        return {"activation_rate": None, "note": "sign_ups must be > 0"}
    rate = first_success / sign_ups
    return {
        "activation_rate": round(rate, 4),
        "activation_pct": round(rate * 100, 2),
        "first_success": first_success,
        "sign_ups": sign_ups,
    }


def funnel_conversion(stage_counts: dict[str, int]) -> dict:
    """
    Stage-to-stage conversion across the activation funnel.

    stage_counts is an ORDERED dict of stage_name -> count, e.g.
    {"sign_up": 1000, "credential": 700, "first_call": 500, "first_success": 320}.
    Returns each step's conversion and flags the steepest drop.
    """
    stages = list(stage_counts.items())
    steps = []
    for (a_name, a), (b_name, b) in zip(stages, stages[1:]):
        conv = (b / a) if a > 0 else None
        steps.append(
            {
                "from": a_name,
                "to": b_name,
                "conversion": round(conv, 4) if conv is not None else None,
                "drop_pct": round((1 - conv) * 100, 2) if conv is not None else None,
            }
        )
    steepest = None
    if steps:
        steepest = max(
            (s for s in steps if s["conversion"] is not None),
            key=lambda s: s["drop_pct"],
            default=None,
        )
    return {
        "steps": steps,
        "steepest_drop": steepest,
        "overall": round(stages[-1][1] / stages[0][1], 4)
        if stages and stages[0][1] > 0
        else None,
    }


def content_roi(activations_attributed: int, effort_hours: float) -> dict:
    """Activations attributable to a content effort ÷ hours invested."""
    if effort_hours <= 0:
        return {"activations_per_hour": None, "note": "effort_hours must be > 0"}
    return {
        "activations_per_hour": round(activations_attributed / effort_hours, 3),
        "activations_attributed": activations_attributed,
        "effort_hours": effort_hours,
    }


def community_health(
    active_members: int,
    total_members: int,
    questions_answered: int,
    questions_asked: int,
    contributors: int,
    active_users: int,
) -> dict:
    """Composite community-health snapshot: active ratio, answer rate, contributor conversion."""
    out: dict = {}
    out["active_ratio"] = (
        round(active_members / total_members, 4) if total_members > 0 else None
    )
    out["answer_rate"] = (
        round(questions_answered / questions_asked, 4) if questions_asked > 0 else None
    )
    out["contributor_conversion"] = (
        round(contributors / active_users, 4) if active_users > 0 else None
    )
    out["inputs"] = {
        "active_members": active_members,
        "total_members": total_members,
        "questions_answered": questions_answered,
        "questions_asked": questions_asked,
        "contributors": contributors,
        "active_users": active_users,
    }
    return out


def cost_per_activation(program_spend: float, activations_attributed: int) -> dict:
    """Cost-per-activation = program spend ÷ activations attributable to it."""
    if activations_attributed <= 0:
        return {
            "cost_per_activation": None,
            "note": "activations_attributed must be > 0",
        }
    return {
        "cost_per_activation": round(program_spend / activations_attributed, 2),
        "program_spend": program_spend,
        "activations_attributed": activations_attributed,
    }


def program_activations_per_dollar(
    audience_fit: float,
    activation_path_strength: float,
    expected_reach: float,
    cost: float,
) -> dict:
    """
    Rank a program (event/sponsorship/content) by expected activations per dollar.

    audience_fit and activation_path_strength are 0..1 multipliers; a program with
    no activation path scores near zero regardless of reach. expected_reach is a
    count; cost is dollars.
    """
    if cost <= 0:
        return {"activations_per_dollar": None, "note": "cost must be > 0"}
    expected_activations = audience_fit * activation_path_strength * expected_reach
    return {
        "expected_activations": round(expected_activations, 2),
        "activations_per_dollar": round(expected_activations / cost, 5),
        "inputs": {
            "audience_fit": audience_fit,
            "activation_path_strength": activation_path_strength,
            "expected_reach": expected_reach,
            "cost": cost,
        },
    }


def vanity_pairing_check(metric_name: str, has_outcome_metric: bool) -> dict:
    """Flag a vanity input reported without a paired activation/adoption outcome."""
    vanity = {"stars", "followers", "impressions", "attendees", "registrants", "pageviews"}
    is_vanity = metric_name.strip().lower() in vanity
    ok = (not is_vanity) or has_outcome_metric
    return {
        "metric": metric_name,
        "is_vanity_input": is_vanity,
        "paired_with_outcome": has_outcome_metric,
        "ok": ok,
        "note": "OK"
        if ok
        else "vanity input reported with no activation/adoption outcome — pair it or cut it",
    }


if __name__ == "__main__":
    # Tiny self-check / usage demo.
    print("activation_rate:", activation_rate(320, 1000))
    print(
        "funnel:",
        funnel_conversion(
            {"sign_up": 1000, "credential": 700, "first_call": 500, "first_success": 320}
        )["steepest_drop"],
    )
    print("ttfv:", time_to_first_value([12, 30, 8, 45, 19, 60, 22]))
    print("cost/activation:", cost_per_activation(20000, 250))
    print(
        "program/$:",
        program_activations_per_dollar(0.7, 0.6, 5000, 15000)["activations_per_dollar"],
    )
    print("vanity:", vanity_pairing_check("stars", has_outcome_metric=False)["note"])
