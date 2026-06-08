#!/usr/bin/env python3
"""
finops_calc.py — FinOps & Cloud Cost calculator (stdlib only, Python 3.8+)

Provides five functions for recurring FinOps arithmetic:
  1. break_even()          — RI/SP break-even months
  2. blended_vs_effective() — blended vs effective hourly rate (committed + on-demand mix)
  3. unit_cost()           — cost per unit (cost ÷ units)
  4. commitment_coverage() — what % of usage the steady-state baseline covers
  5. anomaly_z_score()     — simple z-score for cost anomaly detection

All are CALCULATORS, not data sources. The caller supplies every input.
Outputs are decision-support, not accounting, tax, or investment advice.

Usage:
    python3 finops_calc.py                  # runs the self-test
    python3 -c "from finops_calc import break_even; print(break_even(0.10, 0.06, 200.0))"
"""

import math
import statistics
from typing import List, Tuple


# ---------------------------------------------------------------------------
# 1. RI / Savings-Plan break-even analysis
# ---------------------------------------------------------------------------

def break_even(
    on_demand_hourly: float,
    committed_hourly: float,
    upfront_cost: float = 0.0,
    hours_per_month: float = 730.0,
) -> Tuple[float, float]:
    """
    Calculate break-even months for a commitment (RI, Savings Plan, CUD).

    Parameters
    ----------
    on_demand_hourly : float
        On-demand price per hour (e.g. 0.10 for $0.10/hr).
    committed_hourly : float
        Effective committed price per hour (amortised upfront + hourly rate).
        For a no-upfront RI, this is just the committed hourly rate.
        For a partial/all-upfront RI, include the amortised upfront separately
        via the `upfront_cost` parameter and keep committed_hourly as the
        recurring charge only.
    upfront_cost : float
        One-time upfront payment (default 0.0 for no-upfront).
    hours_per_month : float
        Billing hours per calendar month (default 730 = 365*24/12).

    Returns
    -------
    (break_even_months, monthly_saving_at_break_even)
        break_even_months — months until cumulative saving covers the upfront cost.
        monthly_saving_at_break_even — monthly saving at the break-even point
        (this is the ongoing saving after break-even is reached).

    Raises
    ------
    ValueError
        If committed_hourly >= on_demand_hourly (commitment saves nothing or costs more).
    """
    if committed_hourly >= on_demand_hourly:
        raise ValueError(
            f"committed_hourly ({committed_hourly}) must be less than "
            f"on_demand_hourly ({on_demand_hourly}) for a commitment to save money."
        )

    monthly_od_cost = on_demand_hourly * hours_per_month
    monthly_committed_cost = committed_hourly * hours_per_month
    monthly_saving = monthly_od_cost - monthly_committed_cost

    if upfront_cost == 0.0:
        # No upfront: break-even is immediate (first month is cheaper)
        be_months = 0.0
    else:
        be_months = upfront_cost / monthly_saving

    return round(be_months, 2), round(monthly_saving, 4)


# ---------------------------------------------------------------------------
# 2. Blended vs effective hourly rate
# ---------------------------------------------------------------------------

def blended_vs_effective(
    committed_hours: float,
    committed_hourly: float,
    on_demand_hours: float,
    on_demand_hourly: float,
) -> Tuple[float, float, float]:
    """
    Calculate blended rate and effective rate for a committed + on-demand mix.

    Parameters
    ----------
    committed_hours : float
        Hours consumed under commitment in the billing period.
    committed_hourly : float
        Effective hourly rate under commitment (after amortisation).
    on_demand_hours : float
        Hours consumed on-demand in the billing period.
    on_demand_hourly : float
        On-demand hourly rate.

    Returns
    -------
    (blended_rate, effective_rate, total_cost)
        blended_rate    — total cost / total hours (simple average by hours).
        effective_rate  — same as blended_rate in this model; included for clarity.
                          (In AWS billing terminology, the "effective rate" accounts for
                          amortised upfront costs; this function models that via
                          committed_hourly already including any amortised upfront.)
        total_cost      — total spend for the period.

    Raises
    ------
    ValueError
        If total hours is zero.
    """
    total_hours = committed_hours + on_demand_hours
    if total_hours == 0:
        raise ValueError("Total hours (committed + on-demand) cannot be zero.")

    total_cost = (committed_hours * committed_hourly) + (on_demand_hours * on_demand_hourly)
    blended_rate = total_cost / total_hours

    return round(blended_rate, 6), round(blended_rate, 6), round(total_cost, 4)


# ---------------------------------------------------------------------------
# 3. Unit cost (cost ÷ units)
# ---------------------------------------------------------------------------

