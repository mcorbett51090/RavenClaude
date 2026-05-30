# A coefficient is association, not cause — the causal verb triggers a design check

**Status:** Absolute rule
**Domain:** Causal inference / claim discipline
**Applies to:** `applied-statistics`

---

## Why this exists

A regression coefficient, a correlation, or an A/B difference *without randomization* tells you that X and Y move together — not that intervening on X moves Y. Reporting one as the other is the single most consequential overreach a statistician can make: it sends a client to spend money changing X expecting Y to follow, when the link was a confounder, selection, or reverse causation all along (house opinion #7). The discipline is mechanical: **the words "drives / causes / because / impact / effect of" trigger a causal-design check.** Either the data came from a randomized experiment or a defensible causal design, or the claim is downgraded to association in plain language. There is no richer regression that converts correlation into causation — only a better *design* does.

## How to apply

When a question or a draft uses a causal verb, run the three-threat screen, then either point to the design that licenses the claim or downgrade the language:

```
Causal verb present? ("drives / causes / because / impact / effect of")
  -> Did the data come from randomization or a causal design?
       YES (RCT / DiD / IV / RDD / matching, assumptions defended) -> causal claim OK
       NO  -> screen the three threats, then DOWNGRADE to association:
              Confounding       — a third variable Z causes both X and Y?
              Selection bias     — who is in the sample depends on the outcome?
              Reverse causation  — could Y cause X? (timing / plausibility)
              => report "X is ASSOCIATED with Y", not "X drives Y"
```

**Do:**
- State plainly, on every "does X cause Y?" question, whether the data supports a causal or only an associational claim.
- When only observational data exists, name the most defensible design (usually DiD or matching), its key assumption, and the residual risk (unobserved confounding).
- Use the words "associated with / predicts / correlates" for observational findings; reserve "causes / drives / the effect of" for randomized or causal-design evidence.

**Don't:**
- Let a regression coefficient be reported as a causal lever with no causal design behind it.
- Assume controlling for more covariates makes a claim causal — it only addresses *observed* confounders, and over-controlling can introduce collider bias.
- Accept "drives / impact" language in an analysis doc unchallenged — the advisory hook flags correlation language paired with causal verbs.

## Edge cases / when the rule does NOT apply

- **Pure prediction tasks** ("forecast Y", "flag likely churners") don't need causal claims — association is exactly what a predictive model trades on; just don't slip a causal interpretation onto a predictor's coefficient.
- **Randomized data** already licenses the causal claim — an A/B test *is* the causal design, so its treatment effect is causal (subject to the usual validity checks).
- **Mechanistic / physical models** where the causal structure is known a priori (a law of physics, an accounting identity) don't need an empirical causal design to assert direction.

## See also

- [`../knowledge/causal-inference-primer.md`](../knowledge/causal-inference-primer.md) — the three threats and the DiD/matching/IV/RDD toolkit at primer depth.
- [`./causal-pick-the-identification-strategy.md`](./causal-pick-the-identification-strategy.md) — which causal design to reach for once a causal claim is warranted.
- [`./causal-watch-confounders-and-colliders.md`](./causal-watch-confounders-and-colliders.md) — why "control for everything" is wrong (collider bias).
- [`../knowledge/statistical-pitfalls.md`](../knowledge/statistical-pitfalls.md) — Simpson's paradox (#4), a common confounding manifestation.

## Provenance

Codifies house opinion #7 ("correlation ≠ causation") in [`../CLAUDE.md`](../CLAUDE.md) §3 and the core distinction + three-threats table in [`../knowledge/causal-inference-primer.md`](../knowledge/causal-inference-primer.md) (last reviewed 2026-05-26; textbook consensus). The advisory hook [`../hooks/flag-statistical-smells.sh`](../hooks/flag-statistical-smells.sh) flags correlation language paired with causal verbs in `.md`/`.Rmd`/`.qmd`/`.ipynb`.

---

_Last reviewed: 2026-05-30 by `claude`_
