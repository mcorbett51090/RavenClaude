---
description: "Vet a regression before trusting its coefficients: pick the model family, run residual / multicollinearity / leverage diagnostics, and report adjusted R-squared or out-of-sample error honestly."
argument-hint: "[the model, e.g. 'OLS of revenue on spend, region, and tenure']"
---

# Diagnose a regression

You are running `/applied-statistics:diagnose-regression`. Run the diagnostic gate on the model (`$ARGUMENTS`) before any coefficient, p-value, or R-squared is quoted — a regression ships with its residual plots, its multicollinearity check, and its influence check, or it doesn't ship (the `applied-statistician` discipline).

## When to use this

You have fit (or are about to fit) a regression and need to know whether the coefficients are defensible. Use it before reporting "X drives Y by N." NOT for a bare two-group comparison (that is `/applied-statistics:choose-statistical-test`), and NOT for asserting causation from an observational fit (that is `/applied-statistics:assess-causal-claim`).

## Steps

1. **Pick the model family first** by the outcome type (`regression-pick-the-model-family.md`): OLS for continuous, logistic for binary, Poisson/NegBin for counts, mixed for clustered/hierarchical data — choosing the family before diagnosing.
2. **Run the residual diagnostics** (`regression-run-the-diagnostics-before-trusting-coefficients.md`): residual-vs-fitted (linearity/structure), Q-Q (normality of residuals), Breusch-Pagan/White (homoscedasticity) — funnel shape → robust (HC) standard errors or a variance-stabilizing transform; Durbin-Watson on time-ordered data.
3. **Check multicollinearity** with VIF per predictor; VIF > ~5-10 is a flag [rule of thumb] — coefficients under high collinearity are unstable even when "significant"; drop/combine or regularize (`regression-run-the-diagnostics-before-trusting-coefficients.md`).
4. **Check influence / leverage**: Cook's distance, hat values, studentized residuals; refit with and without high-influence points and report whether the conclusion survives.
5. **Report fit honestly**: adjusted R-squared (not raw R-squared) for many predictors; out-of-sample error for any predictive claim (`regression-run-the-diagnostics-before-trusting-coefficients.md`).
6. **Lead the write-up with the effect size + CI**, p-value secondary (`effect-size-and-ci-not-bare-p.md`), per the plugin's `templates/statistical-report.md`. Use Tier-1 `statsmodels` for OLS/GLM diagnostics and HC robust SEs.

## Guardrails

- Never read coefficients off a fit whose residuals you never plotted.
- A coefficient is association, not a causal lever, unless a causal design backs it — downgrade the language otherwise.
- Penalized (ridge/lasso) coefficients are not unbiased effects; you changed the estimand — don't interpret them as such.
