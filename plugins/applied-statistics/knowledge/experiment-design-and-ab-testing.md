# Knowledge — Experiment & A/B-test design

> **Last reviewed:** 2026-05-26 · **Confidence:** High on the settled spine; **Medium** on the sequential-testing frontier (vendor methods evolve — verify before quoting).
> Covers designing and analyzing an experiment so the result is defensible. The spine is consensus; the sequential-testing section is an active methodological frontier and is flagged as such.

---

## The settled spine (Tier 1 — consensus)

Design the experiment **before** you collect data, in this order:

1. **One primary metric.** Pick the single metric the decision hinges on. Everything else is secondary.
2. **Guardrail metrics.** The things you must *not* break while moving the primary (latency, error rate, churn, revenue-per-user). A "win" that tanks a guardrail is not a win.
3. **Directional hypothesis.** "Variant B increases <primary> vs control" — stated before launch.
4. **Sample size from power + MDE.** Compute n up front from:
   - **α = 0.05** (significance level — tolerated false-positive rate), conventional.
   - **power = 0.80** (probability of detecting a true effect of the target size), Cohen's (1988) convention.
   - **MDE** (minimum detectable effect) — the smallest effect worth acting on. If no pilot exists, anchor with Cohen's effect-size conventions (d = 0.2 / 0.5 / 0.8 = small / medium / large) but prefer a business-meaningful MDE. See [`../skills/power-and-sample-size/SKILL.md`](../skills/power-and-sample-size/SKILL.md).
5. **Randomization unit = unit of independence.** Randomize at the **user** level (not session/pageview) when users return — otherwise repeated observations from one user violate independence and shrink your effective sample.
6. **Pre-register the analysis plan.** Metric, test, segments, stopping rule, and correction — written down before seeing data ([`../templates/analysis-plan.md`](../templates/analysis-plan.md)). This is the *structural* defense against p-hacking (pitfall #1) and peeking (pitfall #3).

**Analysis (after the planned sample is in):** run the pre-registered test, **report effect size + confidence interval** (not just the p-value), check guardrails, and apply a multiple-comparison correction if you tested several metrics/segments ([`statistical-pitfalls.md`](statistical-pitfalls.md)).

---

## Fixed-horizon vs sequential (Tier 3 — divergent; verify before quoting)

The single most common experiment mistake is **peeking**: watching a running test and stopping when it crosses significance. With a fixed-horizon frequentist test, that inflates the false-positive rate far above α.

- **Fixed-horizon** is the simplest correct option: pick n from the power analysis, **do not look at significance until n is reached.** Recommend this whenever the business can wait.
- **Sequential / always-valid testing** is the principled way to peek/stop early. The foundational method is the **mixture Sequential Probability Ratio Test (mSPRT) / always-valid p-values** (Johari et al., arXiv:1512.04922).

> ⚠️ **Vendor methods diverge and change — verify against current vendor docs before quoting to a client.** As of early-2026 secondary sources: Optimizely / Uber / Netflix / Amplitude were associated with **mSPRT**, Statsig with a **corrected-alpha approach (CAA)**, and Eppo with **generalized always-valid inference (GAVI)**. Treat these attributions as *directional, retrieval-dated (2026-05-26), and worth re-checking* — not as settled fact. The point for a client is: *if you want to peek, you need a method built for it; don't peek at a fixed-horizon test.*

---

## When Bayesian A/B is preferred (Tier 2 — strong-but-contextual)

Reach for a Bayesian A/B framework when:

- Stakeholders want a directly interpretable **"probability B beats A"** and an expected-loss / decision rule, rather than a p-value.
- You have **informative priors** worth encoding.
- **Sample sizes are small** and the frequentist large-sample approximations are shaky.

> ⚠️ **Nuance — do not state flatly that "Bayesian avoids the peeking penalty."** Bayesian decision rules don't incur the *frequentist* peeking penalty in the same way, but Bayesian sequential analysis has its own stopping-rule subtleties. Frame it as "different failure modes," not "immune."

For SMB consulting, **frequentist is the spine** (clients understand p-values and the α/power conventions; tooling is fast). Bayesian is a Tier-2 differentiation play — see PyMC / bambi in [`statistics-tooling-2026.md`](statistics-tooling-2026.md).

---

## Provenance

- α = 0.05 / power = 0.80 conventions: Meera (Univ. of Michigan), "Power Analysis, Statistical Significance & Effect Size" (retrieved 2026-05-26); Statistics Solutions, "Components of Power Analysis" (retrieved 2026-05-26).
- Cohen effect-size conventions (d = 0.2/0.5/0.8): PMC6736231, "Effect Size Guidelines, Sample Size Calculations, and Statistical Power in Gerontology" (retrieved 2026-05-26).
- Sequential / always-valid inference (mSPRT): Johari et al., arXiv:1512.04922 (retrieved 2026-05-26). Vendor-method attributions (mSPRT/CAA/GAVI): Statsig, "Sequential Testing on Statsig" (retrieved 2026-05-26); Spotify Engineering, "Choosing a Sequential Testing Framework" (2023) — confirms the framework choice is contested. **Re-verify vendor methods before quoting.**
- Tier 1 spine / Tier 3 sequential frontier per the 2026-05-26 research brief. Refresh trigger: re-verify the sequential-testing vendor landscape quarterly.
