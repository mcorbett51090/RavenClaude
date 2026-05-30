# When the assumption gate fails, drop to the named nonparametric fallback — don't force the parametric test

**Status:** Pattern (strong default; deviate only with a written reason)
**Domain:** Hypothesis testing / robustness
**Applies to:** `applied-statistics`

---

## Why this exists

Every parametric test has a distribution-free counterpart, and the whole point of the assumption gate is that the fallback is chosen *before* a result is reported, not retrofitted after a reviewer objects. When normality or equal-variance fails and a transformation won't fix it, forcing the parametric test produces a p-value and CI you can't defend. The fallback is not a defeat — it answers the same question (is there a location shift / association?) without the assumption you couldn't meet. The companion rule [`./check-assumptions-before-the-test.md`](./check-assumptions-before-the-test.md) says *check the gate*; this rule names *what to do when it fails*, so the agent never stalls at "assumptions violated" with no next move.

## How to apply

Map the failed parametric test to its named fallback (this is the plugin's canonical pairing table):

```
Parametric (gate failed)                 ->  Named fallback
  one-sample t-test                       ->  Wilcoxon signed-rank
  independent t-test                       ->  Mann-Whitney U
  paired t-test                            ->  Wilcoxon signed-rank
  one-way ANOVA (+ Tukey)                  ->  Kruskal-Wallis (+ Dunn)
  repeated-measures ANOVA                  ->  Friedman
  Pearson correlation / OLS                ->  Spearman rank correlation
  unequal variance only (normality OK)     ->  Welch's t-test / Welch ANOVA (still parametric)
  several predictors, no clean fallback    ->  robust SEs or bootstrap CIs
```

**Do:**
- Take the *named* fallback for the specific test, not a generic "use a non-parametric test."
- Note that unequal-variance-only does not require going nonparametric — Welch's t-test handles it and keeps the parametric framing.
- When no clean rank fallback exists (e.g., multi-predictor regression), reach for bootstrap CIs or robust standard errors and name that as the method taken.

**Don't:**
- Report a parametric result you can't stand behind because "the t-test is more familiar."
- Treat the fallback as assumption-free — rank tests still assume independence and (for a clean location-shift interpretation) similar distribution shapes across groups.
- Silently swap to a fallback without recording it on the `Assumptions checked:` line of the Output Contract.

## Edge cases / when the rule does NOT apply

- **Large-sample CLT robustness** — at large n a t-test/ANOVA is robust to mild non-normality; "robust" is a defended judgment with the Q-Q plot shown, not a blanket excuse to skip the fallback.
- **Rank tests change the estimand** — Mann-Whitney tests stochastic dominance / median shift, not a mean difference; if the stakeholder needs a mean difference with a CI, prefer a transformation or bootstrap over a rank test.
- **Tied / heavily-discrete data** can break the assumptions of some rank tests too — use the exact or permutation version.

## See also

- [`../knowledge/test-selection-decision-tree.md`](../knowledge/test-selection-decision-tree.md) — the parametric↔nonparametric fallback table this codifies.
- [`./check-assumptions-before-the-test.md`](./check-assumptions-before-the-test.md) — the gate that tells you when to take the fallback.
- [`./test-match-the-test-to-the-data-type.md`](./test-match-the-test-to-the-data-type.md) — choosing the candidate test before the gate runs.
- [`../knowledge/statistics-tooling-2026.md`](../knowledge/statistics-tooling-2026.md) — `scipy`/`pingouin` calls for each fallback; `scipy.stats.bootstrap` for the distribution-free CI route.

## Provenance

Codifies house opinion #4 ("check assumptions or use the fallback") in [`../CLAUDE.md`](../CLAUDE.md) §3 and the parametric↔nonparametric fallback table in [`../knowledge/test-selection-decision-tree.md`](../knowledge/test-selection-decision-tree.md) (last reviewed 2026-05-26; Tier 1 / consensus). Companion to [`./check-assumptions-before-the-test.md`](./check-assumptions-before-the-test.md).

---

_Last reviewed: 2026-05-30 by `claude`_
