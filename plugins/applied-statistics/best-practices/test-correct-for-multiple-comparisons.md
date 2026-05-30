# Correct for multiple comparisons — pick FWER or FDR by the cost of a false positive

**Status:** Absolute rule
**Domain:** Hypothesis testing / multiplicity
**Applies to:** `applied-statistics`

---

## Why this exists

Run twenty independent tests at α=0.05 and you expect roughly one "significant" result by chance alone, even when nothing is real (pitfall #2). The moment an analysis tests several metrics, several segments, several time windows, or several arms, the per-test α no longer controls the chance of *any* false positive across the family — and the un-corrected "winner" is frequently noise dressed as signal. The fix is not optional and it is not one-size: the two correction families control *different* error rates and are **not interchangeable**. Choosing the wrong one either bleeds power (Bonferroni on a 200-feature screen) or under-protects a launch decision (FDR where a single false positive is costly). The agent's job is to name which family the decision needs *and* apply it before calling any one result significant.

## How to apply

Count the family of tests, then pick the family of correction by the cost of a single false positive:

```
Confirmatory work (a launch / medical / contract decision; one false positive is costly)
  -> control the FAMILY-WISE ERROR RATE (FWER)
     Holm   (uniformly more powerful than Bonferroni — prefer it)
     Bonferroni  (divide α by #tests — simplest, most conservative)

Exploratory / screening (which of 200 features look promising; you'll follow up the hits)
  -> control the FALSE DISCOVERY RATE (FDR)
     Benjamini-Hochberg   (more powerful; tolerates a known proportion of false hits)

# Tier-1 tooling
from statsmodels.stats.multitest import multipletests
reject, p_corr, *_ = multipletests(pvals, alpha=0.05, method='holm')   # or 'fdr_bh'
```

**Do:**
- Decide FWER vs FDR by the decision's cost of a false positive — confirmatory → FWER (Holm ≥ Bonferroni for power), exploratory → FDR (Benjamini-Hochberg).
- Count *every* test in the family — secondary metrics, segments, interim looks, and post-hoc pairwise comparisons all count.
- For 3+ group comparisons, use the omnibus test (ANOVA/Kruskal-Wallis) then a multiplicity-correcting post-hoc (Tukey/Dunn) rather than raw pairwise tests.

**Don't:**
- Report the one p < 0.05 out of many without disclosing how many tests were run.
- Treat FDR as a universal drop-in for Bonferroni — it controls a *proportion*, not the probability of any error; pick the one that matches the decision [rule of thumb: confirmatory→FWER, exploratory→FDR].
- Correct after the fact to rescue a result — the family is defined by the analysis plan, not by which tests turned out significant.

## Edge cases / when the rule does NOT apply

- **A single pre-registered primary metric** needs no multiplicity correction — that is the whole point of designating one primary. Secondary/guardrail metrics still do.
- **Strongly correlated tests** make Bonferroni over-conservative; permutation-based or hierarchical corrections recover power — name the upgrade rather than living with the power loss.
- **Pre-specified hierarchical / gatekeeping designs** (test B only if A is significant) control FWER by structure and don't need a flat correction across the whole set.

## See also

- [`../knowledge/statistical-pitfalls.md`](../knowledge/statistical-pitfalls.md) — pitfall #2 (multiple comparisons) and the FWER-vs-FDR expansion.
- [`./effect-size-and-ci-not-bare-p.md`](./effect-size-and-ci-not-bare-p.md) — what you report once the surviving result is corrected.
- [`./design-pre-register-to-avoid-p-hacking.md`](./design-pre-register-to-avoid-p-hacking.md) — pre-specifying the family removes the "how many tests" ambiguity.
- [`../knowledge/test-selection-decision-tree.md`](../knowledge/test-selection-decision-tree.md) — the omnibus-then-post-hoc rule for 3+ groups.

## Provenance

Codifies pitfall #2 and the FWER-vs-FDR guidance in [`../knowledge/statistical-pitfalls.md`](../knowledge/statistical-pitfalls.md) (last reviewed 2026-05-26; Tier 1 / consensus — Statsig "Controlling your type I errors"; MetricGate "Bonferroni vs Holm vs FDR"; with the caveat from J. Clin. Epidemiol. S0895-4356(15)00301-7 that FDR is not a universal Bonferroni drop-in). The advisory hook [`../hooks/flag-statistical-smells.sh`](../hooks/flag-statistical-smells.sh) flags 3+ test calls with no correction.

---

_Last reviewed: 2026-05-30 by `claude`_
