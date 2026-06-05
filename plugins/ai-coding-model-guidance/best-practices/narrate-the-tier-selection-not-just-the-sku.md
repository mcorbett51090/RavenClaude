# Narrate the tier-selection reasoning, not just the final SKU

**Status:** Pattern
**Domain:** Model selection methodology
**Applies to:** `ai-coding-model-guidance`

---

## Why this exists

A model recommendation that says "use Grok 4.3" or "use the Codex frontier model" without narrating the reasoning that got there is a black-box recommendation. If the model id changes next week (which it will), the developer has no methodology to re-derive the answer; they return to the agent and ask the same question again. The goal of this plugin is to teach the selection methodology so developers can apply it themselves — the narrated traversal is the deliverable, not just the SKU at the end.

## How to apply

Every model recommendation must narrate the tree traversal in plain language before naming the SKU:

```
Template:
"Given that your task is [use-case type], running on [surface], with [blast radius]
demand and [context demand], the vendor-neutral tree puts this in the [tier] leaf.
That maps to [ecosystem]'s current [tier] offering. Verify the specific model id
before your run — [verify-at-use — YYYY-MM]."
```

The narration should be 2-5 sentences, not a bullet list of all possible options. The developer needs to see the path from their task to the recommendation, not all paths.

**Do:**
- Name the 2-3 task attributes that drove the tree traversal (latency, blast radius, context demand).
- State the leaf the traversal reached and why.
- Explain any tradeoff if two leaves were nearly equal (e.g., "balanced default is appropriate here; frontier would help only if the task scope expands beyond X").

**Don't:**
- Skip the narration because "the developer just wants the model name."
- Present the recommendation as a brand preference or a quality ranking.
- Narrate all four dimensions when only two were determinative — brevity serves understanding better than completeness for its own sake.

## Edge cases / when the rule does NOT apply

- The developer explicitly states they have already traversed the tree and only want the current verified SKU for a known leaf — confirm the leaf and supply the name with a `[verify-at-use]` marker; no full narration needed.

## See also

- [`../knowledge/ai-coding-decision-trees.md`](../knowledge/ai-coding-decision-trees.md) — the tree to narrate
- [`../templates/model-recommendation-brief.md`](../templates/model-recommendation-brief.md) — structured output format that includes the reasoning section

## Provenance

Codifies house opinion #1 from `CLAUDE.md` §3 ("traverse the decision tree before naming a SKU") in the context of the output: the traversal is load-bearing, not background. A recommendation without the reasoning is incomplete.

---

_Last reviewed: 2026-06-05 by `claude`_
