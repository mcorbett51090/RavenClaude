---
scenario_id: 2026-06-08-thin-contribution-starved-the-pool
contributed_at: 2026-06-08
plugin: insurance-life-health-benefits
product: fully-insured
product_version: "unknown"
scope: likely-general
tags: [contribution, enrollment, adverse-selection, take-up, rating, total-cost]
confidence: medium
reviewed: false
---

## Problem

To trim spend, an employer cut its medical contribution from ~80% of the employee-only premium to a flat ~$250/month and called it "still a generous benefit." Take-up cratered the next open enrollment: the healthy, lower-paid, and single employees declined and went elsewhere (a spouse's plan, the marketplace), while the people who stayed were disproportionately high-utilizers who needed the coverage at any price. The following renewal came back sharply worse, and leadership read the increase as "the carrier gouging us" rather than a pool they had thinned themselves.

## Constraints context

- The contribution decision was made as a pure cost line — nobody modeled how the employee share would move take-up or who would drop.
- A mixed workforce on pay: a flat dollar contribution was a small share of a high earner's premium but a punishing share of a lower-paid employee's, so it selectively pushed out exactly the healthy, cost-sensitive lives a pool needs.
- The renewal was being read as a single "+X%" with no decomposition and no link back to the participation drop.

## Attempts

- Tried: defend the flat-$250 cut on budget savings alone. Failed — the per-head savings were real, but the shrinking, sicker risk pool drove the next rate up by more than the cut saved; the "savings" were borrowed from the renewal.
- Tried: model the split before committing — the calculator's `contribution` mode showed the employee share at each design (percent-of-premium vs flat dollar) and made the take-up risk legible instead of a surprise.
- Tried: move back toward a percent-of-premium employer share (so the contribution scales with the premium and doesn't disproportionately tax lower-paid employees), and pair it with the renewal decomposition (the `renewal`/`review-renewal` path) so the participation effect was named, not blamed on the carrier.

## Resolution

The employer restored a percent-of-premium contribution closer to the prior level for employee-only coverage (tiered down for dependents to hold budget), participation recovered enough to re-broaden the pool, and the next renewal was decomposed so the participation-driven piece was visible and separable from trend. The lesson stuck: the contribution split is a risk-pool lever, not just a cost line. The `medium` confidence reflects that the magnitude of the take-up swing is group-specific — the direction is reliable, the size is not.

## Lesson

The employer/employee contribution split shapes enrollment and the risk pool, not just the budget — a thin or flat employer share suppresses take-up and adversely selects the pool, and the savings often come straight back as a worse renewal. Model the employee share and projected participation before changing contribution, prefer a percent-of-premium basis so it doesn't selectively push out lower-paid healthy lives, and decompose the resulting renewal rather than blaming the carrier. (Educational scaffolding; a licensed broker confirms the actual contribution/affordability and ACA-safe-harbor math.)
