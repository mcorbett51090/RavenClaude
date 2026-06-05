# Right-size the model; don't default to the frontier tier

**Status:** Pattern
**Domain:** Model selection methodology / cost
**Applies to:** `ai-coding-model-guidance`

---

## Why this exists

Defaulting every coding task to the most capable (and most expensive) model in
the lineup is the single most common over-spend pattern across GitHub Copilot,
OpenAI Codex, and xAI Grok deployments. Everyday code completions,
autocomplete, and routine single-file changes do not benefit from frontier-tier
reasoning — they benefit from low latency and a tight feedback loop. The
frontier tier should be reserved for the hard tail: large autonomous refactors,
complex multi-file analysis, and tasks where the quality gap is measurable.

## How to apply

Map every task to a tier first, then pick the cheapest SKU in that tier:

| Tier | Observable task shape | Default choice |
|---|---|---|
| Inline / fast | Autocomplete, one-line fix, quick lookup | Cheapest fast model available |
| Balanced | Routine coding, PR review, moderate reasoning | Mid-tier balanced default |
| Frontier | Autonomous multi-file, deep analysis, hard reasoning tail | Top frontier model |

The metric is **cost-per-resolved-task**, not model rank. If a balanced model
resolves a task 98% as well as the frontier at 20% of the cost, the balanced
model wins for that task class.

**Do:**
- Measure task resolution rate by tier in your eval harness before committing
  to a model choice.
- Communicate the tier recommendation with the tradeoff to the developer
  ("balanced resolves this class 95% as well at significantly lower cost
  `[verify-at-use]`").
- Revisit tier assignment when the task complexity profile changes.

**Don't:**
- Recommend the frontier tier as a "safe default" to avoid being wrong.
- Use model rank/benchmark position as a proxy for fitness to a specific task
  shape — benchmark scores are not task-specific `[verify-at-use]`.
- Quote specific price ratios without a `[verify-at-use — YYYY-MM]` marker;
  pricing changes frequently.

## Edge cases / when the rule does NOT apply

- Safety-critical, irreversible autonomous actions (deleting production data,
  merging to main): use the frontier tier regardless of routine cost — the
  downside risk justifies the spend.
- When the developer has independently measured that the balanced tier fails
  their specific task class: respect the measurement, not the heuristic.

## See also

- [`../agents/grok-model-strategist.md`](../agents/grok-model-strategist.md) — Grok tier selection
- [`./traverse-the-tree-before-naming-a-sku.md`](./traverse-the-tree-before-naming-a-sku.md) — the upstream tree traversal this tier mapping feeds
- [`../knowledge/ai-coding-decision-trees.md`](../knowledge/ai-coding-decision-trees.md) — the vendor-neutral tier decision tree

## Provenance

Codifies house opinion #2 from `CLAUDE.md` §3 ("right-size, don't default to
the top") and the anti-pattern "defaulting to the top frontier for everyday work
instead of right-sizing." Standard cost-per-resolved-task discipline.

---

_Last reviewed: 2026-06-05 by `claude`_
