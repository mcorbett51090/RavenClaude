# Report prediction intervals on every forecast — never a bare point line

**Status:** Absolute rule
**Domain:** Forecasting / uncertainty communication
**Applies to:** `applied-statistics`

---

## Why this exists

A forecast with no interval communicates false certainty. The point estimate (the expected value) is almost guaranteed to be wrong in magnitude; the interval says how wrong it might plausibly be. A business that plans hiring headcount or inventory levels based on a bare point forecast is planning on the wrong number. Prediction intervals (for a single future observation) and forecast intervals (for a future mean) are qualitatively different from confidence intervals — they are wider because they account for both parameter uncertainty and the inherent variability of the process. Omitting them is not a simplification; it is misinformation.

## How to apply

```python
from statsmodels.tsa.statespace.sarimax import SARIMAX

model = SARIMAX(train, order=(1,1,1), seasonal_order=(1,1,1,12))
result = model.fit(disp=False)

# Get forecast with prediction intervals
forecast = result.get_forecast(steps=12)
forecast_mean = forecast.predicted_mean
forecast_ci = forecast.conf_int(alpha=0.05)  # 95% prediction interval

print(forecast_mean)
print(forecast_ci)
```

Always visualize the interval:

```python
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 5))
plt.plot(train.index, train, label='Historical', color='black')
plt.plot(forecast_mean.index, forecast_mean, label='Forecast', color='blue')
plt.fill_between(
    forecast_ci.index,
    forecast_ci.iloc[:, 0],
    forecast_ci.iloc[:, 1],
    alpha=0.3, label='95% prediction interval'
)
plt.legend()
```

In every statistical report, state:
- The interval width and meaning: "We expect the next observation to fall in this range 95% of the time under the model assumptions."
- The key uncertainty drivers: model uncertainty, process variance, horizon length.
- Holdout interval calibration: in a well-calibrated model, ~95% of actual holdout values should fall in the 95% PI.

**Do:**
- Report both 80% and 95% prediction intervals — the 80% is often more operationally useful for planning.
- Widen the uncertainty narrative as the forecast horizon grows.
- Validate interval calibration on a holdout set before citing the intervals to a client.

**Don't:**
- Show only the point forecast line in a stakeholder chart.
- Conflate a confidence interval (parameter uncertainty) with a prediction interval (future observation).
- Report an interval calibrated on training data without reporting the holdout coverage.

## Edge cases / when the rule does NOT apply

If a forecast is used only to determine direction of change (up/down) and the absolute value is not operationally relevant, a point-only forecast with an explicit "direction only" label is acceptable — but this must be stated clearly in the report.

## See also

- [`../agents/applied-statistician.md`](../agents/applied-statistician.md) — drives the regression-and-forecasting-review skill
- [`./effect-size-and-ci-not-bare-p.md`](./effect-size-and-ci-not-bare-p.md) — the companion rule for hypothesis test outputs

## Provenance

Codifies applied-statistics CLAUDE.md §4 anti-patterns ("A forecast point line with no prediction interval") and §3 house opinion #2 ("The deliverable is the interval, not the point"). Standard forecasting practice across all textbook time-series and regression references.

---

_Last reviewed: 2026-06-05 by `claude`_
