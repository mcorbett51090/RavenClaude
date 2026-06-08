# RevPAR is the north star — not occupancy alone

**Status:** Absolute rule
**Domain:** Hotel revenue management
**Applies to:** `hospitality-hotels`

---

## Why this exists

Occupancy is an incomplete metric. A hotel at 95% occupancy that achieved it by discounting $40
below its optimal rate has produced less revenue than a hotel at 82% occupancy at the right rate.
Optimizing occupancy in isolation — "fill the house" — is a trap that systematically destroys ADR
over time: guests anchor to the discounted rate, distribution channels learn the hotel's floor,
and the habit of discounting embeds itself in the revenue culture.

RevPAR (Revenue Per Available Room = ADR × occupancy %) is the metric that holds both variables
simultaneously. It cannot be gamed by sacrificing one for the other without the product showing the
trade-off. GOPPAR extends this discipline into the cost dimension: a high-RevPAR hotel that is
losing ground on expense management is not a well-run property.

## How to apply

- **Do:** Cite RevPAR as the primary revenue-performance metric. When reporting occupancy or ADR,
  always report the other alongside it and derive the RevPAR product.
- **Do:** Use the RevPAR index (RGI from STR comp-set data) to assess relative performance — a
  RevPAR of $120 means nothing without knowing whether the comp set is at $90 or $140.
- **Do:** When evaluating a pricing decision, always model the RevPAR outcome (ADR change × likely
  occupancy change), not just the occupancy fill rate.

**Don't:**

- Report occupancy as the headline KPI without ADR alongside it.
- Celebrate a "full house" that was achieved through rate cuts that reduced RevPAR vs. prior period.
- Set revenue targets in dollar terms alone without a RevPAR / RevPAR-index framing (dollar
  targets are hostage to room-count changes; RevPAR indexes are not).

## Edge cases / when the rule does NOT apply

- **Extremely soft periods with fixed costs threatening coverage:** when a hotel is running below
  the breakeven occupancy needed to cover fixed costs (debt service, fixed labor, utilities), a
  short-term occupancy-maximization tactic that accepts a lower ADR can be rational — but the
  breakeven occupancy must be calculated, and the tactic must be time-bounded.
- **Anchoring a new property:** in a hotel's first months of operation, building volume to create
  review density and loyalty-member trials can justify a temporary ADR sacrifice. Define the
  anchor period and the rate-ramp schedule explicitly.

## See also

- [`./sell-the-last-room-at-the-right-price.md`](./sell-the-last-room-at-the-right-price.md)
- [`./know-your-net-adr-after-ota-cost.md`](./know-your-net-adr-after-ota-cost.md)
- [`../knowledge/hospitality-hotels-decision-trees.md`](../knowledge/hospitality-hotels-decision-trees.md) — raise-or-hold-rate tree

## Provenance

Standard hotel industry revenue management doctrine; codified in the STR (CoStar) benchmarking
methodology and the AHLA / HSMAI revenue management curriculum. The RevPAR formula
(ADR × occupancy) is definitionally correct and not vendor-specific.

---

_Last reviewed: 2026-06-08 by `claude`._
