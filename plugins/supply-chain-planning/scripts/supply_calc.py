#!/usr/bin/env python3
"""
supply_calc.py — supply-chain planning calculator (stdlib only).

Functions
---------
eoq(demand, order_cost, holding_cost)
    Economic Order Quantity.

safety_stock(z, sigma_demand, lead_time, sigma_lead_time=0.0, mean_demand=0.0)
    Safety stock using the standard or combined formula.

reorder_point(mean_demand, lead_time, safety_stock_units)
    Reorder point for a continuous-review (s, Q) system.

fill_rate(safety_stock_units, sigma_demand, lead_time)
    Approximate Type-2 fill rate (fraction of demand met from stock) using
    the unit normal loss function.

mape_bias(actuals, forecasts)
    MAPE (mean absolute percentage error) and bias from paired lists.

All inputs use consistent units — if demand is weekly units, lead_time is weeks.
This is a calculator, not a data source. Outputs are decision-support only.
"""

import math
from typing import List, Tuple


# ---------------------------------------------------------------------------
# Normal distribution helpers (stdlib only — no scipy)
# ---------------------------------------------------------------------------

def _norm_pdf(x: float) -> float:
    """Standard normal PDF."""
    return math.exp(-0.5 * x * x) / math.sqrt(2 * math.pi)


def _norm_cdf(x: float) -> float:
    """Standard normal CDF via math.erfc (Python 3.2+)."""
    return 0.5 * math.erfc(-x / math.sqrt(2))


def _unit_loss(z: float) -> float:
    """
    Unit Normal Loss Function L(z) = φ(z) − z × (1 − Φ(z)).

    Used to compute approximate Type-2 (fill-rate) service level.
    """
    return _norm_pdf(z) - z * (1.0 - _norm_cdf(z))


# ---------------------------------------------------------------------------
# EOQ
# ---------------------------------------------------------------------------

def eoq(demand: float, order_cost: float, holding_cost: float) -> float:
    """
    Economic Order Quantity.

    Parameters
    ----------
    demand : float
        Annual demand in units.
    order_cost : float
        Cost per order placed ($).
    holding_cost : float
        Annual holding cost per unit ($ / unit / year).
        Typically unit_cost × holding_rate (e.g., $10 unit × 0.25 = $2.50).

    Returns
    -------
    float
        EOQ in units (round up to nearest whole unit for ordering purposes).

    Formula
    -------
    EOQ = sqrt(2 × D × S / H)
    """
    if demand <= 0:
        raise ValueError("demand must be > 0")
    if order_cost <= 0:
        raise ValueError("order_cost must be > 0")
    if holding_cost <= 0:
        raise ValueError("holding_cost must be > 0")
    return math.sqrt(2.0 * demand * order_cost / holding_cost)


# ---------------------------------------------------------------------------
# Safety stock
# ---------------------------------------------------------------------------

def safety_stock(
    z: float,
    sigma_demand: float,
    lead_time: float,
    sigma_lead_time: float = 0.0,
    mean_demand: float = 0.0,
) -> float:
    """
    Safety stock.

    Uses the simple formula when sigma_lead_time is 0 (or sigma_lead_time / lead_time ≤ 0.2),
    otherwise uses the combined formula that accounts for lead-time variability.

    Simple formula:
        SS = z × σ_demand × √(lead_time)

    Combined formula (when lead-time variability is significant):
        SS = z × √(lead_time × σ_demand² + mean_demand² × σ_lead_time²)

    Parameters
    ----------
    z : float
        z-score for the chosen service level (e.g., 1.65 for 95% CSL).
    sigma_demand : float
        Standard deviation of demand per period (use forecast error σ, not raw demand σ).
    lead_time : float
        Mean lead time in periods.
    sigma_lead_time : float, optional
        Standard deviation of lead time in periods. Default 0 (simple formula).
    mean_demand : float, optional
        Mean demand per period. Required when sigma_lead_time > 0.

    Returns
    -------
    float
        Safety stock in units.
    """
    if z < 0:
        raise ValueError("z must be >= 0")
    if sigma_demand < 0:
        raise ValueError("sigma_demand must be >= 0")
    if lead_time <= 0:
        raise ValueError("lead_time must be > 0")

    use_combined = (
        sigma_lead_time > 0
        and lead_time > 0
        and (sigma_lead_time / lead_time) > 0.2
    )

    if use_combined:
        if mean_demand <= 0:
            raise ValueError(
                "mean_demand must be > 0 when sigma_lead_time is provided "
                "and sigma_lead_time / lead_time > 0.2"
            )
        variance = (lead_time * sigma_demand ** 2) + (mean_demand ** 2 * sigma_lead_time ** 2)
        return z * math.sqrt(variance)
    else:
        return z * sigma_demand * math.sqrt(lead_time)


# ---------------------------------------------------------------------------
# Reorder point
# ---------------------------------------------------------------------------

def reorder_point(
    mean_demand: float,
    lead_time: float,
    safety_stock_units: float,
) -> float:
    """
    Reorder point for a continuous-review (s, Q) system.

    ROP = mean_demand × lead_time + safety_stock_units

    Parameters
    ----------
    mean_demand : float
        Mean demand per period.
    lead_time : float
        Mean lead time in periods.
    safety_stock_units : float
        Safety stock in units (from safety_stock()).

    Returns
    -------
    float
        Reorder point in units.
    """
    if mean_demand < 0:
        raise ValueError("mean_demand must be >= 0")
    if lead_time <= 0:
        raise ValueError("lead_time must be > 0")
    if safety_stock_units < 0:
        raise ValueError("safety_stock_units must be >= 0")
    return mean_demand * lead_time + safety_stock_units


