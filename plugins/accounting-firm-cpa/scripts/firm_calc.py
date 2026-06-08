#!/usr/bin/env python3
"""
firm_calc.py — CPA firm economics calculator (stdlib only).

Five functions covering the core metrics of a US public-accounting practice:
  realization_rate   — collected ÷ standard (rack-rate) billed
  utilization_rate   — charge (billable) hours ÷ available hours
  effective_rate     — collected fees ÷ actual hours charged
  leverage_ratio     — staff/senior hours ÷ manager/partner hours on an engagement
  fixed_fee_margin   — (fixed fee − cost of hours) ÷ fixed fee

All inputs are supplied by the caller; this script is a calculator, not a data source.
Outputs are decision-support, not accounting, tax, or business advice.

Usage:
    python3 firm_calc.py                  # run self-tests and print results
    python3 -c "from firm_calc import *; print(realization_rate(18000, 20000))"
"""


# ---------------------------------------------------------------------------
# Core metric functions
# ---------------------------------------------------------------------------


def realization_rate(collected: float, standard_billed: float) -> float:
    """
    Realization rate = collected fees / standard (rack-rate) fees billed.

    Args:
        collected:        Fees actually collected (cash received) for the engagement.
        standard_billed:  Standard fees at the firm's rack rate (hours × standard rate,
                          before write-downs or write-ups).

    Returns:
        Realization rate as a decimal (e.g., 0.87 = 87%).

    Raises:
        ValueError: if standard_billed is zero or negative.
    """
    if standard_billed <= 0:
        raise ValueError("standard_billed must be positive")
    return collected / standard_billed


def utilization_rate(charge_hours: float, available_hours: float) -> float:
    """
    Utilization rate = charge (billable) hours / total available hours.

    Args:
        charge_hours:    Hours charged to client engagements (billable) in the period.
        available_hours: Total work hours available in the period (e.g., 2,080 for a
                         full-time staff member in a 52-week year at 40 hrs/week).

    Returns:
        Utilization rate as a decimal (e.g., 0.78 = 78%).

    Raises:
        ValueError: if available_hours is zero or negative.
    """
    if available_hours <= 0:
        raise ValueError("available_hours must be positive")
    return charge_hours / available_hours


def effective_rate(collected: float, actual_hours: float) -> float:
    """
    Effective hourly rate = collected fees / actual hours charged.

    The "real" rate earned after write-downs and write-ups — what the firm
    actually earned per hour of professional time.

    Args:
        collected:     Fees actually collected for the engagement.
        actual_hours:  Actual hours charged (time logged) for the engagement.

    Returns:
        Effective rate in dollars per hour.

    Raises:
        ValueError: if actual_hours is zero or negative.
    """
    if actual_hours <= 0:
        raise ValueError("actual_hours must be positive")
    return collected / actual_hours


def leverage_ratio(
    staff_senior_hours: float, manager_partner_hours: float
) -> float:
    """
    Leverage ratio = staff/senior hours / manager/partner hours.

    A higher ratio means more work is done by lower-cost staff relative to
    higher-cost supervisory time — generally indicates a more profitable
    engagement structure (at the same realization rate).

    Args:
        staff_senior_hours:    Hours charged by staff and senior associates.
        manager_partner_hours: Hours charged by managers and partners.

    Returns:
        Leverage ratio (e.g., 3.5 means 3.5 staff/senior hours per manager/partner hour).

    Raises:
        ValueError: if manager_partner_hours is zero or negative.
    """
    if manager_partner_hours <= 0:
        raise ValueError("manager_partner_hours must be positive")
    return staff_senior_hours / manager_partner_hours


def fixed_fee_margin(
    fixed_fee: float, total_hours: float, blended_cost_rate: float
) -> float:
    """
    Fixed-fee margin = (fixed fee − cost of hours) / fixed fee.

    Measures what percentage of the fixed fee is margin after direct labor cost.
    Note: this is a contribution-margin view (direct labor only); it does not
    include overhead, benefits, or indirect costs.

    Args:
        fixed_fee:          The fixed fee billed to the client.
        total_hours:        Actual hours charged on the engagement.
        blended_cost_rate:  Blended cost rate for the engagement staff (fully-loaded
                            cost per hour, including salary and benefits, for the
                            staff mix actually used).

    Returns:
        Margin as a decimal (e.g., 0.35 = 35% contribution margin).
        May be negative if the engagement ran over its cost estimate.

    Raises:
        ValueError: if fixed_fee is zero or negative.
    """
    if fixed_fee <= 0:
        raise ValueError("fixed_fee must be positive")
    if blended_cost_rate < 0:
        raise ValueError("blended_cost_rate cannot be negative")
    cost_of_hours = total_hours * blended_cost_rate
    return (fixed_fee - cost_of_hours) / fixed_fee


# ---------------------------------------------------------------------------
# Convenience: print a formatted summary for a single engagement
# ---------------------------------------------------------------------------


