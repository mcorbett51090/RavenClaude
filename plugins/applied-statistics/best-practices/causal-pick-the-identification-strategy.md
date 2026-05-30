# Pick the causal design by what natural variation you have — and defend its key assumption

**Status:** Pattern (strong default; deviate only with a written reason)
**Domain:** Causal inference / design selection
**Applies to:** `applied-statistics`

---

## Why this exists

When a causal claim is warranted (the causal-verb check passed) but you can't run a clean A/B test, the answer is not "a richer regression" — it's a **causal identification strategy** matched to the natural variation the situation offers. Each design buys causal identification with a *different* assumption, and that assumption — not the estimator's machinery — is what a reviewer will attack. Reaching for instrumental variables when a difference-in-differences setup is sitting right there, or quoting a matching estimate without flagging unobserved confounding, is how observational causal work loses credibility. The discipline: name the design that fits the available variation, state its load-bearing assumption out loud, and flag the residual risk.

## How to apply

Traverse the causal-method decision tree (data-generating situation → design → key assumption):

```
Can you randomize the intervention?
  YES -> Randomized experiment (A/B)        gold standard; sidesteps all three threats
  NO  -> what natural variation exists?
     Treatment hit one group at a known time, with before/after on treated + untreated
            -> Difference-in-Differences      KEY ASSUMPTION: parallel trends
     Treatment assigned by a sharp cutoff on a running variable
            -> Regression Discontinuity (RDD) estimates a LOCAL effect near the cutoff
     A variable shifts treatment but not the outcome directly
            -> Instrumental Variables (2SLS)  needs a valid, defensible instrument (rare)
     Just observational treated vs untreated, want comparable units
            -> Matching / propensity scores   balances OBSERVED confounders only
# Implementation of IV / panel models -> linearmodels (Tier 2)
```

**Do:**
- For SMB engagements, push hard toward a randomized experiment when feasible — it is the cleanest and most communicable.
- When observational, prefer DiD or matching (most defensible and explainable); reach for IV/RDD only when the natural setup genuinely exists.
- State the design's key assumption (parallel trends / valid instrument / local-to-cutoff / no unobserved confounding) and the residual risk in the report.

**Don't:**
- Present a matching/propensity estimate as if it handled unobserved confounding — it does not; say so.
- Quote a difference-in-differences result without showing (or at least arguing) parallel pre-trends.
- Generalize an RDD estimate beyond the neighborhood of the cutoff — it is a *local* effect.

## Edge cases / when the rule does NOT apply

- **Randomization is available** — then this whole tree collapses to "run the experiment"; the observational designs are the fallback, not the goal.
- **Multiple valid designs fit** — triangulating two independent designs (e.g., DiD and IV) that agree is stronger evidence than either alone; do it when the stakes justify the effort.
- **Estimator depth beyond a primer** (staggered-adoption DiD, fuzzy RDD, weak-instrument diagnostics) — flag that the build needs more than the primer and route to the agent / `linearmodels`, don't hand-wave the assumption.

## See also

- [`../knowledge/causal-inference-primer.md`](../knowledge/causal-inference-primer.md) — the toolkit table (RCT / DiD / matching / IV / RDD) with each design's one-line caveat.
- [`./causal-correlation-is-not-causation.md`](./causal-correlation-is-not-causation.md) — the gate that decides whether a causal design is even needed.
- [`./causal-watch-confounders-and-colliders.md`](./causal-watch-confounders-and-colliders.md) — covariate selection within whichever design you pick.
- [`../knowledge/stats-test-selection-decision-trees.md`](../knowledge/stats-test-selection-decision-trees.md) — the causal-method decision tree in full.

## Provenance

Codifies the causal toolkit table and the "push toward randomization; else DiD/matching > IV/RDD" guidance in [`../knowledge/causal-inference-primer.md`](../knowledge/causal-inference-primer.md) (last reviewed 2026-05-26; textbook consensus, Tier 2). IV/panel implementation via `linearmodels` per [`../knowledge/statistics-tooling-2026.md`](../knowledge/statistics-tooling-2026.md).

---

_Last reviewed: 2026-05-30 by `claude`_
