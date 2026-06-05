# Compare AI coding tools by tier, not by model name

**Status:** Pattern
**Domain:** Multi-tool model selection
**Applies to:** `ai-coding-model-guidance`

---

## Why this exists

Developers comparing GitHub Copilot, OpenAI Codex, and xAI Grok frequently ask "which has the better model?" — naming specific model ids from each platform. This framing breaks within weeks when a lineup changes, and it produces a comparison that is immediately stale. The durable comparison is at the **tier level**: does the task need fast inline, balanced default, or frontier? Once the tier is established, the question becomes "which platform's current offering at that tier best fits the use case?" — a question that remains answerable even as specific model ids churn.

## How to apply

1. Place the task on the vendor-neutral tier tree first (`../knowledge/ai-coding-decision-trees.md`).
2. For each platform, identify the current offering at the required tier — consulting the dated knowledge bank, not memory.
3. Compare platforms on **tier-stable axes**: surface coupling, org policy controls, reasoning-level dial availability, and ecosystem fit.
4. Name specific model ids only at step 4, after the tier and axes have narrowed the field, and always with `[verify-at-use]` markers.

```
Stable axes (compare these):      Volatile axes (verify before quoting):
- Surface coupling                 - Specific model ids
- Reasoning-level dial (yes/no)    - Context-window sizes
- Org policy controls              - Pricing / cost per call
- IDE / terminal / API surface     - Picker contents per plan
```

**Do:**
- Lead with the tier comparison; follow with the current (dated) model id.
- Acknowledge when a tier is represented equally well by two platforms and recommend based on surface fit rather than fabricating a quality difference.

**Don't:**
- Compare "`GPT-5.5-Pro` vs. `Grok 4.3 vs. Copilot default`" as if those names persist — they don't.
- Let a developer's preference for a specific model name override the tier logic.

## Edge cases / when the rule does NOT apply

- A developer is migrating from a specific deprecated model id to a new one within a single platform — the comparison is id-level, not tier-level; use `../skills/grok-model-retirement-check/SKILL.md` or the Codex equivalent.

## See also

- [`../skills/multi-tool-model-comparison/SKILL.md`](../skills/multi-tool-model-comparison/SKILL.md) — structured cross-ecosystem comparison playbook
- [`../knowledge/ai-coding-decision-trees.md`](../knowledge/ai-coding-decision-trees.md) — the vendor-neutral tier tree

## Provenance

Derived from `CLAUDE.md` §3 house opinion #3 (availability is always scoped) and #4 (volatile numbers carry a retrieval date). Model-name comparisons are availability claims — they inherit the same verify-at-use discipline.

---

_Last reviewed: 2026-06-05 by `claude`_
