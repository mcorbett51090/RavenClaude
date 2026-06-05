# Knowledge — Statistical method selection: decision trees

> **Last reviewed:** 2026-05-30 · **Confidence:** High (canonical biostatistics / econometrics / time-series consensus; see each tree's Provenance line).
> This file is the **extended decision-tree bank** for method selection across the plugin's whole surface — hypothesis tests, parametric-vs-nonparametric, regression family, causal-inference design, and time-series model. It complements (does not replace) [`test-selection-decision-tree.md`](test-selection-decision-tree.md), which holds the primary hypothesis-test tree plus the assumption gate and the parametric↔nonparametric fallback table.
>
> **How the agent uses it:** traverse the relevant Mermaid graph **top-to-bottom before naming a method** (the pre-action decision-tree traversal the Capability Grounding Protocol requires). Resolve each node against the data in *observable* terms — the outcome's data type, the group structure, the natural variation available — not against keywords in the user's phrasing. The first branch whose condition resolves cleanly is the leaf to apply.

Format follows the marketplace convention in [`../../../docs/best-practices/decision-trees-in-knowledge-files.md`](../../../docs/best-practices/decision-trees-in-knowledge-files.md): each tree carries a *When this applies* (observable), a `Last verified:` date, a Mermaid graph, per-leaf rationale, and a tradeoffs table.

---

## Decision Tree: Hypothesis tests — which test for this data + group structure

**When this applies:** The user asks "which test do I use / is this difference significant?" and you can observe (a) the **outcome variable's data type** (continuous / ordinal / nominal / count), (b) the **number of groups** being compared, and (c) whether observations are **paired/repeated or independent**. Not for "which model predicts Y" (see the regression tree) or "did X cause Y" (see the causal tree).

**Last verified:** 2026-05-30 against canonical biostatistics decision-tree sources (Statology; BioData Mining/Springer 2025) — see Provenance.

```mermaid
flowchart TD
  START([Comparing groups on an outcome]) --> DT{Outcome data type?}
  DT -->|Nominal / categorical| CHI{Expected cell counts all >= 5?}
  DT -->|Ordinal| ORD[Rank-based: Mann-Whitney 2 groups<br/>/ Kruskal-Wallis 3+ groups]
  DT -->|Continuous / numeric| NG{How many groups?}

  CHI -->|Yes| CHISQ[Chi-square test of independence]
  CHI -->|No / small cells| FISH[Fisher's exact test]

  NG -->|1 vs known value| ONE{Differences ~ normal?}
  NG -->|2 groups| TWO{Paired or independent?}
  NG -->|3+ groups| THREE{Repeated or independent?}

  ONE -->|Yes| ONET[One-sample t-test]
  ONE -->|No| ONEW[Wilcoxon signed-rank]

  TWO -->|Independent| TI{Normal per group + equal variance?}
  TWO -->|Paired| TP{Differences ~ normal?}
  TI -->|Yes, equal var| TT[Independent t-test]
  TI -->|Yes, unequal var| WELCH[Welch's t-test]
  TI -->|No / small n| MW[Mann-Whitney U]
  TP -->|Yes| PTT[Paired t-test]
  TP -->|No / small n| WSR[Wilcoxon signed-rank]

  THREE -->|Independent| AI{Assumptions OK?}
  THREE -->|Repeated| AR{Assumptions OK?}
  AI -->|Yes| ANOVA[One-way ANOVA + Tukey HSD post-hoc]
  AI -->|No| KW[Kruskal-Wallis + Dunn post-hoc]
  AR -->|Yes| RM[Repeated-measures ANOVA]
  AR -->|No| FRIED[Friedman test]
```

**Rationale per leaf:**
- *Chi-square / Fisher's exact* — categorical-vs-categorical association; Fisher's when any expected cell count < 5 (chi-square's approximation breaks).
- *Rank tests on ordinal* — ordinal data has order but not interval spacing, so means are undefined; rank-based tests are the honest choice.
- *One-sample t / Wilcoxon signed-rank* — comparing one sample to a fixed value; Wilcoxon when the differences aren't normal.
- *Independent t / Welch / Mann-Whitney* — two independent groups; Welch when variances differ (the safer default even then), Mann-Whitney when normality fails or n is small.
- *Paired t / Wilcoxon signed-rank* — two paired measurements; the test is on the within-pair differences.
- *ANOVA+Tukey / Kruskal-Wallis+Dunn* — 3+ independent groups via an omnibus test then a multiplicity-correcting post-hoc; **never a stack of pairwise t-tests** (inflates Type I error).
- *Repeated-measures ANOVA / Friedman* — 3+ repeated measurements on the same units; Friedman is the nonparametric fallback.

**Tradeoffs summary table:**

| Test | Outcome type | Groups | Assumption load | Use when |
|---|---|---|---|---|
| Chi-square / Fisher's | Nominal | 2+ | Expected cell counts ≥ 5 (else Fisher) | Association between two categorical variables |
| Mann-Whitney U | Ordinal / non-normal continuous | 2 indep. | Independence; similar shapes for a median-shift read | t-test assumptions fail, or ordinal data |
| Independent / Welch t-test | Continuous | 2 indep. | Normality per group (Welch relaxes equal variance) | Normal-ish continuous, two groups |
| Paired t / Wilcoxon signed-rank | Continuous | 2 paired | Normality of *differences* (Wilcoxon if not) | Before/after or matched pairs |
| ANOVA + Tukey / Kruskal-Wallis + Dunn | Continuous / ordinal | 3+ indep. | Normality + equal variance (KW if not) | 3+ groups — omnibus then corrected post-hoc |

> The full assumption gate (how to *check* normality/variance/independence) and the parametric↔nonparametric fallback table live in [`test-selection-decision-tree.md`](test-selection-decision-tree.md). This tree names the destination; that file gates the parametric leaves.

---

## Decision Tree: Parametric vs nonparametric — should I take the distribution-free route?

**When this applies:** You have *already* identified the candidate parametric test (from the tree above) and are deciding whether its assumptions hold well enough to use it, or whether to drop to the distribution-free counterpart. Observable inputs: the normality check result, the equal-variance check, the sample size, and whether a transformation is available/acceptable.

**Last verified:** 2026-05-30 against the assumption-gate + fallback canon in [`test-selection-decision-tree.md`](test-selection-decision-tree.md) (Sheffield APS 240; Statology) — see Provenance.

```mermaid
flowchart TD
  START([Candidate parametric test chosen]) --> N{Normality holds?<br/>Shapiro-Wilk n<=50 / D'Agostino; READ the Q-Q plot}
  N -->|Yes| V{Equal variance?<br/>Levene's / residual plot}
  N -->|No| BIGN{Large n AND only mild non-normality?}
  V -->|Yes| PARAM[Use the parametric test]
  V -->|No, normality OK| WELCHB[Welch variant — still parametric<br/>Welch t-test / Welch ANOVA]
  BIGN -->|Yes| CLT[Parametric defensible via CLT<br/>SHOW the Q-Q plot as the defense]
  BIGN -->|No| TRANS{Transformation fixes it?<br/>log / Box-Cox, then re-check}
  TRANS -->|Yes| RECHK[Transform, re-run the gate, use parametric on transformed scale]
  TRANS -->|No| NEED{Need a MEAN difference with a CI?}
  NEED -->|No — a location shift answers it| NONPAR[Nonparametric fallback<br/>Mann-Whitney / Wilcoxon / Kruskal-Wallis / Friedman / Spearman]
  NEED -->|Yes — stakeholder needs the mean| BOOT[Bootstrap CIs / robust SEs<br/>keeps the mean estimand]
```

**Rationale per leaf:**
- *Use the parametric test* — assumptions met; the parametric test is more powerful and gives the interpretable (mean-difference) estimand.
- *Welch variant* — unequal variance with normality intact does **not** require going nonparametric; Welch handles it and is a safe default even when variances look equal.
- *CLT-defensible* — at large n a t-test/ANOVA is robust to mild non-normality, but "robust" is a *defended* judgment shown with the Q-Q plot, not an excuse to skip the check.
- *Transform then re-check* — a log/Box-Cox transform often restores normality/homoscedasticity; re-run the gate on the transformed scale before trusting it.
- *Nonparametric fallback* — when normality fails, no transform fixes it, and a location-shift answer suffices; note rank tests test stochastic dominance / median shift, not a mean.
- *Bootstrap / robust SEs* — when the stakeholder genuinely needs a **mean** difference with a CI and no clean rank fallback fits (e.g. multi-predictor regression); distribution-free without changing the estimand.

**Tradeoffs summary table:**

| Route | Estimand | Power | Assumption cost | Use when |
|---|---|---|---|---|
| Parametric (t / ANOVA / OLS) | Mean difference + CI | Highest | Normality (+ equal var) | Gate passes, or large-n CLT with Q-Q shown |
| Welch variant | Mean difference + CI | High | Normality only (relaxes equal var) | Variances differ, normality OK |
| Transform → parametric | Mean on transformed scale | High | Transform must restore the gate | Skew/heteroscedasticity a log/Box-Cox fixes |
| Nonparametric (rank) | Median / stochastic dominance | Moderate | Independence; similar shapes | Normality fails, location-shift answer is enough |
| Bootstrap / robust SE | Original-scale mean + CI | Moderate–high | Independence (resampling valid) | Need the mean, no clean rank fallback |

---

## Decision Tree: Regression family — which model for this outcome

**When this applies:** The question is "what predicts / explains / models Y" and you can observe the **outcome's data type** (continuous / binary / proportion / count / time-to-event / ordinal) and its **dependence structure** (independent rows vs repeated/clustered). Choosing the model *family* — the prerequisite to fitting and then diagnosing it.

**Last verified:** 2026-05-30 against the GLM-family canon (McCullagh & Nelder) and the regression leaves of [`test-selection-decision-tree.md`](test-selection-decision-tree.md) — see Provenance.

```mermaid
flowchart TD
  START([Model Y from predictors]) --> CLUST{Repeated / clustered / nested observations?}
  CLUST -->|Yes| MIX[Mixed-effects model or GEE<br/>model the dependence]
  CLUST -->|No| TYPE{Outcome data type?}
  TYPE -->|Continuous, ~symmetric| OLS[Linear regression OLS]
  TYPE -->|Continuous, skewed/positive| SKEW[OLS on log y, or Gamma GLM]
  TYPE -->|Binary 0/1| LOGIT[Logistic regression]
  TYPE -->|Proportion / rate| PROP[Binomial or Beta GLM]
  TYPE -->|Ordinal categories| ORDL[Ordinal / proportional-odds logistic]
  TYPE -->|Count| CNT{Variance > mean? overdispersed?}
  TYPE -->|Time-to-event + censoring| SURV[Cox PH / Kaplan-Meier]
  CNT -->|No| POIS[Poisson GLM]
  CNT -->|Yes| NB[Negative-binomial GLM]
  CNT -->|Excess zeros| ZI[Zero-inflated / hurdle model]
```

**Rationale per leaf:**
- *Mixed-effects / GEE* — repeated or nested data violates independence; a random-effects (or GEE) structure models the within-cluster correlation so the SEs are honest.
- *OLS* — continuous, roughly symmetric outcome; the interpretable default *only* here.
- *Log-OLS / Gamma GLM* — positive, right-skewed continuous (spend, time); models multiplicative structure and keeps predictions positive.
- *Logistic* — binary outcome; keeps predicted probabilities in [0,1], which OLS cannot.
- *Binomial / Beta GLM* — proportions/rates bounded in [0,1] with their own variance structure.
- *Ordinal logistic* — ordered categories where you want covariate adjustment beyond a rank test.
- *Poisson → Negative-binomial → zero-inflated* — counts; Poisson assumes variance = mean, so check dispersion and escalate to NegBin when var ≫ mean, or a zero-inflated/hurdle model when zeros are excessive.
- *Cox / Kaplan-Meier* — time-to-event with censoring; standard regression mishandles the censored observations.

**Tradeoffs summary table:**

| Family | Outcome | Link / error | Key check | Use when |
|---|---|---|---|---|
| OLS | Continuous, symmetric | Identity / Normal | Residual diagnostics | Interpretable effect on a symmetric continuous Y |
| Logistic | Binary | Logit / Binomial | Separation, calibration | 0/1 outcome; want odds/probabilities |
| Poisson / Neg-binomial | Count | Log / Poisson(NB) | **Dispersion** (var vs mean) | Event counts; NB when overdispersed |
| Cox PH | Time-to-event | Hazard | Proportional-hazards assumption | Survival/churn timing with censoring |
| Mixed-effects / GEE | Any, repeated/nested | Varies | Variance components / cluster count | Repeated measures, hierarchical data |

> Once the family is chosen, run the diagnostics before trusting coefficients — see [`../best-practices/regression-run-the-diagnostics-before-trusting-coefficients.md`](../best-practices/regression-run-the-diagnostics-before-trusting-coefficients.md).

---

## Decision Tree: Causal inference — which identification strategy

**When this applies:** A **causal** claim is warranted ("does X *cause / drive / impact* Y?", and the causal-verb check in [`../best-practices/causal-correlation-is-not-causation.md`](../best-practices/causal-correlation-is-not-causation.md) passed). You can observe what **natural variation** the situation offers: can you randomize? is there a before/after on treated + untreated groups? a sharp assignment cutoff? a valid instrument? only observational treated/untreated units?

**Last verified:** 2026-05-30 against the causal toolkit in [`causal-inference-primer.md`](causal-inference-primer.md) (textbook consensus; Hernán & Robins) — see Provenance.

```mermaid
flowchart TD
  START([Causal claim warranted]) --> RAND{Can you randomize the intervention?}
  RAND -->|Yes| RCT[Randomized experiment A/B<br/>gold standard — sidesteps all 3 threats]
  RAND -->|No| VAR{What natural variation exists?}
  VAR -->|Treatment hit one group at a known time;<br/>before/after on treated + untreated| DID[Difference-in-Differences<br/>requires: parallel trends]
  VAR -->|Treatment assigned by a sharp cutoff<br/>on a running variable| RDD[Regression Discontinuity<br/>local effect near the cutoff only]
  VAR -->|A variable shifts treatment<br/>but not the outcome directly| IV[Instrumental Variables 2SLS<br/>requires: a valid, defensible instrument]
  VAR -->|Just observational treated vs untreated| MATCH[Matching / propensity scores<br/>balances OBSERVED confounders only]
```

**Rationale per leaf:**
- *Randomized experiment* — randomization makes treated and untreated groups exchangeable, so it sidesteps confounding, selection, and reverse causation at once; prefer it whenever feasible.
- *Difference-in-Differences* — uses an untreated group's trajectory as the counterfactual for the treated group; identifies the effect *if* the two would have moved in parallel absent treatment (the load-bearing, partly-checkable assumption).
- *Regression Discontinuity* — units just above vs just below a sharp cutoff are comparable, so the cutoff acts like local randomization; estimates a **local** effect near the threshold only.
- *Instrumental Variables (2SLS)* — an instrument that moves treatment but affects the outcome only *through* treatment isolates exogenous variation; valid instruments are rare and the exclusion restriction is untestable.
- *Matching / propensity scores* — builds comparable treated/untreated groups on observed covariates; **cannot** fix unobserved confounding — always flag that residual risk.

**Tradeoffs summary table:**

| Design | Key assumption | Effect estimated | Defensibility | Use when |
|---|---|---|---|---|
| Randomized experiment | Successful randomization | Average treatment effect | Highest | You can assign the intervention |
| Difference-in-Differences | Parallel trends | ATT (treated group) | High, communicable | Known treatment time + untreated comparison |
| Matching / propensity | No *unobserved* confounding | ATT/ATE on overlap | Medium — unobserved bias bites | Observational, rich observed covariates |
| Instrumental Variables | Valid + exclusion-restricted instrument | LATE (compliers) | Lower — strong, untestable assumptions | A credible natural instrument exists |
| Regression Discontinuity | Continuity at the cutoff | Local effect at cutoff | High *locally* | Sharp assignment rule on a running variable |

> IV / panel estimation uses `linearmodels` (Tier 2). Design selection is the destination; covariate selection *within* the design follows [`../best-practices/causal-watch-confounders-and-colliders.md`](../best-practices/causal-watch-confounders-and-colliders.md).

---

## Decision Tree: Time-series model — which forecasting model

**When this applies:** You are forecasting or modelling a **time-ordered** metric and have run the stationarity + autocorrelation gate ([`../best-practices/timeseries-test-stationarity-and-autocorrelation.md`](../best-practices/timeseries-test-stationarity-and-autocorrelation.md)). Observable inputs: is there a trend? clear seasonality? are there exogenous predictors? is the series stationary after differencing?

**Last verified:** 2026-05-30 against Box-Jenkins / `statsmodels.tsa` canon — see Provenance.

```mermaid
flowchart TD
  START([Forecast a time-ordered metric]) --> STAT{Stationary? ADF + KPSS read together}
  STAT -->|Non-stationary| DIFF[Difference / detrend / log-stabilize first]
  STAT -->|Stationary, or after differencing| EXOG{Exogenous predictors / known drivers?}
  DIFF --> EXOG
  EXOG -->|Yes| REGARMA[Regression with ARMA errors / SARIMAX with exog<br/>or a causal interrupted-time-series for a known event]
  EXOG -->|No| SEAS{Clear seasonality?}
  SEAS -->|Yes| SEASM{Few clean seasonal components vs complex?}
  SEAS -->|No| TREND{Trend present?}
  SEASM -->|Clean level/trend/season| ETS_S[Holt-Winters / seasonal ETS]
  SEASM -->|Complex / autocorrelated| SARIMA[SARIMA]
  TREND -->|Yes| ETS_T[Holt's linear trend / ARIMA with d>=1]
  TREND -->|No, stationary| ARMA[ARIMA p,0,q — read orders from ACF/PACF]
```

**Rationale per leaf:**
- *Difference / detrend first* — a non-stationary series produces spurious regressions and a model that won't generalize; difference (d) / detrend / log-stabilize until ADF+KPSS agree it's stationary.
- *Regression with ARMA errors / SARIMAX-with-exog* — when known drivers explain the series; model the mean with predictors and the residual autocorrelation with ARMA. A known one-time event → interrupted time series.
- *Holt-Winters / seasonal ETS* — clean, interpretable level/trend/seasonality; fast and a strong baseline.
- *SARIMA* — seasonality plus residual autocorrelation that ETS doesn't capture; orders read from ACF/PACF, residuals confirmed white-noise via Ljung-Box.
- *Holt's linear trend / ARIMA(d≥1)* — trend without strong seasonality.
- *ARIMA(p,0,q)* — already-stationary series; identify AR/MA orders from ACF/PACF.

**Tradeoffs summary table:**

| Model | Captures | Needs | Interpretability | Use when |
|---|---|---|---|---|
| ARIMA(p,d,q) | Autocorrelation + trend (via d) | Stationarity after differencing | Medium | Trended/autocorrelated, no strong seasonality |
| SARIMA | Seasonality + autocorrelation | Stationarity; ACF/PACF orders | Medium | Seasonal + residual autocorrelation |
| Holt-Winters / ETS | Level + trend + seasonality | Clean components | High | Clear seasonal pattern, strong baseline wanted |
| Regression + ARMA errors / SARIMAX | Exogenous drivers + serial dep. | Valid predictors | High (driver coefficients) | Known drivers explain the series |
| Interrupted time series | Effect of a known event | Dated intervention | High | A one-time change at a known date (causal seam) |

> Every forecast ships **with a prediction interval**, never a bare point line, and validation is **temporal** (rolling-origin) — never shuffle (pitfall #9). ETS/ARIMA/SARIMAX live in `statsmodels.tsa` (Tier 1).

---

## Decision Tree: A/B test analysis — complete the experiment correctly

**When this applies:** an A/B test has finished collecting data (or has reached its pre-specified stopping rule) and the results are being analyzed. Observable inputs: whether the primary metric is pre-registered, whether peeking has occurred, whether guardrail metrics moved, and whether multiple segments were analyzed.

**Last verified:** 2026-06-05 against `skills/experiment-analysis/SKILL.md` and `knowledge/experiment-design-and-ab-testing.md`.

```mermaid
flowchart TD
    START[A/B test data ready to analyze] --> Q1{Was the primary metric pre-registered?}
    Q1 -->|NO| PREREG[Label as exploratory - pre-register the metric before the next experiment]
    Q1 -->|YES| Q2{Did peeking occur - was significance checked before the stopping rule?}
    Q2 -->|YES - peeked and stopped early| PEEK[Result is biased - report as directional only - rerun with sequential test or CUPED]
    Q2 -->|NO - ran to the stopping rule| Q3{Does the primary metric pass the significance threshold?}
    Q3 -->|YES significant| Q4{Did any guardrail metric move significantly?}
    Q4 -->|YES guardrail breached| GUARD[Do NOT ship - guardrail breach blocks the win]
    Q4 -->|NO guardrails clean| Q5{Was segment analysis run?}
    Q5 -->|YES without correction| SEGCORR[Apply BH-FDR correction to segment p-values before reporting]
    Q5 -->|YES with correction or NO| REPORT[Report: effect size + CI + guardrail status + segments if any]
    Q3 -->|NO not significant| NULL[Report null result with power + MDE - not no effect]
    PREREG --> REPORT_EXP[Report as exploratory - no confirmatory claim]
```

**Rationale per leaf:**
- *PREREG* — an unregistered primary is an exploratory result by definition; report it as such and pre-register for the next experiment.
- *PEEK* — peeking inflates Type I error; a result from an early-stopped fixed-horizon test should be reported as directional, not confirmatory. The fix for future tests is sequential testing (sequential p-values, always-valid p, or CUPED).
- *GUARD* — a guardrail breach means the treatment harms another metric; the "win" on the primary is a net negative. Do not ship.
- *SEGCORR* — multiple segment comparisons require FDR correction; uncorrected segment p-values are hypothesis-generating, not confirmatory.
- *REPORT* — a clean, pre-registered, peeking-free, guardrail-passing result is a confirmatory win; report effect size + CI as the headline.
- *NULL* — a null result is informative only if the power and MDE are reported; a null from an underpowered study is uninformative.

**Tradeoffs summary:**

| Situation | Result status | Action |
|---|---|---|
| Pre-registered, no peeking, guardrails clean | Confirmatory | Ship if practical significance met |
| Peeked and stopped early | Directional only | Do not claim; rerun with sequential design |
| Guardrail breached | Blocked win | Investigate the guardrail harm |
| No pre-registration | Exploratory | Pre-register before next experiment |
| Null result | Inconclusive | Report power + MDE; expand n if effect is meaningful |

---

## Decision Tree: Sample size calculator — which formula applies?

**When this applies:** a new study (A/B test, survey, observational analysis) needs a sample size estimate before data collection begins. Observable inputs: the test type (means, proportions, regression), the effect metric (absolute or relative lift, Cohen's d/h/f), the desired power, and whether the study is one-sided or two-sided.

**Last verified:** 2026-06-05 against `skills/power-and-sample-size/SKILL.md` and statsmodels docs.

```mermaid
flowchart TD
    START[Need a sample size estimate] --> Q1{What type of outcome?}
    Q1 -->|Continuous mean - t-test| MEANS[TTestIndPower or TTestPower - effect size is Cohens d]
    Q1 -->|Proportion - conversion rate| PROPS[NormalIndPower or zt_ind_solve_power - effect size is Cohens h]
    Q1 -->|Count - rate or Poisson| RATES[Poisson power - or normal approximation if rate is large]
    Q1 -->|Regression R-squared or f2| REG[FTestAnovaPower - effect size is f-squared]
    MEANS --> SIDED{One-sided or two-sided?}
    PROPS --> SIDED
    RATES --> SIDED
    REG --> INPUTS[Set alpha=0.05 power=0.80 unless overridden - document the override reason]
    SIDED -->|Two-sided default| COMPUTE[Compute n per group - multiply by number of groups]
    SIDED -->|One-sided with justification| COMPUTE
    COMPUTE --> FEASIBLE{Is the required n feasible in the time window?}
    FEASIBLE -->|NO - n too large| TRADEOFF[Increase MDE or accept lower power - document the decision]
    FEASIBLE -->|YES| PREREGISTER[Record in design doc before any data is collected]
```

**Rationale per leaf:**
- *MEANS* — `TTestIndPower` from statsmodels is the standard for comparing two independent group means; effect size is Cohen's d (mean difference / pooled SD).
- *PROPS* — conversion rates and proportions use `zt_ind_solve_power` or `NormalIndPower`; effect size is Cohen's h (arcsine transformation of the rate difference).
- *RATES* — count/rate outcomes (events per user) use a Poisson power approximation; at large rates, the normal approximation is acceptable.
- *REG* — for regression, effect size is f-squared = R-squared / (1 - R-squared); use `FTestAnovaPower`.
- *TWO-SIDED* — the default; one-sided tests require a pre-registered directional hypothesis and a written justification — they are not a way to reduce sample size without cause.
- *FEASIBLE* — if the required n exceeds what is available in the time window, the tradeoff is transparent: increase the MDE (detect only larger effects) or accept reduced power. Document the decision; do not silently run an underpowered study.
- *PREREGISTER* — the sample size is fixed before data collection; computing it post-hoc to justify a result is circular.

**Tradeoffs summary:**

| Outcome type | statsmodels function | Effect size metric | Default settings |
|---|---|---|---|
| Continuous means | `TTestIndPower` | Cohen's d | alpha=0.05, power=0.80, two-sided |
| Proportions | `zt_ind_solve_power` | Cohen's h | alpha=0.05, power=0.80, two-sided |
| Count/rate | `zt_ind_solve_power` (approx) | Relative rate change | alpha=0.05, power=0.80 |
| Regression F-test | `FTestAnovaPower` | f-squared = R2/(1-R2) | alpha=0.05, power=0.80 |

---

## Decision Tree: Missing data — which imputation or exclusion strategy?

**When this applies:** a dataset has missing values and you must decide whether to exclude, impute, or use a model-based approach. Observable inputs: the missingness mechanism (MCAR, MAR, or MNAR), the percentage of missing values, and whether the analysis is predictive or inferential.

**Last verified:** 2026-06-05 against `best-practices/data-handle-missingness-by-its-mechanism.md` and `knowledge/statistical-pitfalls.md`.

```mermaid
flowchart TD
    START[Missing values in the dataset] --> Q1{What is the missingness mechanism?}
    Q1 -->|MCAR - completely random - test with Little MCAR| MCAR_N{What percent missing?}
    Q1 -->|MAR - depends on observed data| MAR_N{What percent missing?}
    Q1 -->|MNAR - depends on unobserved - the hard case| MNAR[Sensitivity analysis required - no clean fix exists]
    MCAR_N -->|Under 5 percent| LISTWISE[Listwise deletion OK - small bias risk]
    MCAR_N -->|5 to 20 percent| SINGLE[Single imputation mean/median acceptable with SE correction]
    MCAR_N -->|Over 20 percent| MICE[Multiple imputation by chained equations MICE]
    MAR_N -->|Under 5 percent| LISTWISE
    MAR_N -->|Over 5 percent| MICE
    MNAR --> MNAR_PATHS[Model the missingness OR bound the estimate OR collect the missing data]
    MICE --> POOL[Pool results across M=5-20 imputed datasets - Rubins rules]
    LISTWISE --> VERIFY[Verify: compare missers vs non-missers on key covariates]
    SINGLE --> VERIFY
```

**Rationale per leaf:**
- *LISTWISE* — for MCAR with under 5% missing, listwise deletion introduces negligible bias and is the simplest option; still verify that missers and non-missers look similar on key variables.
- *SINGLE IMPUTATION* — mean/median imputation underestimates variance and correlations; acceptable only for small MCAR gaps with a standard-error correction in the model.
- *MICE* — the standard method for MAR data and for moderate-to-large MCAR gaps; creates M complete datasets, runs the analysis on each, and pools with Rubin's rules; preserves the uncertainty from imputation.
- *MNAR* — no imputation method fixes MNAR; the options are to model the missingness process explicitly, to bound the estimate (worst-case / best-case sensitivity), or to go back and collect the missing data. Report the sensitivity analysis.
- *POOL* — MICE results must be pooled (Rubin's rules) across imputed datasets to get correct standard errors; using a single imputed dataset throws away the MICE uncertainty estimate.

**Tradeoffs summary:**

| Method | Mechanism it handles | Bias | SE correct | Use when |
|---|---|---|---|---|
| Listwise deletion | MCAR only | Low (MCAR small) | Yes | MCAR + under 5% missing |
| Single imputation | MCAR only | Underestimates variance | No (SE too small) | MCAR + small gap + correction applied |
| MICE | MCAR / MAR | Low | Yes (pooled) | MAR or MCAR + over 5% missing |
| Model missingness | MNAR | Depends on model | Depends | MNAR - no clean alternative |
| Sensitivity bounds | MNAR | Bounds the bias | n/a | MNAR when modelling is infeasible |

---

## Provenance

- **Hypothesis-test tree + parametric/nonparametric tree** — topology and pairings from Statology, "Choosing the Right Statistical Test: A Decision Tree Approach" (retrieved 2026-05-26); BioData Mining/Springer, "A simple guide to ... t-test, Mann-Whitney U, Chi-squared, and Kruskal-Wallis" (2025); assumption gate + fallbacks from Sheffield APS 240 "Non-parametric tests" — consolidated in [`test-selection-decision-tree.md`](test-selection-decision-tree.md) (Tier 1 / consensus).
- **Regression-family tree** — GLM family/link selection by outcome type: McCullagh & Nelder, *Generalized Linear Models*; overdispersion → negative-binomial and zero-inflation are canonical count-model guidance; the OLS/logistic/Poisson/survival leaves mirror [`test-selection-decision-tree.md`](test-selection-decision-tree.md).
- **Causal-inference tree** — RCT > DiD/matching > IV/RDD framing and each design's key assumption from [`causal-inference-primer.md`](causal-inference-primer.md) (textbook consensus; Hernán & Robins, *Causal Inference: What If*) — Tier 2 (strong-but-contextual).
- **Time-series tree** — Box-Jenkins ARIMA/SARIMA identification (ACF/PACF, Ljung-Box residual check) and ETS/Holt-Winters; ADF+KPSS read-together (opposite nulls) is standard practice; Hamilton, *Time Series Analysis*. Implemented in `statsmodels.tsa` per [`statistics-tooling-2026.md`](statistics-tooling-2026.md).
- Refresh trigger: re-verify a tree if a future engagement surfaces a method it doesn't cover (mixed models beyond a primer, staggered-adoption DiD, state-space/Prophet-style forecasting). Per the marketplace staleness convention, the Researcher meta-skill flags any `Last verified:` older than 90 days.
