# Raise the reasoning level before upgrading to a bigger model

**Status:** Pattern
**Domain:** Model selection methodology / cost (Codex)
**Applies to:** `ai-coding-model-guidance`

---

## Why this exists

For tools that expose a reasoning-level dial (most clearly: OpenAI Codex CLI,
where the `--reasoning` flag adjusts thinking effort on the current model), the
cheaper lever is almost always to increase reasoning on the same model before
jumping to a larger, pricier SKU. Teams that escalate directly to a bigger model
when the current one underperforms leave money and capability on the table — the
reasoning dial often closes the quality gap at a fraction of the model-upgrade
cost. This is a Codex-specific pattern today but the principle applies whenever
a vendor exposes effort/thinking controls separately from model tier.

## How to apply

Follow the ladder:

1. Try the balanced default model at the default reasoning level.
2. If quality is insufficient, **raise the reasoning level on the same model**
   (e.g. Codex `--reasoning high` or the equivalent `[verify-at-use]`).
3. Only if the raised reasoning level is still insufficient, consider moving to
   a bigger model tier.

Document your evaluation at each step: what task, what metric, what improvement
was observed.

```
# Codex CLI example (verify flag names at use — they change)
# Step 1: default reasoning
codex "refactor this module to use async/await" --model balanced-default

# Step 2: raise reasoning — same model, more thinking
codex "refactor this module to use async/await" --model balanced-default --reasoning high

# Step 3 (only if step 2 still fails): upgrade model
codex "refactor this module to use async/await" --model frontier
```

**Do:**
- Document the quality gap at each step so the decision is evidence-based.
- Communicate the cost-vs-quality tradeoff of each step to the developer.
- Re-evaluate the reasoning level when the task class changes — a level that
  was "overkill" for routine changes may be appropriate for the hard tail.

**Don't:**
- Skip step 2 and jump straight to a model upgrade because it "feels" like a
  harder task.
- Leave the reasoning level at the highest setting for all tasks
  (over-spend on easy work).
- Quote specific reasoning-level cost multipliers without a
  `[verify-at-use — YYYY-MM]` marker.

## Edge cases / when the rule does NOT apply

- When the vendor does not expose a reasoning-level dial separately from model
  tier (Copilot, current Grok lineup): skip this step and move directly to the
  model-tier decision.
- Latency-constrained inline completion: high-reasoning levels add latency that
  may be unacceptable for autocomplete.

## See also

- [`../agents/codex-model-strategist.md`](../agents/codex-model-strategist.md) — owns the Codex reasoning-level dial
- [`./right-size-not-top-of-range.md`](./right-size-not-top-of-range.md) — the upstream tier-selection rule
- [`../knowledge/ai-coding-decision-trees.md`](../knowledge/ai-coding-decision-trees.md) — the reasoning-vs-model-upgrade branch in the tree

## Provenance

Codifies house opinion #6 from `CLAUDE.md` §3 ("reasoning level is a dial —
raise it before jumping to a bigger, pricier SKU") and the anti-pattern "jumping
to a bigger Codex model when raising the reasoning level was the cheaper lever."

---

_Last reviewed: 2026-06-05 by `claude`_
