# Route a cheap draft before a premium final

**Status:** Pattern
**Domain:** Operations / cost
**Applies to:** `generative-web-media`

> Engineering pattern. Every provider price is `[unverified — confirm on provider pricing page]`; the tools bake in zero prices.

---

## Why this exists

Premium generation models cost meaningfully more per render than draft models, and most of the iterations in a project are about *composition and brand* — decisions a cheap draft model resolves just as well. Spending premium credits on every exploratory render is the classic cost blowout. Lock the composition and brand on a cheap draft, then spend once on a premium final (and upscale the chosen one rather than re-rolling at high cost).

## How to apply

- **Iterate on a cheap draft model** to lock composition + brand.
- Spend on **one premium final render** of the chosen composition.
- **Upscale** the final (a round-trip) instead of a premium re-roll for higher resolution.
- Set a **per-project generation budget** as a design input; log spend with [`../scripts/gen-budget.py`](../scripts/gen-budget.py) (you supply every price) and check it with [`/check-generation-budget`](../commands/check-generation-budget.md), which fails loudly over the cap.
- **Dedup / reuse** an approved asset (prefer an editing round-trip) before generating a near-duplicate.

**Do:** draft cheap, spend once, cap the project.
**Don't:** premium-render every iteration, or bake a provider price into a tool or a client quote.

## Edge cases / when the rule does NOT apply

When only one premium model can produce the required capability at all (e.g. a specific style or resolution), draft-tiering may not apply — but the per-project cap still does.

## See also

- [`../skills/generation-budget-guard/SKILL.md`](../skills/generation-budget-guard/SKILL.md)
- [`../scripts/gen-budget.py`](../scripts/gen-budget.py), [`../commands/check-generation-budget.md`](../commands/check-generation-budget.md)

## Provenance

Codifies the cost house opinion; grounded in the provider-matrix price ordering (all `[unverified]`, retrieved 2026-07-13).

---

_Last reviewed: 2026-07-13 by `claude`_
