---
name: generation-budget-guard
description: "Keep generation spend a design input, not a surprise: route a cheap draft before a premium final, set a per-project generation budget cap, log each spend line (you supply the unit price — every provider price is [unverified]), and fail loudly when the cap is exceeded. Backed by gen-budget.py (stdlib, no baked-in prices) and /check-generation-budget."
---

# Generation Budget Guard

Cost control is a rubric ★ row. Draft cheap, spend once on the final, cap the project, and know before you blow the budget — not after.

> **Zero baked-in prices.** Every unit price is a **user input** — provider prices are date/plan-volatile and `[unverified — confirm on provider pricing page]`. Pull the live number from the provider's pricing page and pass it in.

## Workflow

1. **Set the per-project cap** up front (a design input, from the brief or the engagement).
2. **Route cheap draft → premium final** — iterate on a low-cost draft model to lock composition + brand, then spend on **one** premium final render. Don't premium-render every iteration.
3. **Log each spend line** with [`../../scripts/gen-budget.py`](../../scripts/gen-budget.py) `add` — model, tier (draft/final), your unit price, count. It computes the line cost; it never invents a price.
4. **Check status** — `gen-budget.py status --budget <cap>` (wired into [`/check-generation-budget`](../../commands/check-generation-budget.md)) reports spent, remaining, and by-tier, and **exits non-zero if over budget** (LOUD-FAIL, never a silent pass).
5. **Dedup/cache** — reuse an approved asset (and prefer an editing round-trip) before generating a near-duplicate.

## The cheap-draft-then-final loop

| Phase | Model tier | Spend |
|---|---|---|
| Explore composition + brand | Draft (cheap) | Many cheap renders |
| Lock the chosen composition | — | Curation gate |
| Final render | Premium | **One** render |
| Ship resolution | Upscale round-trip | Cheaper than a premium re-roll |

## Anti-patterns

- Premium-rendering every iteration (draft first).
- No per-project cap (budget as a quarterly surprise).
- Baking a provider price into a tool or a client quote (prices are `[unverified]`).
- Re-generating a near-duplicate instead of reusing / round-tripping an approved asset.

## See also

- Best-practice: [`../../best-practices/route-cheap-draft-before-premium-final.md`](../../best-practices/route-cheap-draft-before-premium-final.md)
- [`../../scripts/gen-budget.py`](../../scripts/gen-budget.py), [`../../commands/check-generation-budget.md`](../../commands/check-generation-budget.md)
