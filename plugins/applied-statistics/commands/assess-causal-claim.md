---
description: "Gut-check a 'does X cause Y?' claim: run the correlation-vs-causation gate, pick a causal identification strategy matched to the natural variation, and state its load-bearing assumption out loud."
argument-hint: "[the causal question, e.g. 'did the price change cause the churn drop?']"
---

# Assess a causal claim

You are running `/applied-statistics:assess-causal-claim`. Decide whether the claim (`$ARGUMENTS`) can be made causally and, if so, with which design — the `applied-statistician`'s causal gut-check. A coefficient is association unless the data came from a randomized or causal design (house opinion #7).

## When to use this

Someone wants to say "X drives / causes / impacts Y" and you need to know whether the evidence supports it. NOT for a pure significance test of a difference (that is `/applied-statistics:choose-statistical-test`), and NOT for the mechanics of fitting the model (that is `/applied-statistics:diagnose-regression`).

## Steps

1. **Run the correlation-vs-causation gate first** (`causal-correlation-is-not-causation.md`): does the request use causal verbs, and does the data-generating process justify them? If not, downgrade the claim to "associated with" and stop.
2. **If a causal claim is warranted but you can't run a clean A/B test, pick an identification strategy from the natural variation** (`causal-pick-the-identification-strategy.md`): treatment at a known time with before/after on treated + untreated → Difference-in-Differences; sharp cutoff on a running variable → Regression Discontinuity (local effect); a variable that shifts treatment but not the outcome → Instrumental Variables; comparable observational units → matching / propensity scores.
3. **State the design's load-bearing assumption out loud** — parallel trends / valid instrument / local-to-cutoff / no unobserved confounding — because that, not the estimator, is what a reviewer attacks (`causal-pick-the-identification-strategy.md`).
4. **Watch confounders and colliders** in covariate selection (`causal-watch-confounders-and-colliders.md`): adjust for confounders, never condition on a collider or a post-treatment variable.
5. **Push toward randomization** when feasible for an SMB engagement — it is cleanest and most communicable; prefer DiD/matching over IV/RDD when observational (`causal-pick-the-identification-strategy.md`).
6. Report the design, its key assumption, the residual risk, and the effect + CI (`effect-size-and-ci-not-bare-p.md`); IV/panel implementation routes to Tier-2 `linearmodels`. Flag estimator depth beyond a primer (staggered DiD, fuzzy RDD, weak instruments) rather than hand-waving.

## Guardrails

- Never present a matching/propensity estimate as if it handled unobserved confounding — it balances observed confounders only; say so.
- Don't quote a DiD result without showing or arguing parallel pre-trends; don't generalize an RDD estimate beyond the cutoff neighborhood.
- "Correlation is not causation" is the default; a causal verb in the deliverable needs a causal design behind it.
