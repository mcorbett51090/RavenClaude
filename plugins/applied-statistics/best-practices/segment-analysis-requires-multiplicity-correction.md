# Segment analysis is multiple testing — apply multiplicity correction or label it exploratory

**Status:** Absolute rule
**Domain:** A/B testing / multiple comparisons
**Applies to:** `applied-statistics`

---

## Why this exists

A standard A/B test with one primary metric and two groups is a single test. The same test sliced by device type (3 segments) × age group (4 segments) × country (10 segments) = 120 sub-group tests. At alpha=0.05, you expect 6 "significant" segment effects by chance alone. A stakeholder who looks at 120 segments and reports "Mobile users in the 25-34 age group in Germany showed a significant lift!" has found noise, not a signal — unless the multiplicity inflation is corrected. Segment analysis is a standard part of A/B reporting, and it requires either a multiplicity correction or an explicit "exploratory" label.

## How to apply

**Approach 1 — Bonferroni correction (simplest, most conservative):**

```python
from statsmodels.stats.multitest import multipletests
import numpy as np

# p-values from all segment tests
p_values = [0.03, 0.12, 0.04, 0.001, 0.08, 0.20, 0.02]  # example

# Bonferroni correction
reject, p_corrected, _, _ = multipletests(p_values, alpha=0.05, method='bonferroni')
print("Corrected p-values:", p_corrected)
print("Reject H0:", reject)
```

**Approach 2 — Benjamini-Hochberg FDR (less conservative, preferred for many segments):**

```python
reject_bh, p_corrected_bh, _, _ = multipletests(p_values, alpha=0.05, method='fdr_bh')
```

**Labeling approach (for exploratory segment analysis):**

When segment analysis is explicitly exploratory (pre-specified as "we will look at these segments to generate hypotheses for future tests"):
- Label every segment result as "Exploratory — not confirmatory"
- Do not use any segment p-values to claim significant effects
- Use segment results only to prioritize future experiments

**In the statistical report:**

```markdown
## Segment analysis

**Note:** This analysis examines [N] segments. Results are [corrected with Benjamini-Hochberg FDR 
at q=0.05 / labeled exploratory and require confirmation in a dedicated experiment].

| Segment | Observed lift | Uncorrected p | BH-adjusted p | Significant |
|---|---|---|---|---|
| Mobile - 25-34 - Germany | +8.2% | 0.031 | 0.112 | No |
```

**Do:**
- Pre-specify in the design doc which segments will be analyzed (reduces fishing).
- Apply BH-FDR correction when analyzing many segments with an inference goal.
- Label segment results as exploratory when no correction is applied.

**Don't:**
- Report uncorrected p-values for segment analyses without any multiplicity caveat.
- Promote a post-hoc segment finding to a primary result without a follow-up confirmatory experiment.

## Edge cases / when the rule does NOT apply

- Pre-specified single-segment analyses (e.g., "we will ONLY analyze the mobile segment because the product is mobile-only") are not multiple tests — the correction is not needed if only one segment is specified in the design doc before seeing data.

## See also

- [`../agents/applied-statistician.md`](../agents/applied-statistician.md) — drives the experiment-analysis skill
- [`./test-correct-for-multiple-comparisons.md`](./test-correct-for-multiple-comparisons.md) — the parent multiple-comparisons rule this specializes to segment analysis

## Provenance

Codifies applied-statistics CLAUDE.md §3 house opinion (multiple comparison correction) and §4 anti-patterns ("3+ hypothesis tests with no multiple-comparison correction — the hook flags this") applied specifically to the segment-analysis pattern common in A/B testing reports.

---

_Last reviewed: 2026-06-05 by `claude`_