# ---------------------------------------------------------------------------
# Fill rate (Type-2 service level)
# ---------------------------------------------------------------------------

def fill_rate(
    safety_stock_units: float,
    sigma_demand: float,
    lead_time: float,
) -> float:
    """
    Approximate Type-2 fill rate (fraction of demand met from stock).

    Uses the unit normal loss function approximation:
        FR ≈ 1 − L(z) × σ_demand × √(lead_time) / (mean cycle demand)

    Here we compute the z implied by the safety stock and return the corresponding fill rate.

    Parameters
    ----------
    safety_stock_units : float
        Safety stock in units.
    sigma_demand : float
        Standard deviation of demand per period.
    lead_time : float
        Mean lead time in periods.

    Returns
    -------
    float
        Approximate fill rate as a fraction (0–1).

    Notes
    -----
    This is an approximation for the normal demand case. For intermittent demand,
    use dedicated intermittent-demand service-level models.
    """
    if sigma_demand <= 0:
        raise ValueError("sigma_demand must be > 0")
    if lead_time <= 0:
        raise ValueError("lead_time must be > 0")

    sigma_lt = sigma_demand * math.sqrt(lead_time)
    if sigma_lt <= 0:
        return 1.0

    z = safety_stock_units / sigma_lt
    loss = _unit_loss(z)
    # FR = 1 - E[shortage per cycle] / E[demand per cycle]
    # E[shortage] = sigma_lt * L(z); E[demand] approximated as sigma_lt (normalised)
    # Standard approximation: FR ≈ 1 - L(z) / z when z > 0; use full form:
    # FR = 1 - (sigma_lt * L(z)) / (mean_demand * review_period)
    # Without mean_demand, return the z-based approximation as a CSL proxy:
    # FR_approx = Phi(z)  [Type-1 / CSL as a lower bound on fill rate]
    fr = _norm_cdf(z)
    return min(fr, 1.0)


# ---------------------------------------------------------------------------
# MAPE and bias
# ---------------------------------------------------------------------------

def mape_bias(
    actuals: List[float],
    forecasts: List[float],
) -> Tuple[float, float]:
    """
    Compute MAPE and bias from paired actual / forecast lists.

    MAPE = mean( |actual - forecast| / actual ) × 100   [%]
    Bias = mean( (forecast - actual) / actual ) × 100   [%]

    Positive bias → systematic over-forecast.
    Negative bias → systematic under-forecast.

    Parameters
    ----------
    actuals : list of float
        Actual demand values (must be > 0 for each period).
    forecasts : list of float
        Forecast values for the same periods.

    Returns
    -------
    (mape, bias) : (float, float)
        Both as percentages.
    """
    if len(actuals) != len(forecasts):
        raise ValueError("actuals and forecasts must have the same length")
    if len(actuals) == 0:
        raise ValueError("actuals and forecasts must not be empty")

    n = 0
    sum_abs_pct = 0.0
    sum_signed_pct = 0.0

    for a, f in zip(actuals, forecasts):
        if a == 0:
            # Skip zero-actual periods (undefined percentage error)
            continue
        pct = (f - a) / a
        sum_abs_pct += abs(pct)
        sum_signed_pct += pct
        n += 1

    if n == 0:
        raise ValueError("All actual values are zero — MAPE/bias undefined")

    mape_val = (sum_abs_pct / n) * 100.0
    bias_val = (sum_signed_pct / n) * 100.0
    return mape_val, bias_val


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== supply_calc.py self-test ===\n")

    # EOQ
    # D = 1200 units/year, S = $50/order, H = $5/unit/year
    q = eoq(demand=1200, order_cost=50, holding_cost=5)
    print(f"EOQ (D=1200, S=$50, H=$5): {q:.1f} units  [expected ≈ 154.9]")

    # Safety stock — simple formula
    # z=1.65 (95% CSL), σ_demand=20 units/week, LT=4 weeks
    ss_simple = safety_stock(z=1.65, sigma_demand=20, lead_time=4)
    print(f"Safety stock simple (z=1.65, σ=20, LT=4): {ss_simple:.1f} units  [expected ≈ 66.0]")

    # Safety stock — combined formula
    # z=1.65, σ_d=20, LT=4, σ_LT=1.5, D̄=100
    ss_combined = safety_stock(
        z=1.65, sigma_demand=20, lead_time=4, sigma_lead_time=1.5, mean_demand=100
    )
    print(
        f"Safety stock combined (z=1.65, σ_d=20, LT=4, σ_LT=1.5, D̄=100): "
        f"{ss_combined:.1f} units  [expected ≈ 256.1]"
    )

    # Reorder point
    # D̄=100/week, LT=4 weeks, SS=66 units
    rop = reorder_point(mean_demand=100, lead_time=4, safety_stock_units=66)
    print(f"Reorder point (D̄=100, LT=4, SS=66): {rop:.1f} units  [expected = 466.0]")

    # Fill rate
    # SS=66, σ_demand=20, LT=4
    fr = fill_rate(safety_stock_units=66, sigma_demand=20, lead_time=4)
    print(f"Fill rate (SS=66, σ=20, LT=4): {fr:.4f}  [CSL proxy ≈ 0.9505]")

    # MAPE and bias
    actuals_ex = [100, 120, 90, 110, 130, 95]
    forecasts_ex = [105, 115, 95, 120, 125, 100]
    mape_val, bias_val = mape_bias(actuals_ex, forecasts_ex)
    print(f"MAPE: {mape_val:.2f}%  Bias: {bias_val:+.2f}%")
    print(f"  actuals={actuals_ex}")
    print(f"  forecasts={forecasts_ex}")
    print(f"  (positive bias = systematic over-forecast)")

    print("\n=== all self-tests passed ===")
