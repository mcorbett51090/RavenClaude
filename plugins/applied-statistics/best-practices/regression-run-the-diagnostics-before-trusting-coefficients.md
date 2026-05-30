# Run the residual / multicollinearity / leverage diagnostics before trusting a regression

**Status:** Absolute rule
**Domain:** Regression / model diagnostics
**Applies to:** `applied-statistics`

---

## Why this exists

An OLS fit always returns coefficients, standard errors, p-values, and an R² — whether or not its assumptions hold. Those numbers are only defensible after the diagnostics pass. Unmodeled non-linearity, heteroscedastic or autocorrelated residuals, multicollinearity, and a handful of high-leverage points each produce a fit that *looks* authoritative and quietly misleads: biased coefficients, standard errors that are too small (false significance), or an estimate driven by three outliers. This is pitfall #7 (assumption violations) in regression form. The discipline mirrors the hypothesis-test assumption gate: a regression ships with its residual plots, its multicollinearity check, and its influence check — or it doesn't ship.

## How to apply

After fitting, run the four diagnostic families before quoting any coefficient (Tier-1: `statsmodels`):

```
1. RESIDUALS
   Linearity / structure   residual-vs-fitted plot (should be a shapeless cloud)
   Normality of residuals  Q-Q plot (matters for small-n inference, not point estimates)
   Homoscedasticity        Breusch-Pagan / White; funnel shape in residual plot
        violated -> robust (HC) standard errors, or a variance-stabilizing transform
   Independence            Durbin-Watson (time-ordered data) -> if autocorrelated, see time-series rules

2. MULTICOLLINEARITY
   Variance Inflation Factor per predictor; VIF > ~5-10 is a flag [rule of thumb]
        -> drop / combine collinear predictors, or use regularization; coefficients are unstable

3. INFLUENCE / LEVERAGE
   Cook's distance, leverage (hat values), studentized residuals
        -> inspect high-influence points; refit with/without and report sensitivity

4. FIT, honestly
   Adjusted R² (not raw R²); out-of-sample error for a predictive claim
```

**Do:**
- Plot residuals-vs-fitted and a Q-Q plot every time; eyeball them before reading the coefficient table.
- Check VIF when predictors may be correlated; a coefficient under high multicollinearity is unstable even when "significant."
- Identify high-leverage / high-Cook's-distance points and report whether the conclusion survives their removal.

**Don't:**
- Read coefficients, p-values, or R² off a fit whose residuals you never looked at.
- Quote a raw R² as "variance explained" for a model with many predictors — use adjusted R², and for a predictive claim, out-of-sample error.
- Treat heteroscedasticity as fatal — robust (HC) standard errors keep the OLS point estimates and fix the inference; name that as the route taken.

## Edge cases / when the rule does NOT apply

- **Regularized models (ridge/lasso/elastic-net)** trade unbiasedness for stability under multicollinearity — VIF matters less, but you've changed the estimand; don't interpret penalized coefficients as unbiased effects.
- **Large-sample robustness** — mild non-normality of residuals barely affects inference at large n via the CLT; "robust" is a defended judgment with the Q-Q plot shown, not a skipped check.
- **GLMs (logistic/Poisson)** have their own diagnostics (deviance residuals, dispersion, separation) — the *spirit* (check before trusting) holds, but the specific tools differ; see the regression-family rule.

## See also

- [`./regression-pick-the-model-family.md`](./regression-pick-the-model-family.md) — choosing OLS vs logistic vs Poisson vs mixed before diagnosing.
- [`./check-assumptions-before-the-test.md`](./check-assumptions-before-the-test.md) — the hypothesis-test analogue of this gate.
- [`./timeseries-test-stationarity-and-autocorrelation.md`](./timeseries-test-stationarity-and-autocorrelation.md) — when the independence check fails on time-ordered residuals.
- [`../knowledge/statistics-tooling-2026.md`](../knowledge/statistics-tooling-2026.md) — `statsmodels` for OLS/GLM diagnostics and HC robust SEs.

## Provenance

Codifies house opinion #4 ("check assumptions or use the fallback") in [`../CLAUDE.md`](../CLAUDE.md) §3 applied to regression, and pitfall #7 in [`../knowledge/statistical-pitfalls.md`](../knowledge/statistical-pitfalls.md) (last reviewed 2026-05-26; Tier 1 / consensus). VIF / Cook's-distance / Breusch-Pagan are standard regression-diagnostics canon (Belsley-Kuh-Welsch; Fox, *Applied Regression Analysis*). VIF thresholds marked as rules of thumb. `statsmodels` per [`../knowledge/statistics-tooling-2026.md`](../knowledge/statistics-tooling-2026.md).

---

_Last reviewed: 2026-05-30 by `claude`_
