---
description: "Design or fix a craft-beverage club/membership: price tiers on member lifetime value (shipment value x frequency x tenure), read churn by cohort to find the driver, treat each shipment as a retention moment, and coordinate club allocation with production (verify-at-use on norms)."
argument-hint: "[current tiers + shipment value/frequency + club size + churn by cohort if known + production allocation picture]"
---

You are running `/craft-beverage-operations:design-club-tier`. Use `tasting-room-and-club-manager` + the `club-membership-and-dtc-revenue` skill, coordinating allocation with `craft-beverage-operations-lead`.

> Operations decision-support, not legal advice. Club billing can carry payment-processor and consumer-protection implications, and DTC shipping is jurisdiction-specific — flag those `[verify-at-use]` and route to a professional / the compliance advisor. No PII — work in cohorts and offers, never a customer record.

## Steps

1. Capture current tiers, shipment value/frequency, member benefits, club size, and churn (by cohort if known).
2. Traverse the **design the club** tree in `knowledge/craft-beverage-decision-trees.md`.
3. Price tiers on **member lifetime value** (shipment value × frequency × tenure), not on one shipment.
4. Read churn by cohort to name the driver (value/frequency fit vs price vs seasonality); fix curation/frequency/flexibility (skip/swap) before discounting.
5. Coordinate club allocation with production so you don't over-commit past supply (`craft-beverage-operations-lead`).
6. Flag any billing/shipping-compliance specific `[verify-at-use]` and route it.
7. Emit using `templates/channel-margin-and-cogs-worksheet.md` (DTC/club section) + the Structured Output block, with the tier design, modeled LTV, and the churn driver addressed.
