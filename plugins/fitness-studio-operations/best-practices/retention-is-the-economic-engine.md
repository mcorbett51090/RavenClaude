# Retention is the economic engine

**Status:** Absolute rule
**Domain:** Studio unit economics / retention
**Applies to:** `fitness-studio-operations`

---

## Why this exists

A studio's profitability is dominated by how long a member stays, not by how many it signs. Average lifetime months sits directly in the LTV formula (LTV = revenue per member × lifetime months × margin), so a churn improvement compounds across the whole base, while a new-member campaign only earns once per acquisition and costs CAC each time. Operators reflexively reach for acquisition because it's visible; the math usually says fix retention first.

## How to apply

- Before recommending any growth or pricing move, ask what a 5-point churn improvement is worth in lifetime months and LTV, and compare it to the campaign's expected return.
- Treat the first-90-day onboarding window as the highest-ROI retention work.
- Route at-risk detection and win-back through `member-retention-analyst`; route the spend-against-LTV decision through `fitness-studio-operations-lead`.

**Do:** model retention impact alongside any acquisition proposal.
**Don't:** default to "we need more members" without checking the leak.

## Edge cases / when the rule does NOT apply

A brand-new studio with almost no base genuinely needs acquisition to reach critical mass — but even then, build the onboarding/retention engine in parallel, not after.

## See also

- [`./know-your-real-churn-rate.md`](./know-your-real-churn-rate.md)
- [`./compute-ltv-before-cac.md`](./compute-ltv-before-cac.md)
- [`../skills/analyze-retention-and-churn/SKILL.md`](../skills/analyze-retention-and-churn/SKILL.md)

## Provenance

Standard subscription/membership unit economics. Codifies the `member-retention-analyst` house opinion ("retention is the cheapest growth").

---

_Last reviewed: 2026-06-25 by `claude`_