def unit_cost(
    total_cost: float,
    units: float,
    unit_label: str = "unit",
) -> Tuple[float, str]:
    """
    Calculate cost per unit (unit economics).

    Parameters
    ----------
    total_cost : float
        Total attributed cost for the period (e.g. monthly cloud cost for a feature).
    units : float
        Number of units in the denominator (e.g. monthly active customers, API requests).
    unit_label : str
        Human-readable label for the unit (default 'unit').

    Returns
    -------
    (cost_per_unit, label_string)
        cost_per_unit  — total_cost / units.
        label_string   — formatted description, e.g. "$0.0042 per API request".

    Raises
    ------
    ValueError
        If units is zero or negative.
    """
    if units <= 0:
        raise ValueError(f"units must be > 0, got {units}.")

    cpu = total_cost / units
    label = f"${cpu:.6f} per {unit_label}"
    return round(cpu, 8), label


# ---------------------------------------------------------------------------
# 4. Commitment coverage %
# ---------------------------------------------------------------------------

def commitment_coverage(
    committed_baseline_hourly: float,
    total_avg_hourly: float,
) -> Tuple[float, str]:
    """
    Calculate what percentage of average usage the steady-state commitment covers.

    A commitment at the P0 floor means coverage < 100% by design — the rest runs on-demand.
    Coverage > 100% means over-committed (commitment exceeds average usage).

    Parameters
    ----------
    committed_baseline_hourly : float
        The hourly resource level covered by the commitment (the P0 baseline).
    total_avg_hourly : float
        The average hourly usage over the measurement period.

    Returns
    -------
    (coverage_pct, interpretation)
        coverage_pct    — committed_baseline / total_avg * 100.
        interpretation  — one of "under-committed (on-demand above baseline)",
                          "at-baseline (correctly sized to the floor)",
                          or "over-committed (commitment exceeds average usage — risk of waste)".

    Raises
    ------
    ValueError
        If total_avg_hourly is zero.
    """
    if total_avg_hourly <= 0:
        raise ValueError("total_avg_hourly must be > 0.")

    pct = (committed_baseline_hourly / total_avg_hourly) * 100.0

    if pct > 105:
        interpretation = "over-committed (commitment exceeds average usage — risk of stranded cost)"
    elif pct >= 95:
        interpretation = "at-baseline (commitment closely matches average usage)"
    else:
        interpretation = "under-committed (on-demand peaks above commitment baseline — expected)"

    return round(pct, 2), interpretation


# ---------------------------------------------------------------------------
# 5. Anomaly z-score
# ---------------------------------------------------------------------------

def anomaly_z_score(
    daily_costs: List[float],
    today_cost: float,
    threshold_z: float = 2.0,
) -> Tuple[float, bool, str]:
    """
    Calculate a simple z-score for a daily cost value against a rolling baseline.

    Parameters
    ----------
    daily_costs : list[float]
        Rolling window of daily costs (e.g. past 14 days). Must have ≥ 3 values
        to compute a meaningful standard deviation.
    today_cost : float
        The cost value being evaluated for anomaly.
    threshold_z : float
        Z-score threshold above which the cost is flagged as an anomaly (default 2.0).

    Returns
    -------
    (z_score, is_anomaly, description)
        z_score     — (today_cost - mean) / stdev of the baseline window.
        is_anomaly  — True if z_score > threshold_z.
        description — human-readable summary.

    Raises
    ------
    ValueError
        If daily_costs has fewer than 3 values or standard deviation is zero.
    """
    if len(daily_costs) < 3:
        raise ValueError("daily_costs must have at least 3 values for a meaningful z-score.")

    mean = statistics.mean(daily_costs)
    stdev = statistics.stdev(daily_costs)  # sample stdev (n-1)

    if stdev == 0:
        raise ValueError(
            "Standard deviation of daily_costs is zero — all values are identical. "
            "Cannot compute a z-score on a zero-variance baseline."
        )

    z = (today_cost - mean) / stdev
    is_anomaly = z > threshold_z

    status = "ANOMALY" if is_anomaly else "normal"
    desc = (
        f"{status}: today=${today_cost:.2f}, baseline mean=${mean:.2f}, "
        f"stdev=${stdev:.2f}, z={z:.2f} (threshold={threshold_z})"
    )

    return round(z, 4), is_anomaly, desc


