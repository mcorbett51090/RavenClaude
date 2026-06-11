#!/usr/bin/env python3
"""
higher_ed_calc.py — Higher-education administration calculator (stdlib only).

Nine functions covering the core higher-ed decision metrics:
  - yield_rate                  : enrolled ÷ admitted
  - funnel_conversion           : stage-to-stage conversion across the admissions funnel
  - net_tuition_revenue         : gross tuition − institutional aid (per student and total)
  - discount_rate               : institutional aid ÷ gross tuition
  - retention_rate              : returning ÷ entering cohort (persistence)
  - program_contribution_margin : program net tuition − instructional/program cost
  - breakeven_enrollment        : fixed program cost ÷ contribution per student
  - tuition_dependency_ratio    : net tuition revenue ÷ total operating revenue
  - early_alert_score           : weighted leading-signal risk score → tier

All functions are pure (no I/O) and return a dict with the result plus the input
assumptions so callers can audit the calculation.

DISCLAIMER: outputs are decision-support only, not financial-aid, compliance, or
accreditation advice. The caller supplies every input; this script does not source
data. Title IV / FERPA / accreditation specifics must be verified against current
regulation and institutional counsel.
"""

from __future__ import annotations

from collections.abc import Sequence


def yield_rate(enrolled: int, admitted: int) -> dict:
    """Yield = enrolled ÷ admitted."""
    if admitted <= 0:
        return {"yield_rate": None, "note": "admitted must be > 0"}
    r = enrolled / admitted
    return {
        "yield_rate": round(r, 4),
        "yield_pct": round(r * 100, 2),
        "enrolled": enrolled,
        "admitted": admitted,
    }


def funnel_conversion(stage_counts: dict[str, int]) -> dict:
    """
    Stage-to-stage conversion across the admissions funnel.

    stage_counts is an ORDERED dict of stage -> count, e.g.
    {"inquiry": 20000, "applicant": 6000, "admit": 3000, "deposit": 900, "enroll": 800}.
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
    steepest = max(
        (s for s in steps if s["conversion"] is not None),
        key=lambda s: s["drop_pct"],
        default=None,
    )
    return {"steps": steps, "steepest_drop": steepest}


def net_tuition_revenue(
    gross_tuition_per_student: float,
    institutional_aid_per_student: float,
    enrolled_headcount: int = 1,
) -> dict:
    """Net tuition revenue = (gross − institutional aid) per student × headcount."""
    net_per = gross_tuition_per_student - institutional_aid_per_student
    return {
        "net_tuition_per_student": round(net_per, 2),
        "total_net_tuition_revenue": round(net_per * enrolled_headcount, 2),
        "gross_tuition_per_student": gross_tuition_per_student,
        "institutional_aid_per_student": institutional_aid_per_student,
        "enrolled_headcount": enrolled_headcount,
    }


def discount_rate(institutional_aid: float, gross_tuition: float) -> dict:
    """Tuition discount rate = institutional aid ÷ gross tuition."""
    if gross_tuition <= 0:
        return {"discount_rate": None, "note": "gross_tuition must be > 0"}
    r = institutional_aid / gross_tuition
    return {
        "discount_rate": round(r, 4),
        "discount_pct": round(r * 100, 2),
        "institutional_aid": institutional_aid,
        "gross_tuition": gross_tuition,
    }


def retention_rate(returning: int, entering_cohort: int) -> dict:
    """Persistence/retention = returning ÷ entering cohort (frame by entering cohort)."""
    if entering_cohort <= 0:
        return {"retention_rate": None, "note": "entering_cohort must be > 0"}
    r = returning / entering_cohort
    return {
        "retention_rate": round(r, 4),
        "retention_pct": round(r * 100, 2),
        "attrition_pct": round((1 - r) * 100, 2),
        "returning": returning,
        "entering_cohort": entering_cohort,
    }


def program_contribution_margin(
    program_tuition_revenue: float,
    direct_instructional_cost: float,
    program_specific_cost: float,
) -> dict:
    """Program contribution margin = net program tuition − (instructional + program-specific cost)."""
    margin = program_tuition_revenue - direct_instructional_cost - program_specific_cost
    base = program_tuition_revenue if program_tuition_revenue > 0 else None
    return {
        "contribution_margin": round(margin, 2),
        "contribution_margin_pct": round(margin / base * 100, 2) if base else None,
        "program_tuition_revenue": program_tuition_revenue,
        "direct_instructional_cost": direct_instructional_cost,
        "program_specific_cost": program_specific_cost,
    }


def breakeven_enrollment(
    fixed_program_cost: float,
    net_tuition_per_student: float,
    variable_cost_per_student: float = 0.0,
) -> dict:
    """Breakeven enrollment = fixed cost ÷ contribution per student."""
    contribution_per_student = net_tuition_per_student - variable_cost_per_student
    if contribution_per_student <= 0:
        return {
            "breakeven_enrollment": None,
            "note": "contribution per student must be > 0 (net tuition exceeds variable cost)",
        }
    import math

    return {
        "breakeven_enrollment": math.ceil(fixed_program_cost / contribution_per_student),
        "contribution_per_student": round(contribution_per_student, 2),
        "fixed_program_cost": fixed_program_cost,
    }


def tuition_dependency_ratio(
    net_tuition_revenue_total: float, total_operating_revenue: float
) -> dict:
    """Tuition dependency = net tuition revenue ÷ total operating revenue (a structural-risk metric)."""
    if total_operating_revenue <= 0:
        return {
            "tuition_dependency": None,
            "note": "total_operating_revenue must be > 0",
        }
    r = net_tuition_revenue_total / total_operating_revenue
    return {
        "tuition_dependency": round(r, 4),
        "tuition_dependency_pct": round(r * 100, 2),
        "net_tuition_revenue_total": net_tuition_revenue_total,
        "total_operating_revenue": total_operating_revenue,
    }


def early_alert_score(signals: Sequence[tuple[str, float, bool]]) -> dict:
    """
    Weighted leading-signal risk score → tier.

    signals is a sequence of (name, weight, triggered) tuples, e.g.
    [("attendance", 1.0, True), ("lms_drop", 1.0, False), ("midterm", 1.5, True)].
    The score is the sum of weights for triggered signals; the tier follows the
    count of triggered signals (the constitution's ladder).
    """
    triggered = [(n, w) for (n, w, t) in signals if t]
    score = round(sum(w for _, w in triggered), 3)
    count = len(triggered)
    if count >= 3:
        tier = "high"
    elif count == 2:
        tier = "elevated"
    elif count == 1:
        tier = "watch"
    else:
        tier = "none"
    return {
        "score": score,
        "triggered_count": count,
        "tier": tier,
        "triggered_signals": [n for n, _ in triggered],
    }


if __name__ == "__main__":
    print("yield:", yield_rate(800, 3000))
    print(
        "funnel:",
        funnel_conversion(
            {"inquiry": 20000, "applicant": 6000, "admit": 3000, "deposit": 900, "enroll": 800}
        )["steepest_drop"],
    )
    print("net_rev:", net_tuition_revenue(50000, 27500, 800))
    print("discount:", discount_rate(27500, 50000))
    print("retention:", retention_rate(820, 1000))
    print("program_margin:", program_contribution_margin(900000, 520000, 140000))
    print("breakeven:", breakeven_enrollment(300000, 22500, 3000))
    print("tuition_dependency:", tuition_dependency_ratio(18000000, 26000000))
    print(
        "early_alert:",
        early_alert_score(
            [("attendance", 1.0, True), ("lms_drop", 1.0, False), ("midterm", 1.5, True)]
        ),
    )
