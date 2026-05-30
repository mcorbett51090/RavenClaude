# Adjust for confounders, never for colliders or mediators — draw the DAG first

**Status:** Primary diagnostic (when an "effect of X" estimate looks off, check what was controlled for)
**Domain:** Causal inference / covariate selection
**Applies to:** `applied-statistics`

---

## Why this exists

"Control for everything you can measure" is a folk rule that is actively wrong. Whether adjusting for a variable *removes* bias or *creates* it depends on that variable's causal role, not on whether it is available:

- A **confounder** (causes both treatment and outcome) — adjusting for it *removes* bias. Skip it and the X→Y estimate is confounded.
- A **collider** (caused by both treatment and outcome, or by two causes of the outcome) — adjusting for it *opens* a spurious path and *creates* bias where none existed (this is how selection bias and Berkson's paradox arise).
- A **mediator** (sits on the causal path X→M→Y) — adjusting for it removes part of the very effect you want to estimate, biasing the total effect toward zero.

You cannot tell these apart from the data — they can have identical correlations with X and Y. You tell them apart from the **assumed causal structure**, which is why the discipline is: sketch the DAG, classify each candidate covariate, then adjust for confounders only.

## How to apply

Before fitting an "effect of X on Y" model, classify each candidate covariate by its role in the DAG:

```
For each covariate Z, what is its causal role relative to X (treatment) and Y (outcome)?
  Z -> X and Z -> Y         CONFOUNDER  -> ADJUST (control for it)
  X -> Z and Y -> Z         COLLIDER    -> DO NOT adjust (adjusting opens a spurious path)
  X -> Z -> Y               MEDIATOR    -> DO NOT adjust for the TOTAL effect
                                          (adjust only when you explicitly want the DIRECT effect)
  Z -> X only (not Y)       INSTRUMENT-ish / precision var -> optional; adjusting rarely hurts
# Tooling: dagitty / pgmpy to derive the minimal sufficient adjustment set from the DAG
```

**Do:**
- Draw (or write out) the assumed causal graph before choosing the covariate set; let it dictate the adjustment set.
- Adjust for confounders; leave colliders and mediators out of the total-effect model.
- Be explicit when you want a *direct* (mediator-adjusted) vs *total* effect — they answer different questions.

**Don't:**
- Throw every available variable into the regression and read a coefficient as "the effect of X" — you may have conditioned on a collider.
- Adjust for a post-treatment variable (anything measured after X) without checking it isn't a mediator or collider.
- Assume more covariates always means less bias — for colliders/mediators, more is worse.

## Edge cases / when the rule does NOT apply

- **Pure prediction** (no causal interpretation of any coefficient) can use colliders and mediators freely — they carry predictive signal; the prohibition is specifically about *causal* coefficient interpretation.
- **Unknown DAG** — when the causal structure is genuinely uncertain, run a sensitivity analysis across plausible adjustment sets and report how much the estimate moves, rather than asserting one.
- **Instrumental-variable / RDD designs** identify the effect through design, not adjustment — the covariate-role logic still informs which controls are safe, but the identification comes from the instrument/cutoff.

## See also

- [`../knowledge/causal-inference-primer.md`](../knowledge/causal-inference-primer.md) — confounding / selection / reverse causation; matching balances *observed* confounders only.
- [`./causal-correlation-is-not-causation.md`](./causal-correlation-is-not-causation.md) — the upstream rule: a coefficient is association unless a design backs it.
- [`./causal-pick-the-identification-strategy.md`](./causal-pick-the-identification-strategy.md) — choosing the design once the threats are mapped.
- [`../knowledge/statistical-pitfalls.md`](../knowledge/statistical-pitfalls.md) — Simpson's paradox (#4) as confounding made visible.

## Provenance

Extends the "selection bias" / "confounding" threats in [`../knowledge/causal-inference-primer.md`](../knowledge/causal-inference-primer.md) (last reviewed 2026-05-26; textbook consensus) with the standard DAG-based confounder/collider/mediator taxonomy (Pearl; Hernán & Robins, *Causal Inference: What If*). The "matching balances observed confounders only" caveat is from the primer's toolkit table. Tier 2 (strong-but-contextual) — the role classification is a modelling judgment, marked as resting on the assumed DAG.

---

_Last reviewed: 2026-05-30 by `claude`_
