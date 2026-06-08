# Attribution is a model, not the truth

**Status:** Pattern
**Domain:** Marketing attribution / measurement
**Applies to:** `marketing-operations-demand-gen`

---

## Why this exists

Attribution models are accounting frameworks for credit-sharing — they are useful proxies for
relative channel comparison, not proofs of causation. Presenting a channel's "contribution to
pipeline" without naming the attribution model is misinformation: the same data under last-touch
vs W-shaped attribution can produce wildly different channel rankings, and leadership making
multi-hundred-thousand-dollar budget decisions on unnamed-model outputs is making decisions on
a number they cannot verify or interrogate.

The second failure mode is treating the model's output as causal proof ("paid social caused this
deal") — an overclaim that attribution methodology cannot support. Attribution tells you which
touchpoint gets proportional credit under a set of accounting rules. It does not isolate the
counterfactual.

## How to apply

- **Name the model in every report.** Every attribution output — in a deck, a dashboard, a Slack
  message, a budget request — states which model produced it. "Marketing contributed 40% of Q3
  pipeline" is incomplete. "Marketing contributed 40% of Q3 pipeline under W-shaped attribution"
  is a claim someone can interrogate.
- **Present ranges across models.** When making a budget-reallocation argument, show the channel
  rankings under at least two models. Where they agree, the case is strong. Where they diverge,
  explain why and flag the uncertainty.
- **Document model limitations explicitly.** Every attribution report has a "Model caveats"
  section: what the model over-credits, what it under-credits, and the data coverage rate (% of
  pipeline with known source).
- **Distinguish marketing-sourced from marketing-influenced.** They answer different questions.
  Conflating them — or presenting only the larger number without disclosure — is misleading.

**Do:**

- State the attribution model name and lookback window in every report header.
- Include a model caveats section for any budget-level decision.
- Offer to re-run analysis under an alternative model when asked.

**Don't:**

- Present a single attribution model's output as "what marketing contributed" without naming it.
- Use the phrase "attribution proves" — attribution models estimate, they do not prove.
- Compare two channels' ROI figures from different attribution models in the same table without labeling each row.
- Build attribution reports on top of UTM data with >20% unknown-source traffic without flagging the coverage gap.

## Edge cases / when the rule does NOT apply

For internal quick reads in a weekly Slack update (e.g., "last week: 15 MQLs from LinkedIn"),
the model label can be abbreviated if the team's shared understanding of the default model is
documented. Any report that exits the marketing team — to Sales, RevOps, finance, the board —
carries the full label, no abbreviation.

## See also

- [`./a-utm-taxonomy-or-your-data-is-noise.md`](./a-utm-taxonomy-or-your-data-is-noise.md)
- [`../skills/attribution-modeling/SKILL.md`](../skills/attribution-modeling/SKILL.md)
- [`../knowledge/marketing-ops-decision-trees.md`](../knowledge/marketing-ops-decision-trees.md) — Attribution-model selection tree.

## Provenance

Codifies the standard disclaimer in multi-touch attribution methodology from Nielsen, Forrester,
and the B2B attribution platform documentation (Dreamdata, HockeyStack methodology guides),
specifically the principle that attribution is a **credit-allocation framework**, not a causal
inference tool. The "name the model" discipline is the practitioner consensus in the MO Pros
and Demand Gen Report communities.

---

_Last reviewed: 2026-06-08 by `claude`._