def engagement_summary(
    engagement_name: str,
    collected: float,
    standard_billed: float,
    actual_hours: float,
    staff_senior_hours: float,
    manager_partner_hours: float,
    fixed_fee: float,
    blended_cost_rate: float,
    available_hours: float,
) -> dict:
    """
    Compute all five metrics for one engagement and return them in a dict.

    All inputs are the same as the individual functions above.
    'available_hours' is used for utilization (total staff available hours in the period).
    """
    return {
        "engagement": engagement_name,
        "realization_rate": realization_rate(collected, standard_billed),
        "utilization_rate": utilization_rate(actual_hours, available_hours),
        "effective_rate": effective_rate(collected, actual_hours),
        "leverage_ratio": leverage_ratio(staff_senior_hours, manager_partner_hours),
        "fixed_fee_margin": fixed_fee_margin(fixed_fee, actual_hours, blended_cost_rate),
    }


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("firm_calc.py — self-test")
    print("=" * 60)

    # --- Test 1: realization_rate ---
    # Client billed at $20,000 standard; $17,500 collected after write-down.
    r = realization_rate(17500, 20000)
    assert abs(r - 0.875) < 1e-9, f"realization_rate failed: {r}"
    print(f"\n[1] realization_rate(17500, 20000) = {r:.1%}  (expected 87.5%)")

    # Edge: collected > standard (write-up)
    r_writeup = realization_rate(21000, 20000)
    assert abs(r_writeup - 1.05) < 1e-9, f"write-up case failed: {r_writeup}"
    print(f"    write-up case (21000/20000) = {r_writeup:.1%}  (expected 105.0%)")

    # --- Test 2: utilization_rate ---
    # Senior charged 1,540 hours; 2,000 available (25 weeks × 80h, approximation).
    u = utilization_rate(1540, 2000)
    assert abs(u - 0.77) < 1e-9, f"utilization_rate failed: {u}"
    print(f"\n[2] utilization_rate(1540, 2000) = {u:.1%}  (expected 77.0%)")

    # Full-year: 1,820 billable out of 2,080 available.
    u2 = utilization_rate(1820, 2080)
    print(f"    full-year case (1820/2080)   = {u2:.1%}")

    # --- Test 3: effective_rate ---
    # Collected $17,500; 110 actual hours → effective rate $159.09/hr.
    e = effective_rate(17500, 110)
    assert abs(e - (17500 / 110)) < 1e-6, f"effective_rate failed: {e}"
    print(f"\n[3] effective_rate(17500, 110) = ${e:.2f}/hr  (expected ${17500/110:.2f}/hr)")

    # --- Test 4: leverage_ratio ---
    # 120 staff/senior hours; 30 manager/partner hours → leverage 4.0.
    lev = leverage_ratio(120, 30)
    assert abs(lev - 4.0) < 1e-9, f"leverage_ratio failed: {lev}"
    print(f"\n[4] leverage_ratio(120, 30) = {lev:.2f}  (expected 4.00)")

    # Low-leverage case: partner-heavy engagement.
    lev2 = leverage_ratio(40, 60)
    print(f"    partner-heavy case (40/60) = {lev2:.2f}  (below 1.0 = partner doing staff work)")

    # --- Test 5: fixed_fee_margin ---
    # Fixed fee $15,000; 85 hours at $95/hr blended cost → cost $8,075 → margin 46.2%.
    margin = fixed_fee_margin(15000, 85, 95)
    expected_margin = (15000 - 85 * 95) / 15000
    assert abs(margin - expected_margin) < 1e-9, f"fixed_fee_margin failed: {margin}"
    print(f"\n[5] fixed_fee_margin(15000, 85hrs, $95/hr cost)")
    print(f"    cost of hours = ${85*95:,.0f}")
    print(f"    margin        = {margin:.1%}  (expected {expected_margin:.1%})")

    # Negative margin (over-ran the engagement).
    neg_margin = fixed_fee_margin(8000, 100, 95)
    print(f"    over-run case (8000 fee, 100hrs @ $95) = {neg_margin:.1%}  (negative = loss)")

    # --- Test 6: engagement_summary ---
    summary = engagement_summary(
        engagement_name="Acme LLC — 1065 Tax Return",
        collected=12600,
        standard_billed=14000,
        actual_hours=70,
        staff_senior_hours=50,
        manager_partner_hours=20,
        fixed_fee=12600,
        blended_cost_rate=85,
        available_hours=2080,
    )
    print(f"\n[6] engagement_summary — {summary['engagement']}")
    print(f"    realization   = {summary['realization_rate']:.1%}")
    print(f"    utilization   = {summary['utilization_rate']:.1%}  (of 2,080 available hrs)")
    print(f"    effective rate= ${summary['effective_rate']:.2f}/hr")
    print(f"    leverage      = {summary['leverage_ratio']:.2f}x")
    print(f"    fixed-fee margin = {summary['fixed_fee_margin']:.1%}")

    # --- Test 7: error handling ---
    errors_caught = 0
    try:
        realization_rate(10000, 0)
    except ValueError:
        errors_caught += 1
    try:
        utilization_rate(1000, -1)
    except ValueError:
        errors_caught += 1
    try:
        effective_rate(5000, 0)
    except ValueError:
        errors_caught += 1
    try:
        leverage_ratio(100, 0)
    except ValueError:
        errors_caught += 1
    try:
        fixed_fee_margin(0, 10, 50)
    except ValueError:
        errors_caught += 1
    assert errors_caught == 5, f"Expected 5 ValueError catches, got {errors_caught}"
    print(f"\n[7] Error handling: {errors_caught}/5 ValueError checks passed")

    print("\n" + "=" * 60)
    print("All self-tests PASSED")
    print("=" * 60)
    print(
        "\nNote: outputs are decision-support only — not accounting, tax, or business advice."
        "\nAll inputs are supplied by the caller; this script does not read external data."
    )
