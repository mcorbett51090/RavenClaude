# Validate time-series models with a temporal holdout — never a random train-test split

**Status:** Absolute rule
**Domain:** Time-series / forecasting / model validation
**Applies to:** `applied-statistics`

---

## Why this exists

A random train-test split on time-series data leaks future information into the training set: a model trained on 2023-01-15 and 2024-01-15 data "tested" on 2023-07-01 has seen the future. The model has been trained on post-holdout observations, so it learns temporal patterns it wouldn't have had access to at inference time. The result is an optimistically biased accuracy estimate that will fail to generalize. The correct validation is temporal: train on all data up to time T, test on data from T to T+horizon, and repeat this via a rolling-origin evaluation.

## How to apply

```python
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX

def rolling_origin_evaluation(series, order, seasonal_order, 
                               n_test_windows=12, h=1):
    """
    Rolling-origin cross-validation for time series.
    Each fold: train on [0, n-n_test_windows+i], predict i+1 to i+h.
    """
    n = len(series)
    min_train = n - n_test_windows
    errors = []
    
    for i in range(n_test_windows):
        train = series[:min_train + i]
        actual = series[min_train + i: min_train + i + h]
        
        model = SARIMAX(train, order=order, seasonal_order=seasonal_order)
        result = model.fit(disp=False)
        forecast = result.forecast(steps=h)
        
        errors.append((actual.values - forecast.values) ** 2)
    
    rmse = np.sqrt(np.mean(errors))
    print(f"Rolling-origin RMSE (h={h}): {rmse:.4f}")
    return rmse
```

**In the statistical report:**
- State the number of rolling-origin windows used.
- Report accuracy by horizon (h=1, h=3, h=6) — accuracy degrades with horizon.
- Compare to a naive baseline (random walk, seasonal naive) — if the model doesn't beat the baseline, report it.

**Do:**
- Use at least 10-20 rolling-origin windows for a robust estimate.
- Report interval calibration: % of actuals that fall within the 80% and 95% prediction intervals.
- Benchmark against a naive model as a minimum bar.

**Don't:**
- Use `sklearn.model_selection.train_test_split` on time-series data with `shuffle=True`.
- Use `shuffle=False` but with a single holdout window — the rolling-origin evaluation is more robust.
- Claim good accuracy without a temporal holdout.

## Edge cases / when the rule does NOT apply

- Cross-sectional regression models (not time-series) use random splits. This rule applies specifically when the data has a time dependency and the model is used to predict future time points.
- Models with very short series (fewer than 24 observations) may have insufficient data for rolling-origin; use a single temporal holdout (last 20% of observations) with a note about the limited evaluation.

## See also

- [`../agents/applied-statistician.md`](../agents/applied-statistician.md) — drives the regression-and-forecasting-review skill
- [`./timeseries-test-stationarity-and-autocorrelation.md`](./timeseries-test-stationarity-and-autocorrelation.md) — the stationarity gate that precedes model selection

## Provenance

Codifies applied-statistics CLAUDE.md §4 anti-patterns ("pitfall #9" — validating on shuffled time-series data). Standard time-series validation practice; Hyndman & Athanasopoulos, *Forecasting: Principles and Practice* (3rd ed.) Chapter 5 on time-series cross-validation.

---

_Last reviewed: 2026-06-05 by `claude`_
