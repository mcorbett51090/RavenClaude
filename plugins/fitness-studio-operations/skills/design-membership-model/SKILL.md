---
name: design-membership-model
description: "Design the studio's membership model: drop-in, class packs, unlimited recurring, and founding-member pricing — choosing the model on cash-flow shape and retention shape, and setting founding-member cohort caps and sunset terms."
---

# Design Membership Model

A membership model is a *business shape*, not a price. Choose it on cash flow and retention, then set the number.

## The four models (shapes)

| Model | Cash-flow shape | Retention shape | Best when |
|---|---|---|---|
| **Drop-in** | High margin, volatile, no commitment | None — re-acquire every visit | Tourists, low-frequency, trial |
| **Class packs** (e.g. 10-pack) | Cash pulled forward; expiry-driven | Breakage + pack-end churn cliff | Mid-frequency, flexibility-seekers |
| **Unlimited recurring** | Predictable MRR — the engine | Lives or dies on churn; compounds | Committed regulars; the core base |
| **Founding-member** | Funds launch; caps lifetime value | Loyal but low-LTV forever | Pre-open / launch only |

## Rules
- **Name the shape before the number.** Decide which cash-flow and retention shape the studio needs, then price it.
- **Recurring is the engine.** It's the only model with predictable MRR — but it only works if churn is managed (hand off to `member-retention-analyst`).
- **Packs hide a churn cliff.** Members vanish when the pack runs out; a recurring nudge before the last class is where you convert them.
- **Founding-member pricing is a loan against future revenue.** Always cap the cohort size and **sunset the terms** (a date or a tenure), or you anchor your best fans at your lowest rate forever.
- **A discount is near-permanent.** Prefer limited-time or value-add to cutting the headline rate.

## Pair it with the math
Every model recommendation carries its unit economics — hand the chosen model to [`../compute-studio-unit-economics/SKILL.md`](../compute-studio-unit-economics/SKILL.md) for revenue per member, LTV, and the CAC ceiling.

## Anti-patterns
- A pricing doc with no churn/retention view (the hook flags this).
- Founding-member pricing with no cohort cap and no sunset.
- Defaulting to unlimited because competitors do, without modeling whether your churn supports it.

Output via [`../../templates/membership-model-and-pricing.md`](../../templates/membership-model-and-pricing.md). Traverse the pricing-model tree in [`../../knowledge/fitness-studio-operations-decision-trees.md`](../../knowledge/fitness-studio-operations-decision-trees.md) first.
