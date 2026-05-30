# Pick the regression family from the outcome's type — OLS is not the default for non-continuous outcomes

**Status:** Absolute rule
**Domain:** Regression / model-family selection
**Applies to:** `applied-statistics`

---

## Why this exists

Linear regression (OLS) is the reflex, and for a continuous, roughly-symmetric outcome it is right. For a **binary**, **count**, **proportion**, **time-to-event**, or **clustered** outcome it is the wrong model, and forcing OLS produces nonsense the fit won't warn you about: predicted probabilities below 0 or above 1, negative predicted counts, heteroscedasticity baked in by the outcome's distribution, and standard errors that ignore within-group correlation. The outcome's data type selects the link function and error distribution — that is what the generalized-linear-model framework exists for. The discipline mirrors hypothesis-test selection: **the outcome's type gates the model family**, and the agent names the family before the library (house opinion #1).

## How to apply

Resolve the outcome's data type and its dependence structure, then pick the family:

```
Outcome type                     -> Model family                          (Tier-1 call)
  Continuous, ~symmetric          -> Linear regression (OLS)               smf.ols
  Continuous, skewed/multiplicative -> OLS on log(y), or Gamma GLM         smf.glm(family=Gamma)
  Binary 0/1                      -> Logistic regression                   smf.logit / glm Binomial
  Proportion / rate               -> Binomial or Beta GLM                  smf.glm
  Count                           -> Poisson GLM ...                       smf.glm(family=Poisson)
     ...overdispersed (var > mean) -> Negative-binomial GLM                (check dispersion first)
     ...excess zeros               -> zero-inflated / hurdle model
  Time-to-event (with censoring)  -> Cox proportional hazards / Kaplan-Meier   lifelines
  Repeated / clustered / nested   -> Mixed-effects (random intercepts/slopes) or GEE   mixedlm / bambi
  Ordinal                         -> Ordinal (proportional-odds) logistic
```

**Do:**
- Let the outcome's data type pick the family before writing any model code (continuous → OLS; binary → logistic; count → Poisson/NegBin; time-to-event → Cox; clustered → mixed/GEE).
- For counts, check overdispersion (variance ≫ mean) and move Poisson → negative-binomial when it holds — Poisson SEs are too small under overdispersion.
- For repeated/nested data, model the dependence (mixed-effects or GEE) rather than pretending observations are independent.

**Don't:**
- Run OLS on a 0/1 outcome — predicted "probabilities" escape [0,1] and the errors are structurally heteroscedastic; use logistic.
- Ignore within-cluster correlation (users measured repeatedly, students within schools) — independence is violated and naive SEs are too small.
- Fit Poisson and trust its p-values without checking dispersion.

## Edge cases / when the rule does NOT apply

- **Linear-probability models** (OLS on a binary outcome) are a deliberate econometric choice for interpretable marginal effects in causal work — defensible *as a named choice with robust SEs*, not as an accident.
- **Pure prediction** may favor a flexible learner (gradient boosting) over a named GLM — that is a modelling-as-product call routed to `ravenclaude-core/data-engineer`, not this plugin's interpretable-model lane.
- **Small clusters / few groups** can make mixed-model variance components unstable — sometimes a fixed-effects or cluster-robust-SE approach is more honest; name the trade.

## See also

- [`../knowledge/test-selection-decision-tree.md`](../knowledge/test-selection-decision-tree.md) — the regression leaves (OLS / logistic / Poisson / survival) of the main tree.
- [`../knowledge/stats-test-selection-decision-trees.md`](../knowledge/stats-test-selection-decision-trees.md) — the full regression-family decision tree with tradeoffs.
- [`./regression-run-the-diagnostics-before-trusting-coefficients.md`](./regression-run-the-diagnostics-before-trusting-coefficients.md) — the diagnostics to run once the family is chosen.
- [`../knowledge/statistics-tooling-2026.md`](../knowledge/statistics-tooling-2026.md) — `statsmodels` GLMs; `linearmodels` for panel; `bambi` for Bayesian mixed models.

## Provenance

Codifies house opinion #1 ("method before library") for the modelling leaves of [`../knowledge/test-selection-decision-tree.md`](../knowledge/test-selection-decision-tree.md) (last reviewed 2026-05-26; Tier 1 / consensus). GLM family/link selection by outcome type is standard (McCullagh & Nelder, *Generalized Linear Models*); overdispersion → negative-binomial and zero-inflation are canonical count-model guidance. Tooling tiers per [`../knowledge/statistics-tooling-2026.md`](../knowledge/statistics-tooling-2026.md).

---

_Last reviewed: 2026-05-30 by `claude`_
