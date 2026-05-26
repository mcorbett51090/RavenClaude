# Knowledge — Statistical pitfalls (the guardrail)

> **Last reviewed:** 2026-05-26 · **Confidence:** High (each pitfall and its fix are well-documented; see Provenance).
> This is the highest-value file in the plugin — the "statistician in the room" checklist. The `applied-statistician` agent runs an analysis or a claim against this list before endorsing it, and the advisory hook [`../hooks/flag-statistical-smells.sh`](../hooks/flag-statistical-smells.sh) catches the mechanically-detectable subset.

A finding is only as trustworthy as the process that produced it. These nine pitfalls are the ones that turn a real-looking number into an artifact.

---

## The nine pitfalls

| # | Pitfall | Symptom (what to watch for) | Fix |
|---|---|---|---|
| 1 | **p-hacking / data dredging** | Many tests run, only "significant" ones reported; analysis decisions (which subgroup, which cutoff, which covariates) made *after* seeing the data | Pre-register the analysis plan ([`../templates/analysis-plan.md`](../templates/analysis-plan.md)); report **all** tests run; label confirmatory vs exploratory |
| 2 | **Multiple comparisons** | Many simultaneous tests/metrics/segments; some p < 0.05 by chance alone (20 tests at α=0.05 ≈ 1 false positive expected) | Correct: **Bonferroni/Holm (FWER)** for confirmatory, **Benjamini-Hochberg (FDR)** for exploratory/screening — see below |
| 3 | **Peeking / optional stopping** | Repeatedly checking a running A/B test and stopping the moment it hits significance | Fix the sample size up front (power analysis), **or** use a valid sequential method (always-valid CIs / mSPRT). Naïve peeking massively inflates false positives |
| 4 | **Simpson's paradox** | An aggregate trend reverses (or vanishes) inside subgroups | Stratify by the lurking variable; don't trust a pooled rate when group sizes/mixes differ |
| 5 | **Base-rate neglect** | Reading a "significant"/"positive" result without the prior prevalence (classic with screening tests) | Apply Bayes' rule; report **PPV given the base rate**, not just sensitivity/specificity |
| 6 | **Significance ≠ effect size** | p-value reported with no magnitude; "highly significant" on huge n where the effect is trivial | Always report **effect size + confidence interval** alongside p; ask "is it big enough to matter to the business?" |
| 7 | **Assumption violations** | Skewed / heteroscedastic / non-independent data pushed through a t-test or OLS unchecked | Check assumptions ([`test-selection-decision-tree.md`](test-selection-decision-tree.md)); use the nonparametric fallback, transform, robust SEs, or bootstrap |
| 8 | **Underpowered study** | Small n, null result reported as "no effect" / "no difference" | A-priori power analysis ([`../skills/power-and-sample-size/SKILL.md`](../skills/power-and-sample-size/SKILL.md)); **"absence of evidence ≠ evidence of absence"** — report the CI and the MDE the study could detect |
| 9 | **Data leakage** | A model uses information unavailable at prediction time; train/test contamination; fitting transforms on the full dataset | Strict temporal/group splits; fit scalers/encoders on **train only**; for time series, never shuffle |

---

## Multiple-comparison correction: FWER vs FDR (pitfall #2, expanded)

The two correction families control different things and are **not interchangeable**:

- **Family-Wise Error Rate (FWER)** — the probability of **any** false positive among the family of tests. Controlled by **Bonferroni** (divide α by the number of tests) or, less conservatively, **Holm**. Use for **confirmatory** work where a single false positive is costly (a launch decision, a medical claim).
- **False Discovery Rate (FDR)** — the expected **proportion** of false positives among the rejections. Controlled by **Benjamini-Hochberg**. More powerful; use for **exploratory / screening** work where you'll follow up on the hits anyway (which of 200 features look promising).

Rule of thumb: *confirmatory → FWER (Holm ≥ Bonferroni for power), exploratory → FDR (Benjamini-Hochberg).* Note FDR is not a universal drop-in for Bonferroni — pick the one that matches the cost of a false positive in the decision at hand.

---

## How the agent uses this file

1. Before endorsing any "X is significant / X went up / X drives Y" claim, walk the table and ask which pitfalls the analysis is exposed to.
2. For experiments specifically, pitfalls #1, #2, #3, #6, #8 are the load-bearing ones — see [`experiment-design-and-ab-testing.md`](experiment-design-and-ab-testing.md).
3. State the caveat plainly in the report (the `applied-statistician` Output Contract requires a "caveats / assumptions checked" line).

---

## Provenance

- FWER vs FDR (Bonferroni controls FWER; Benjamini-Hochberg controls FDR): Statsig, "Controlling your type I errors: Bonferroni and Benjamini-Hochberg" (retrieved 2026-05-26); MetricGate, "Bonferroni vs. Holm vs. FDR Compared" (retrieved 2026-05-26). Caveat that FDR is not always a drop-in for Bonferroni: Journal of Clinical Epidemiology letter S0895-4356(15)00301-7.
- Peeking / optional stopping invalidates fixed-horizon p-values: Johari et al., "Always Valid Inference" (arXiv:1512.04922) — see [`experiment-design-and-ab-testing.md`](experiment-design-and-ab-testing.md).
- Tier 1 (consensus). Refresh trigger: revisit if a new correction method or a peeking-correction standard becomes dominant.
