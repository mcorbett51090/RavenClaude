# Test stationarity and autocorrelation before modelling a time series — never shuffle, never trust IID

**Status:** Absolute rule
**Domain:** Time series / temporal dependence
**Applies to:** `applied-statistics`

---

## Why this exists

Time-ordered data violates the independence assumption that almost every standard test and regression rests on, and the violation is invisible in the numbers — a regression of one trending series on another returns a high R² and a tiny p-value that mean *nothing* (a **spurious regression** between two random walks). Two failure modes dominate: **non-stationarity** (the mean/variance drift over time, so a model fit to the past doesn't describe the future and correlations are spurious) and **autocorrelation** (residuals carry serial dependence, so standard errors are too small and significance is overstated). The fix is a gate before any ARIMA/forecast/temporal-regression: test for a unit root, difference or detrend to stationarity, then confirm the residuals are white noise. And because the data is ordered, you must **never shuffle** it — train/test splits are temporal (pitfall #9, leakage), or the backtest is fiction.

## How to apply

Run the stationarity + autocorrelation gate before fitting (Tier-1: `statsmodels.tsa`):

```
1. STATIONARITY
   ADF test (null = unit root / non-stationary) AND KPSS (null = stationary) — read together
        non-stationary -> difference (d) until stationary; or detrend; log to stabilize variance
   Seasonality?  visible period in the series / ACF -> seasonal differencing (D) or SARIMA

2. AUTOCORRELATION (model identification + residual check)
   ACF / PACF plots -> read AR(p) and MA(q) orders
   Fit (S)ARIMA; then on the RESIDUALS:
       Ljung-Box test -> residuals must be white noise (no leftover autocorrelation)
       if not white noise -> model order is wrong; re-identify

3. VALIDATION (never shuffle)
   Temporal train/test split or rolling-origin / time-series cross-validation
   Forecast ships WITH a prediction interval, never a bare point line
```

**Do:**
- Test stationarity (ADF + KPSS together — they have opposite nulls) and difference/detrend to stationarity before fitting.
- Inspect ACF/PACF to identify orders, then confirm residuals are white noise with Ljung-Box.
- Split and cross-validate *temporally* (rolling-origin); always attach a prediction interval to a forecast.

**Don't:**
- Regress one trending series on another and trust the R²/p-value — difference both first or you have a spurious regression.
- Shuffle time-ordered data into a random train/test split — that leaks the future into the past (pitfall #9).
- Present a forecast point line with no prediction interval (a `data-platform` anti-pattern this plugin guards).

## Edge cases / when the rule does NOT apply

- **Cointegration** — two non-stationary series can share a stable long-run relationship; there, difference-then-regress *discards* the signal — use an error-correction model / Engle-Granger or Johansen test instead.
- **Already-stationary series** (a stable, mean-reverting metric with no trend/seasonality) need no differencing — over-differencing introduces artificial negative autocorrelation; the ADF/KPSS check tells you to stop.
- **Pure cross-sectional data** has no temporal ordering — this gate doesn't apply; the standard independence check (clustering?) does.

## See also

- [`../knowledge/stats-test-selection-decision-trees.md`](../knowledge/stats-test-selection-decision-trees.md) — the time-series model-selection decision tree (ARIMA / SARIMA / ETS / regression-with-ARMA-errors).
- [`./regression-run-the-diagnostics-before-trusting-coefficients.md`](./regression-run-the-diagnostics-before-trusting-coefficients.md) — the Durbin-Watson independence check that routes here.
- [`../knowledge/statistical-pitfalls.md`](../knowledge/statistical-pitfalls.md) — pitfall #9 (leakage / "for time series, never shuffle").
- [`../knowledge/statistics-tooling-2026.md`](../knowledge/statistics-tooling-2026.md) — `statsmodels.tsa` (ARIMA/SARIMAX/ETS, ADF, Ljung-Box).

## Provenance

Codifies the temporal-independence facet of pitfall #7 (assumptions) and pitfall #9 ("for time series, never shuffle") in [`../knowledge/statistical-pitfalls.md`](../knowledge/statistical-pitfalls.md) (last reviewed 2026-05-26; Tier 1 / consensus), and the "forecast ships with a prediction interval" anti-pattern in [`../CLAUDE.md`](../CLAUDE.md) §4. Stationarity/spurious-regression/Box-Jenkins canon (Box-Jenkins; Hamilton, *Time Series Analysis*). ADF+KPSS read-together is standard practice (opposite nulls). `statsmodels.tsa` per [`../knowledge/statistics-tooling-2026.md`](../knowledge/statistics-tooling-2026.md).

---

_Last reviewed: 2026-05-30 by `claude`_
