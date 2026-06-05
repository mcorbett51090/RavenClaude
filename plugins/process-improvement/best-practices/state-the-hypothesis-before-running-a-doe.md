# State the Hypothesis Before Running a DOE

**Status:** Absolute rule
**Domain:** Process Improvement — Analyze / Improve (DOE)
**Applies to:** `process-improvement`

---

## Why this exists

A Design of Experiments (DOE) generates data that can confirm or refute a hypothesis about which input factors drive output variation. When a team runs a DOE without a pre-stated hypothesis — the expected direction and magnitude of each factor's effect — the analysis becomes a fishing expedition. Fishing expeditions in multi-factor data are statistically hazardous: enough factors and enough effects, and spurious significance appears by chance. Pre-stating the hypothesis makes the test confirmatory, not exploratory, and forces the team to articulate *why* they think each factor matters before the data exists.

## How to apply

**Pre-DOE hypothesis register (complete before the experiment runs):**

| Factor | Hypothesis | Expected direction | Expected effect size (order of magnitude) | Basis (fishbone / expert opinion / literature) |
|---|---|---|---|---|
| Temperature | Increasing temperature increases defect rate at the sealing step | Positive | ~2× rate per 10°C | Fishbone Analyze-phase finding |
| Operator | Operator training level affects defect rate | Positive (higher training = lower rate) | 30–40% reduction | Pareto analysis: operators split by tenure |

**Steps:**
1. Write the hypothesis register before designing the experiment.
2. Use the hypothesized factors (and their expected ranges) to design the DOE (full factorial vs fractional, center points, replication level).
3. Route the DOE design and the statistical analysis to `applied-statistics` — this plugin owns the *framing*; applied-statistics owns the *math*.
4. Compare actual results to the pre-stated hypotheses; document confirmations and surprises.

**Do:**
- List "null hypothesis: no effect" explicitly for control factors included as a check.
- Distinguish between factors you expect to *control* vs factors you expect to *quantify* (noise vs signal).
- Archive the pre-experiment hypotheses and compare them to post-experiment results in the project record.

**Don't:**
- Reverse-engineer a hypothesis from the DOE results to make the write-up look confirmatory.
- Include more factors than the experiment is powered to detect (the minimum detectable effect determines the replication requirement — route this calculation to `applied-statistics`).
- Run the DOE on the current (unimproved) process to "explore" without a specific Analyze-phase question driving it.

## Edge cases / when the rule does NOT apply

- **Screening DOEs** are genuinely exploratory — the hypothesis register still exists, but it lists all plausible factors rather than a narrow confirmatory set. The analysis must apply an appropriate multiplicity correction (route to `applied-statistics`).
- **Historical data re-analysis** (not a designed experiment): label it as observational, acknowledge confounders, and route to `applied-statistics` for the appropriate analysis — do not call it a DOE.

## See also

- [`../agents/lean-six-sigma-blackbelt.md`](../agents/lean-six-sigma-blackbelt.md) — frames the DOE hypothesis and routes the math
- [`./prove-root-cause-with-data-before-improving.md`](./prove-root-cause-with-data-before-improving.md) — the upstream rule that generates the candidate factors for the DOE

## Provenance

Standard DOE practice requiring a priori hypothesis specification (Montgomery, "Design and Analysis of Experiments"; AIAG PPAP; NIST Engineering Statistics Handbook). Codifies the `CLAUDE.md` §5 statistics seam: this plugin frames the question; `applied-statistics` runs and defends the math. _Last verified: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_
