---
description: "Build a defensible demand forecast: traverse the forecast-method selection tree, clean demand history, select and fit the statistical model, measure MAPE and bias on a holdout period, design the consensus overlay process, and hand off the error distribution to inventory policy."
---

# Demand Forecasting

**Purpose:** produce a calibrated, accuracy-measured demand forecast that serves as the single
number for MRP, safety-stock sizing, and the S&OP demand review.

---

## Steps

### 1. Qualify and clean demand history

- Verify the demand signal: actual demand (unconstrained) not shipments (constrained by stock-outs).
- Remove outliers: promotions, one-off orders, data errors. Flag each removal with a reason.
- Check data completeness: minimum 12 periods for a seasonal model; minimum 6 periods for a
  non-seasonal model. Below minimums → use analogue-based or judgement-based method.
- Calculate demand statistics: mean (D̄), standard deviation (σ), coefficient of variation
  (CV = σ/μ), demand frequency (for intermittent check).

### 2. Traverse the forecast-method selection tree

Before choosing a method, traverse `## Decision Tree: Forecast-method selection` in
[`../../knowledge/supply-chain-planning-decision-trees.md`](../../knowledge/supply-chain-planning-decision-trees.md).
The tree selects based on: demand frequency (intermittent vs. continuous), trend presence, seasonality
presence, and causal data availability.

### 3. Fit the statistical baseline

| Demand character | Method |
|---|---|
| Stable, no trend, no season | Simple exponential smoothing (SES / α) |
| Trending, no season | Holt double exponential smoothing (α, β) |
| Trending + seasonal | Holt-Winters triple exponential smoothing (α, β, γ) |
| Intermittent (CV > 0.5, sporadic) | Croston's method or TSB (Teunter-Syntetos-Babai) |
| Causal data available (price, promotions, macro) | Regression or causal model |

- Fit on the training period (all periods minus the holdout window).
- Holdout: last 3–6 periods for accuracy measurement.

### 4. Measure forecast accuracy (mandatory)

Compute on the holdout period using [`../../scripts/supply_calc.py`](../../scripts/supply_calc.py)
`mape_bias()`:

- **MAPE** = mean |actual − forecast| / actual × 100%. World-class ≤ 10% for high-runners; 20–30%
  acceptable for volatile / promoted SKUs.
- **Bias** = mean (forecast − actual) / actual × 100%. A positive bias = systematic over-forecast.
  Target: |bias| ≤ 5%.
- **Tracking signal** = cumulative forecast error / MAD. |TS| > 4 → model out of control.

Document accuracy results. **A forecast without measured accuracy cannot enter the S&OP.**

### 5. Design the consensus overlay

- Present the statistical baseline to the demand review with the accuracy KPIs visible.
- Collect commercial overrides (sales, marketing, key account) — each override must be:
  - Named (who raised it)
  - Quantified (volume and period)
  - Rationale documented (promotion, new channel, customer intel)
- The consensus forecast = statistical baseline + approved overlays.
- Track override accuracy post-hoc: overrides consistently worse than the baseline get retired.

### 6. Document seasonality if present

- Decompose: trend + seasonal index + residual.
- Seasonal index per period = period mean / overall mean (multiplicative) or period mean − overall
  mean (additive). Use multiplicative when the seasonal swing scales with level.
- Document the indices and the year the seasonal base was calculated.
- Forward-adjust for known calendar shifts (Easter, trading-day count, new store openings).

### 7. Hand off to inventory policy

The demand forecast produces two outputs for `inventory-optimization-engineer`:
1. The point forecast (D̄ per period, by SKU and horizon).
2. The forecast error distribution (σ of forecast errors from the holdout = σ_demand for safety-
   stock sizing).

## Anti-patterns

- Publishing a forecast with no MAPE or bias measurement.
- Fitting a model without first cleaning promotions and outliers from history.
- Using exponential smoothing on intermittent demand without checking demand frequency.
- Allowing commercial overrides with no documentation or post-audit.
- Using shipment data as the demand signal without adjusting for stock-out periods.

## Output

A demand forecast package: method selected (with decision-tree path), cleaned history note, the
statistical model parameters, MAPE + bias from the holdout, seasonal indices (if applicable), the
consensus overlay log, and the error distribution for safety-stock sizing. Use the `demand-planning-analyst`
agent for the full guided workflow.
