---
name: club-membership-and-dtc-revenue
description: "Build the recurring-revenue engine: design club/membership tiers on member lifetime value (shipment value/frequency, benefits), read and reduce churn by cohort, and manage DTC e-commerce. A club member is worth more than a case sold — but churn quietly eats the club."
---

# Club / Membership & DTC Revenue

The club is the craft producer's recurring-revenue engine — predictable, high-margin depletion from a member who's also a brand advocate. But a club with strong sign-ups and quiet churn is a leaky bucket. This skill designs tiers on lifetime value and manages churn as hard as acquisition.

## The loop

1. **Design tiers on member lifetime value, not one shipment.** Shipment value, frequency, and member benefits (allocations, discounts, events, pickup) shape LTV. Traverse the **design the club** tree in [`../../knowledge/craft-beverage-decision-trees.md`](../../knowledge/craft-beverage-decision-trees.md). Norms are `[verify-at-use]`.
2. **Read churn by cohort and shipment.** Where members drop (after shipment 1? after a price change? seasonal?) names the driver — usually value/frequency fit, not price alone.
3. **Manage the shipment as the retention moment.** Each shipment is a chance to retain or lose; curation, communication, and flexibility (skip/swap) reduce churn.
4. **Coordinate allocation with production.** The club pre-commits volume; hand allocation between club, tasting-room, and wholesale to `craft-beverage-operations-lead`.
5. **Run DTC e-commerce as the always-on channel.** The club plus e-commerce is the full-margin DTC base wholesale can't match.

## Metrics

| Metric | Reads | Note |
|---|---|---|
| Club member LTV | avg shipment value × tenure | The design target; `[verify-at-use]` |
| Club churn rate | cancels / members / period | The leaky-bucket metric; read by cohort |
| Sign-up conversion | joins / tasting-room visitors | Feeds the funnel |
| Shipment fulfillment / skip rate | shipped / due, skips | Flexibility signal |
| DTC e-commerce contribution | online margin / period | Always-on full-margin demand |

## Anti-patterns

- Pricing a tier on one shipment's margin instead of member LTV.
- Celebrating sign-ups while churn quietly offsets them.
- Treating the shipment as fulfillment instead of a retention moment.
- Over-committing club allocation past what production can supply (coordinate with the ops lead).

## See also

- [`../tasting-room-throughput-and-conversion/SKILL.md`](../tasting-room-throughput-and-conversion/SKILL.md) — the funnel that feeds the club.
- Best practices: [`../../best-practices/the-club-is-the-recurring-revenue-engine.md`](../../best-practices/the-club-is-the-recurring-revenue-engine.md).
- Command: [`/design-club-tier`](../../commands/design-club-tier.md).
