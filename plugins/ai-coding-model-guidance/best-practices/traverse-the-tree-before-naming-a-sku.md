# Traverse the selection tree before naming a model SKU

**Status:** Absolute rule
**Domain:** Model selection methodology
**Applies to:** `ai-coding-model-guidance`

---

## Why this exists

Keyword-matching a task to a model name is the dominant failure pattern in this
plugin's domain: a developer says "complex coding task" and the agent replies
"GPT-5.5-Pro" without reasoning through latency, autonomy, plan length, or
difficulty. The result is an over-provisioned expensive model for work that a
balanced default handles fine, or an under-provisioned model for a genuinely hard
task. The decision tree in the knowledge bank encodes the vendor-neutral
selection logic; bypassing it turns the agent into a brand-name lookup table.

## How to apply

Before naming any model SKU, place the task on the vendor-neutral tree:

1. **Latency constraint** — is inline completion / interactive chat, or is it an
   autonomous background run?
2. **Task difficulty** — everyday code completion and routine changes vs.
   hard analysis, large refactors, or open-ended autonomous tasks?
3. **Reasoning lever** — can more reasoning on the same model close the gap
   before jumping to a bigger model (Codex-specific: reasoning-level dial)?
4. **Cost sensitivity** — is per-token cost a binding constraint relative to the
   task value?

Only once these four dimensions are placed does the agent map the leaf to the
vendor's current lineup.

```
Step 1: Ask "What is the task shape?" → place on the tree
Step 2: "Which leaf?" → identify the tier (inline/fast, balanced, frontier)
Step 3: "Which vendor?" → map the tier to the verified SKU in the dated lineup
Step 4: "Is that SKU current?" → verify against the knowledge bank [verify-at-use]
```

**Do:**
- Always narrate the tree traversal to the developer; don't just name a model.
- When two leaves are plausible, explain the tradeoff rather than picking
  arbitrarily.
- Re-traverse after the developer provides more context — task shape updates the
  answer.

**Don't:**
- Skip to a model name because the developer used a keyword ("complex", "simple",
  "production") — those are not tree nodes.
- Keyword-match "Codex" to a model name without checking the current lineup.
- Treat the tree traversal as optional when the answer "feels obvious."

## Edge cases / when the rule does NOT apply

- The developer has already placed the task on the tree and is asking only for
  the current verified SKU for a known leaf: confirm the leaf and supply the
  verified name.

## See also

- [`../agents/codex-model-strategist.md`](../agents/codex-model-strategist.md) — owns the Codex reasoning-level dial
- [`../agents/copilot-model-strategist.md`](../agents/copilot-model-strategist.md) — owns Copilot surface/plan scoping
- [`../knowledge/ai-coding-decision-trees.md`](../knowledge/ai-coding-decision-trees.md) — the vendor-neutral tree to traverse

## Provenance

Codifies house opinion #1 from `CLAUDE.md` §3 ("traverse the decision tree before
naming a SKU") and the anti-pattern "keyword-matching the task to a SKU without
traversing the decision tree" (§4). Standard model-selection methodology.

---

_Last reviewed: 2026-06-05 by `claude`_
