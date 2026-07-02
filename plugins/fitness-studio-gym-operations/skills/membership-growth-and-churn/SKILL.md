---
name: membership-growth-and-churn
description: "Read a fitness membership base as a subscription business: net member movement (joins minus churn), the retention/survival curve, member LTV = ARPU / churn, and the leaky-bucket diagnosis that tells you whether to fix acquisition or retention first. Churn/LTV benchmarks are verify-at-use."
---

# Membership Growth & Churn

A gym is a subscription business. The number that matters is not gross joins but **net movement and the retention curve** — and the fastest way to lose money is to pour marketing into a leaky bucket.

## The core identities

```
net member change   =  joins  -  churned members
member LTV (simple)  =  ARPU per month  /  monthly churn rate
```

A member at $150/month dues with 5% monthly churn is worth ~20 months × $150 = ~$3,000 in dues alone (before ancillary). Halve churn to 2.5% and LTV roughly doubles — which is why retention outperforms acquisition on unit economics. Treat the churn and ARPU inputs as `[verify-at-use]` against your own books.

## The leaky-bucket diagnosis

```
Is the base growing?
  -> joins > churn  and churn near benchmark   ->  scale acquisition
  -> joins > churn  but churn high             ->  FIX churn first (marketing into a leaky bucket)
  -> joins < churn                             ->  retention emergency — stop spending on acquisition until the curve stabilizes
```

## Metrics

| Metric | What it tells you | Note |
|---|---|---|
| Monthly churn rate | Base durability | The denominator of LTV — move this first |
| Net member change | Real growth | Joins alone is a vanity number |
| Member LTV | What a member is worth | Drives allowable acquisition cost (CAC) |
| LTV : CAC ratio | Whether growth pays | Under target = acquisition is unprofitable |
| Retention/survival by cohort | Where members drop | Early-month cliff = onboarding problem |

## Anti-patterns

- Celebrating gross joins while net movement is flat or negative.
- Scaling ad spend on a base with above-benchmark churn.
- Quoting an LTV without dating the churn and ARPU inputs.

## See also

- Traverse the **churn-save triage** and **membership pricing / tier model** trees in [`../../knowledge/fitness-studio-decision-trees.md`](../../knowledge/fitness-studio-decision-trees.md).
- Benchmarks (dated, verify-at-use): [`../../knowledge/fitness-studio-reference-2026.md`](../../knowledge/fitness-studio-reference-2026.md).
- Sibling skills: [`../member-onboarding-and-retention/SKILL.md`](../member-onboarding-and-retention/SKILL.md), [`../ancillary-revenue-mix/SKILL.md`](../ancillary-revenue-mix/SKILL.md).
- Best practices: [`../../best-practices/retention-beats-acquisition-on-unit-economics.md`](../../best-practices/retention-beats-acquisition-on-unit-economics.md), [`../../best-practices/price-the-membership-on-value-and-commitment.md`](../../best-practices/price-the-membership-on-value-and-commitment.md).
