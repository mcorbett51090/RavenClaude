# Sell the last room at the right price

**Status:** Pattern
**Domain:** Hotel revenue management — compression-night pricing
**Applies to:** `hospitality-hotels`

---

## Why this exists

The marginal room on a compression night (high-demand, near-sold-out) has disproportionate value.
The scarcity of available inventory creates genuine pricing power that most hotels systematically
leave unrealized. A common failure mode: a hotel that stops raising rate at 85% occupancy because
"it feels high enough" — and sells the last 15% of inventory at the same rate as the first 50%,
surrendering the revenue that compression pricing would have earned.

The **last-room-value** principle states that the optimal rate for the last available room on a
high-demand date is higher than the rate for the first room, because the buyer's alternatives
are narrowing. This is the core logic of yield management applied to perishable inventory.

## How to apply

- **Do:** Identify compression nights at least 14–21 days in advance using OTB pace and pick-up
  trend. When OTB pace is significantly ahead of same-time-last-year and forecast, rate up.
- **Do:** Set BAR progressively as occupancy fills — a rate ladder rather than a flat rate. Each
  occupancy threshold (e.g., 70% → 80% → 90% OTB) should trigger a rate step.
- **Do:** On the night before arrival with >80% OTB, move to last-room-value pricing: the rate
  should be at the top of the comp-set range or above, not discounted to fill.
- **Do:** Use length-of-stay controls (MinLOS) on compression dates to protect shoulder-night
  revenue from being displaced by single-night arrivals.

**Don't:**

- Cap rate at a psychological threshold ("we never charge more than $X") without a demand basis.
- Discount the last rooms on a compression night to avoid leaving rooms empty overnight — an
  empty room on a genuine compression night is evidence the rate was too low the day before, not
  the night of.
- Sell inventory at a soft-period rate when the demand calendar shows compression.

## Edge cases / when the rule does NOT apply

- **Group blocks:** a pre-contracted group rate at a lower ADR than the compression BAR is a
  sunk decision; don't try to walk the group. Apply last-room-value to the transient inventory
  remaining after the group block is protected.
- **Long-stay / extended-stay guests:** a multi-week guest who arrived at a negotiated rate before
  the compression period was forecast has a prior claim; do not adjust their rate mid-stay.
- **Catastrophic weather/event:** if the compression event cancels (hurricane, major event
  cancellation), rate should return to normal immediately to avoid gouging perception and
  reputational risk.

## See also

- [`./revpar-is-the-north-star-not-occupancy-alone.md`](./revpar-is-the-north-star-not-occupancy-alone.md)
- [`./overbooking-is-a-calculated-risk-not-a-gamble.md`](./overbooking-is-a-calculated-risk-not-a-gamble.md)
- [`../knowledge/hospitality-hotels-decision-trees.md`](../knowledge/hospitality-hotels-decision-trees.md) — raise-or-hold-rate tree (last-room-value leaf)

## Provenance

Derived from foundational yield-management theory (Littlewood's Rule, 1972; Belobaba EMSR
method, 1987) applied to hotel single-night room inventory. Industry standard HSMAI CRME (Certified
Revenue Management Executive) curriculum covers last-room-value as a core principle.

---

_Last reviewed: 2026-06-08 by `claude`._
