---
name: regression-and-forecasting-review
description: Review or design a regression model or a time-series forecast so it's defensible — pick the model family (OLS / logistic / Poisson GLM; ARIMA / SARIMAX / ETS), check the assumptions that matter for that family, report honest prediction/confidence intervals, and screen for overfitting, data leakage, and "coefficient = cause" overreach. Used by `applied-statistician` (primary).
---

# Skill: regression-and-forecasting-review

> **Invoked by:** `applied-statistician` (primary). Escalate model-as-product / heavy ML feature-engineering to `ravenclaude-core/data-engineer`; financial-model structure to `finance` (when installed).
>
> **When to invoke:** "what drives <outcome>?"; "build/forecast <metric> for next quarter"; "review this regression — is it sound?"
>
> **Output:** the model-family choice + rationale, the assumption checks for that family, the intervals to report, and a pitfall screen (leakage / overfitting / causal overreach).

## Regression

1. **Pick the family by outcome type** ([`../../knowledge/test-selection-decision-tree.md`](../../knowledge/test-selection-decision-tree.md)): continuous → **OLS**; binary → **logistic GLM**; count → **Poisson / negative-binomial GLM**.
2. **Check the assumptions that matter:** linearity (residual-vs-fitted), independence, homoscedasticity (else robust SEs), no severe multicollinearity (VIF), influential points (Cook's distance). Normality of *residuals* matters for small-sample inference, not for the point estimates.
3. **Report coefficients with CIs**, and translate to plain language ("each +1 in X is associated with +β in Y, 95% CI […]").
4. **Causal overreach guard:** a regression coefficient is **association, not cause**, unless the data came from a randomized/causal design. If the user says "drives/causes," route to [`../../knowledge/causal-inference-primer.md`](../../knowledge/causal-inference-primer.md).

## Forecasting (time series)

1. **Inspect first:** trend, seasonality, level shifts. Plot before modelling.
2. **Pick the model:** **ETS / exponential smoothing** for trend+seasonality without exogenous drivers; **(S)ARIMA / SARIMAX** when you need autocorrelation structure and/or exogenous regressors. `statsmodels.tsa` is the Tier-1 home.
3. **Validate honestly:** **time-based** train/test split (never shuffle), backtest on held-out recent periods, report error (MAE/MAPE) on the holdout — not the training fit.
4. **Report prediction intervals, not just the point forecast.** A forecast line with no band is overconfident; the band is the deliverable.

## Pitfall screen (always run)
- **Data leakage** (pitfall #9): any feature unavailable at prediction time? transforms fit on the full set? time series shuffled? → fix the split.
- **Overfitting:** too many predictors for the n; great train fit, poor holdout → simplify / regularize / report holdout error.
- **Causal overreach:** coefficient reported as a lever to pull, with no causal design → downgrade to "associated with."
- **Extrapolation:** forecasting far beyond the data's support, or a regression prediction outside the observed predictor range → flag the uncertainty.

## Guardrails
- Tooling: `statsmodels` (regression, GLM, ARIMA/SARIMAX/ETS) is Tier 1; `linearmodels` (panel/IV) is Tier 2 — reach for it only when the method needs it ([`../../knowledge/statistics-tooling-2026.md`](../../knowledge/statistics-tooling-2026.md)).
- The deliverable is the **interval**, not the point. Always.
