# Forecast accuracy is measured — MAPE and bias together

**Status:** Absolute rule
**Domain:** Demand forecasting
**Applies to:** `supply-chain-planning`

---

## Why this exists

A forecast without measured accuracy is a guess with authority. MAPE (mean absolute percentage
error) tells you the magnitude of the error — how far off the forecast is on average. Bias (mean
error, directional) tells you which direction you are consistently wrong. Both are required:

- A low MAPE with high positive bias means you are consistently over-forecasting — your supply
  plan will over-buy, and you will accumulate excess inventory.
- A low bias with high MAPE means the forecast is unbiased on average but wildly variable — your
  safety-stock calculation will be wrong because σ_demand is understated.

Reporting only MAPE hides systematic bias. Reporting only bias hides large random error. The two
metrics are complements, not substitutes.

## How to apply

Compute on a holdout period (last 3–6 periods withheld from model fitting):

```
MAPE = mean( |actual - forecast| / actual ) × 100%
Bias = mean( (forecast - actual) / actual ) × 100%
```

Positive bias = systematic over-forecast. Negative bias = systematic under-forecast.

**Benchmarks (orientation — vary by industry and SKU volatility):**

| Category | World-class MAPE | Acceptable MAPE | Bias target |
| --- | --- | --- | --- |
| High-volume, stable SKUs | ≤ 5–10% | ≤ 20% | ± 5% |
| Promoted / seasonal SKUs | ≤ 15% | ≤ 30% | ± 10% |
| New products (NPI) | ≤ 30% | ≤ 50% | ± 20% |

Use `scripts/supply_calc.py` `mape_bias()` to compute both from actual / forecast pairs.

**Do:**

- Measure MAPE and bias on every forecast before it enters the S&OP.
- Track both metrics monthly and trend them over time.
- Use the error distribution (σ of forecast errors) as the σ_demand input for safety-stock sizing.
- Report accuracy by ABC class — high-runner accuracy matters most.

**Don't:**

- Publish a forecast with no holdout measurement.
- Report only MAPE and ignore bias (or vice versa).
- Use a global MAPE across all SKUs — one outlier SKU can dominate the average.
- Accept a "gut feel" commercial override without tracking its post-hoc accuracy.

## Edge cases / when the rule does NOT apply

For purely judgement-based forecasts on new products with no history (NPI, analogue-based), formal
MAPE/bias cannot be calculated until actuals accumulate. In that case: document the analogue used,
the assumption behind the ramp, and set a review trigger ("review at 3 months of actuals").

## See also

- [`./safety-stock-covers-variability-not-the-average.md`](./safety-stock-covers-variability-not-the-average.md) — the σ from forecast error feeds the safety-stock formula.
- [`../skills/demand-forecasting/SKILL.md`](../skills/demand-forecasting/SKILL.md) — full workflow.
- [`../scripts/supply_calc.py`](../scripts/supply_calc.py) — `mape_bias()` function.

## Provenance

Standard supply-chain forecasting discipline (IBF — Institute of Business Forecasting; APICS/ASCM
CPIM body of knowledge). MAPE and bias are the two universally cited forecast-accuracy KPIs in the
practitioner literature.

---

_Last reviewed: 2026-06-08 by `claude`._