# ---------------------------------------------------------------------------
# Self-test (__main__)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 65)
    print("finops_calc.py — self-test")
    print("=" * 65)

    errors: List[str] = []

    # --- 1. break_even ---
    print("\n[1] break_even()")
    # No-upfront SP: on-demand $0.10/hr, committed $0.06/hr, no upfront
    be_months, monthly_saving = break_even(0.10, 0.06, upfront_cost=0.0)
    print(f"  No-upfront case: break_even={be_months} months, monthly_saving=${monthly_saving:.4f}")
    assert be_months == 0.0, f"Expected 0.0 break-even for no-upfront, got {be_months}"
    assert monthly_saving > 0, "Monthly saving should be positive"

    # Partial-upfront RI: on-demand $0.10/hr, committed $0.058/hr, upfront $180
    be_months2, monthly_saving2 = break_even(0.10, 0.058, upfront_cost=180.0)
    print(f"  Partial-upfront: break_even={be_months2} months, monthly_saving=${monthly_saving2:.4f}")
    assert be_months2 > 0, "Partial-upfront should have positive break-even months"

    # Error case: committed >= on_demand
    try:
        break_even(0.10, 0.12)
        errors.append("break_even: should have raised ValueError for committed >= on_demand")
    except ValueError:
        print("  ValueError on committed >= on_demand: OK")

    # --- 2. blended_vs_effective ---
    print("\n[2] blended_vs_effective()")
    # 500 committed hours at $0.06, 230 on-demand hours at $0.10
    blended, effective, total = blended_vs_effective(500, 0.06, 230, 0.10)
    print(f"  blended_rate=${blended:.6f}/hr, effective_rate=${effective:.6f}/hr, total=${total:.2f}")
    assert blended < 0.10, "Blended rate should be less than on-demand rate"
    assert total == round(500 * 0.06 + 230 * 0.10, 4), "Total cost mismatch"

    try:
        blended_vs_effective(0, 0.06, 0, 0.10)
        errors.append("blended_vs_effective: should raise ValueError for zero hours")
    except ValueError:
        print("  ValueError on zero total hours: OK")

    # --- 3. unit_cost ---
    print("\n[3] unit_cost()")
    # $4,200/month, 1,000,000 API requests
    cpu, label = unit_cost(4200.0, 1_000_000, "API request")
    print(f"  {label}")
    assert cpu == round(4200.0 / 1_000_000, 8), "unit_cost mismatch"

    # Cost per customer: $12,000/month, 3,000 MAU
    cpu2, label2 = unit_cost(12_000.0, 3_000, "active customer")
    print(f"  {label2}")
    assert cpu2 == round(12_000.0 / 3_000, 8), "unit_cost customer mismatch"

    try:
        unit_cost(1000.0, 0)
        errors.append("unit_cost: should raise ValueError for units=0")
    except ValueError:
        print("  ValueError on units=0: OK")

    # --- 4. commitment_coverage ---
    print("\n[4] commitment_coverage()")
    # Committed baseline 60 units/hr, average 80 units/hr → 75% coverage
    pct, interp = commitment_coverage(60.0, 80.0)
    print(f"  coverage={pct}% — {interp}")
    assert pct == 75.0, f"Expected 75.0%, got {pct}"
    assert "under-committed" in interp

    # Over-committed: committed 90, average 80 → 112.5%
    pct2, interp2 = commitment_coverage(90.0, 80.0)
    print(f"  coverage={pct2}% — {interp2}")
    assert pct2 > 100, "Should be over-committed"
    assert "over-committed" in interp2

    # At-baseline: committed ~80, average 80 → ~100%
    pct3, interp3 = commitment_coverage(80.0, 80.0)
    print(f"  coverage={pct3}% — {interp3}")
    assert "at-baseline" in interp3 or "over-committed" in interp3

    try:
        commitment_coverage(50.0, 0.0)
        errors.append("commitment_coverage: should raise ValueError for zero average")
    except ValueError:
        print("  ValueError on zero average: OK")

    # --- 5. anomaly_z_score ---
    print("\n[5] anomaly_z_score()")
    # Normal baseline with higher variance (~$1,000/day ±$100);
    # today is $1,050 — within 1 stdev, should not be flagged at z>2.
    baseline_normal = [
        900, 1100, 950, 1050, 1000, 1080, 920, 1070, 990, 1020, 960, 1040, 980, 1010
    ]
    z, flagged, desc = anomaly_z_score(baseline_normal, 1050.0, threshold_z=2.0)
    print(f"  Normal day:  {desc}")
    assert not flagged, f"Expected no anomaly for a modest cost increase, got z={z}"

    # Cost spike: today is $2,500 — clearly above z=2 against this baseline
    z2, flagged2, desc2 = anomaly_z_score(baseline_normal, 2500.0, threshold_z=2.0)
    print(f"  Spike day:   {desc2}")
    assert flagged2, "Expected anomaly for a 2.5x cost spike"
    assert z2 > 2.0

    try:
        anomaly_z_score([100, 100], 150.0)
        errors.append("anomaly_z_score: should raise ValueError for < 3 data points")
    except ValueError:
        print("  ValueError on < 3 data points: OK")

    try:
        anomaly_z_score([100, 100, 100], 150.0)
        errors.append("anomaly_z_score: should raise ValueError for zero stdev")
    except ValueError:
        print("  ValueError on zero stdev: OK")

    # --- Summary ---
    print("\n" + "=" * 65)
    if errors:
        print(f"SELF-TEST FAILED — {len(errors)} error(s):")
        for e in errors:
            print(f"  FAIL: {e}")
        raise SystemExit(1)
    else:
        print("SELF-TEST PASSED — all assertions OK")
    print("=" * 65)
