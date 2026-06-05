# Teach selection methodology, not just current SKU names

**Status:** Pattern
**Domain:** Model selection methodology / longevity
**Applies to:** `ai-coding-model-guidance`

---

## Why this exists

A developer who learns only "use Model X for hard tasks" is one vendor changelog
away from being stranded. A developer who learns the selection methodology —
what dimensions to weight, how to traverse the tree, how to evaluate cost-per-
resolved-task — can re-apply it when the lineup changes next month. This plugin's
agents are designed to teach the methodology and point at the verified current
SKU, not to be a model-name lookup table. The methodology has a lifespan measured
in years; the specific model names have a lifespan measured in weeks to months.

## How to apply

When recommending a model, structure the response in two parts:

1. **Methodology first** — walk the tree dimensions: latency constraint, task
   difficulty, reasoning lever, cost sensitivity. Name the leaf that applies.
2. **Current SKU second** — map the leaf to today's verified model name with a
   `[verify-at-use — YYYY-MM]` marker.

This gives the developer both the answer they need today and the framework to
re-answer it themselves next quarter when the lineup shifts.

Example:
```
Methodology: your task is autonomous, multi-file, without latency constraint
→ the "frontier autonomous" leaf → the highest-reasoning capable model.

Current SKU: [vendor's current frontier model name] (verify-at-use — 2026-05).

When this model is superseded, re-traverse: the leaf is stable; the SKU changes.
```

**Do:**
- Narrate the tree traversal as part of every recommendation.
- Explicitly call out the methodology as reusable and the SKU as volatile.
- When asked "what will replace X?", answer methodologically:
  "whichever model at the frontier leaf has the best cost-quality at the time."

**Don't:**
- Provide only a model name without the methodology reasoning.
- Imply that the recommended SKU is the permanent answer.
- Build the developer's mental model around vendor brand names rather than
  task-shape dimensions.

## Edge cases / when the rule does NOT apply

- The developer has already mastered the methodology and is asking only for the
  current verified SKU: skip the methodology narration and go straight to the
  verified name.

## See also

- [`./traverse-the-tree-before-naming-a-sku.md`](./traverse-the-tree-before-naming-a-sku.md) — the upstream tree-traversal rule
- [`./closed-world-verified-lineup-only.md`](./closed-world-verified-lineup-only.md) — the SKU must be in the verified lineup
- [`../knowledge/ai-coding-decision-trees.md`](../knowledge/ai-coding-decision-trees.md) — the stable methodology the agent teaches

## Provenance

Derived from the plugin's core design rationale in `CLAUDE.md` §3 and §8 ("why
one plugin, not three — one selection concern, one decision tree, one refresh
cadence"). The methodology-first discipline is the durable layer that survives
vendor lineups changing.

---

_Last reviewed: 2026-06-05 by `claude`_
