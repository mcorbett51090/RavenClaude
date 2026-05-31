---
description: "Model or forecast a time series defensibly — test stationarity (ADF + KPSS), difference/detrend, identify orders from ACF/PACF, confirm residuals are white noise, validate temporally (never shuffle), and ship a prediction interval."
argument-hint: "[the series, e.g. 'forecast weekly active users for the next quarter']"
---

# Model a time series

You are running `/applied-statistics:model-time-series`. Turn the user's temporal question (`$ARGUMENTS`) into a defensible model or forecast by running the stationarity + autocorrelation gate before fitting, the way the `applied-statistician` agent enforces — because time-ordered data violates the independence assumption every standard test rests on, invisibly.

## When to use this

You have time-ordered data and need a forecast, a trend estimate, or a temporal regression. NOT for cross-sectional comparisons (use `/applied-statistics:choose-statistical-test`) and NOT for "is this single dashboard move real?" (that is `/applied-statistics:analyze-dashboard-metric-movement`).

## Steps

1. **Test stationarity before fitting anything** (`timeseries-test-stationarity-and-autocorrelation.md`): run ADF (null = unit root) AND KPSS (null = stationary) and read them together — they have opposite nulls. Difference (d) or detrend until stationary; log to stabilize variance; seasonal-difference (D) for a visible period.
2. **Never regress one trending series on another and trust the R²/p** (`timeseries-test-stationarity-and-autocorrelation.md`): two random walks produce a high R² and tiny p that mean nothing — a spurious regression. Difference both first.
3. **Identify orders, then check residuals** (`timeseries-test-stationarity-and-autocorrelation.md`): read AR(p)/MA(q) from ACF/PACF, fit (S)ARIMA, then confirm residuals are white noise with Ljung-Box — if not, the order is wrong; re-identify.
4. **Pick the model family by the outcome's type** if it isn't a plain continuous level (`regression-pick-the-model-family.md`): a count outcome over time is Poisson/NegBin, not OLS on the raw count; time-to-event with censoring is Cox.
5. **Validate temporally — never shuffle** (`timeseries-test-stationarity-and-autocorrelation.md`): use a temporal train/test split or rolling-origin cross-validation; a shuffled split leaks the future and the backtest is fiction (pitfall #9).
6. **Ship the forecast WITH a prediction interval** (`timeseries-test-stationarity-and-autocorrelation.md`, `effect-size-and-ci-not-bare-p.md`), and communicate it with the uncertainty band per `report-communicate-uncertainty-to-non-statisticians.md`. Use Tier-1 `statsmodels.tsa`.

## Guardrails

- A bare forecast point line with no prediction interval is an undisclosed risk — always attach the band.
- Shuffling time-ordered data for a train/test split leaks the future; the split must be temporal.
- High R² between two trending series is the spurious-regression trap, not a finding — difference first, then assess.
