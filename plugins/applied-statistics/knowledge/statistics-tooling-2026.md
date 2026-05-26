# Knowledge — Statistics tooling (2026)

> **Last reviewed:** 2026-05-26 · **Confidence:** High (versions verified against primary sources on the review date).
> Python-first, because that's the SMB consultant's default environment. R is Tier-1-but-contextual. The agent recommends the **method first, the library second**, and defaults to Tier 1.

---

## Tier table

| Tool | Role | Tier | Verified status (2026-05-26) |
|---|---|---|---|
| **scipy.stats** | Core tests, distributions, basic nonparametrics | **Tier 1** | Ubiquitous; stdlib-adjacent |
| **statsmodels** | Regression, GLMs, time-series (ARIMA/SARIMAX/ETS), statistical tests | **Tier 1** | v0.14.6 (Dec 2025) |
| **pingouin** | Ergonomic applied stats — effect sizes, post-hoc, ANOVA variants, partial/robust correlation, Bayes factors, power, bootstrap CIs (fills scipy's gaps) | **Tier 1** | v0.6.1 (2026); Python ≥3.10 |
| **R** (+ tidyverse, etc.) | The statistician's native environment; richer for some methods | **Tier 1, contextual** | Strong — but Python is the likely client default |
| **Bootstrapping** (scipy / arch / manual) | Distribution-free CIs & inference when assumptions fail | **Tier 1** (technique) | Standard |
| **PyMC** | Full Bayesian / probabilistic programming (MCMC, VI) | **Tier 2** | v6.0.0 / 5.28.x active (PyTensor; JAX/Numba backends) |
| **bambi** | R-style formula interface for Bayesian GLMs/mixed models on PyMC | **Tier 2** | Active 2026; Python ≥3.12 |
| **linearmodels** | Panel data, IV/2SLS, GMM, SUR — econometric estimators statsmodels lacks | **Tier 2** | v7.0 |

> Version numbers carry a retrieval date because they drift. Re-verify before pinning a version in client-facing code.

---

## How the agent should recommend code (without overreaching)

1. **Method before library.** "This is a paired comparison with non-normal data → Wilcoxon signed-rank" *before* `pingouin.wilcoxon`.
2. **Short, runnable snippets** (≤ ~10 illustrative lines) the consultant runs **locally on the client's data** — the agent does not execute analysis pipelines (the data lives outside the repo).
3. **Always pair a test with its assumption check and fallback.** Never emit a bare `ttest_ind` without "check normality/variance first; if it fails, use `mannwhitneyu`."
4. **Report effect size + CI by default** in every suggested snippet, not just the p-value.
5. **Default to Tier 1.** Reach for PyMC/bambi/linearmodels only when the method genuinely requires it, and say *why* — a solo SMB engagement rarely justifies the steeper learning curve.

### Quick library map (Tier 1)

| Need | Call |
|---|---|
| t-test / Mann-Whitney / Wilcoxon / chi-square | `scipy.stats` or `pingouin` |
| ANOVA + post-hoc, effect sizes, power | `pingouin` (`anova`, `pairwise_tukey`, `compute_effsize`, `power_ttest`) |
| OLS / logistic / Poisson regression, diagnostics | `statsmodels` (`smf.ols`, `smf.glm`) |
| ARIMA / SARIMAX / exponential smoothing | `statsmodels.tsa` |
| Distribution-free CI when assumptions fail | bootstrap (`scipy.stats.bootstrap`) |

---

## Provenance

- statsmodels v0.14.6 (Dec 2025): statsmodels.org (retrieved 2026-05-26).
- pingouin v0.6.1, feature set vs scipy, Python ≥3.10: pingouin-stats.org (retrieved 2026-05-26).
- PyMC v6.0.0 / 5.28.x active: github.com/pymc-devs/pymc/releases + pymc.io (retrieved 2026-05-26).
- bambi = PyMC + formulae, mixed-effects, Python ≥3.12: bambinos.github.io/bambi (retrieved 2026-05-26).
- linearmodels v7.0 (panel/IV/GMM/SUR): github.com/bashtage/linearmodels + PyPI (retrieved 2026-05-26).
- Refresh trigger: re-verify versions quarterly or before pinning in a client deliverable.
