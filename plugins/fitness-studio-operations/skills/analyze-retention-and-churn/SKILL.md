---
name: analyze-retention-and-churn
description: "Analyze retention and churn: compute the real monthly churn rate (with a defined freeze treatment), read cohort/visit-frequency retention, build an at-risk early-warning signal, and decide keep-vs-acquire and the win-back play."
---

# Analyze Retention and Churn

Retention is the studio's economic engine. This skill produces the numbers that drive every keep-vs-acquire decision.

## Compute churn the same way every time

```
Monthly logo churn = members lost in month / members active at start of month
```

- **Define the freeze treatment up front** and apply it consistently: a freeze is not a cancel, but an unreturning freeze is churn in disguise — track freeze-to-return rate separately.
- Report the **trend** (6-12 months), not a single month.
- Average lifetime months = 1 / monthly churn → this feeds LTV in [`../compute-studio-unit-economics/SKILL.md`](../compute-studio-unit-economics/SKILL.md).

## Read cohorts, not averages
Plot retention by **join cohort** and by **membership type**. The first-90-day cliff is where most studios bleed — early-engagement work is the highest-ROI retention you have.

## At-risk early-warning signals (leading, not lagging)

| Signal | Why it precedes cancel |
|---|---|
| Visit frequency dropping vs the member's own baseline | Disengagement before the decision |
| Failed / declined payment | Involuntary churn — recoverable with dunning |
| No future class booked | Intent gone before the cancel |
| Pack nearing its last class | Conversion window closing |

Rank members on these; trigger an intervention per tier *before* the decision hardens.

## Keep-vs-acquire is arithmetic
Intervene when: `cost of intervention < P(save) × saved LTV` — and note it's almost always cheaper than CAC. Bring the numbers.

## Win-back, segmented by reason × tenure
Price-leaver, moved-away, injured, bored each need a different offer. Reactivating a long-tenure lapsed member is the cheapest growth a studio has.

## Anti-patterns
- A churn number you can't reproduce.
- Blended retention that hides a cohort cliff.
- A save offer that's always a price cut (trains members to threaten to leave).

Output via [`../../templates/retention-dashboard.md`](../../templates/retention-dashboard.md). Traverse the retention-intervention tree in [`../../knowledge/fitness-studio-operations-decision-trees.md`](../../knowledge/fitness-studio-operations-decision-trees.md) first.
