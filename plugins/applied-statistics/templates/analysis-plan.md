# Analysis plan (pre-registration) — <experiment / analysis name>

> Fill this in **before** collecting or looking at the data. A written, dated plan
> is the structural defense against p-hacking and peeking (pitfalls #1, #3). Commit
> it before launch; deviations afterward are labeled exploratory.

**Author:** <name> · **Date pre-registered:** <YYYY-MM-DD> · **Decision this informs:** <what ships/changes based on the result>

## 1. Hypothesis
- **Question:** <plain-language question>
- **Directional hypothesis:** <Variant B increases <primary metric> vs control>
- **Null hypothesis:** <no difference>

## 2. Metrics
- **Primary metric (one):** <definition + how computed>
- **Guardrail metrics (must not break):** <latency / churn / revenue-per-user / error rate …>
- **Secondary / exploratory metrics:** <labeled exploratory — not decision-grade>

## 3. Design
- **Unit of randomization:** <user / account / cluster — must match unit of independence>
- **Assignment:** <50/50 / other; mechanism>
- **Population / eligibility:** <who is in>
- **Planned duration / sample size:** n = <…> per group (from the power analysis below)

## 4. Statistical analysis (decided up front)
- **Primary test:** <test from the decision tree> · **assumption checks:** <normality/variance/independence>
- **Effect size + CI to report:** <e.g., rate difference + 95% Wilson CI>
- **α:** 0.05 · **power:** 0.80 · **MDE:** <smallest effect worth acting on>
- **Multiple-comparison correction:** <Holm/Bonferroni (confirmatory) or Benjamini-Hochberg (exploratory)> across <# metrics/segments>
- **Stopping rule:** <fixed horizon at planned n> OR <valid sequential method — name it>
- **Pre-specified segments:** <list; anything not listed is exploratory>

## 5. What would change the decision
- **Ship if:** <primary effect ≥ MDE, CI excludes the no-go region, guardrails intact>
- **Don't ship if:** <…>
- **Inconclusive (underpowered) if:** <CI too wide to decide — report the MDE the study could detect>

## 6. Deviations log (filled in after)
- <date — what changed from this plan and why; mark affected results exploratory>
