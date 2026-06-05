# Table Turn Time Is a Revenue Lever, Not Just a Hospitality Metric

**Status:** Pattern
**Domain:** FOH operations / revenue management
**Applies to:** `restaurant-operations`

---

## Why this exists

Full-service restaurants treat table turn time almost entirely as a guest-experience metric — rushing guests is poor hospitality. It is also a revenue-per-seat-per-hour metric. A 90-minute average turn on a 2-hour peak window leaves one turn on the table; a 75-minute average allows one-and-a-third turns on the same seats. The incremental revenue of that additional partial turn, at $35 average check, across 40 seats, is $350–$500 per service — without adding a guest, a cook, or a dollar of marketing. Operators who track turn time only for hospitality reasons miss the revenue and contribution-margin conversation.

## How to apply

Build a turn-time revenue model for peak service periods:

```
Turn-time revenue model (per service period):
  Seat count:                          ______
  Peak service window (hours):         ______
  Current average turn time (minutes): ______
  Current turns per peak window:       peak window / (turn time / 60) = ______
  Target turn time (minutes):          ______
  Target turns per peak window:        ______
  Incremental turns:                   ______
  Average check:                       $______
  Incremental revenue per service:     incremental turns × seats × average check = $______
  Contribution margin on incremental:  incremental revenue × (1 − prime cost %) = $______
```

Turn-time levers (in order of blast radius — low to high):
1. **Expediting POS → kitchen tickets** — reduces ticket-to-table time without touching the guest experience.
2. **Payment friction** — moving to table-pay or QR-code payment cuts the check-present-to-cleared cycle from 8–12 min to 2–3 min.
3. **Server greeting and order-timing standards** — a standard that requires greeting within 2 min and order-taking within 5 min sets the pace without rushing.
4. **Dessert-and-add-on pacing** — presenting the dessert offer at the right moment (after entrée cleared, not mid-bite) moves the decision faster.

**Do:**
- Track turn time by server and by table section; wide variance between servers is a training signal, not random.
- Set turn-time targets by segment: QSR casual (45–60 min), fast-casual (20–30 min), full-service (75–90 min target for peak), fine dining (uncapped).
- Model the revenue impact of a 10-minute improvement before making a process change — it justifies the investment in training and technology.

**Don't:**
- Rush guests during off-peak or when utilization is below 70% — the turn-time revenue case only applies when the restaurant is demand-constrained, not seat-constrained.
- Cut turn time by reducing service touchpoints (refills, check-ins) — the revenue gain from the extra turn is erased by lower average check and poor reviews.

## Edge cases / when the rule does NOT apply

Fine dining and destination restaurants where the experience IS the product have no turn-time optimization case — the brand and check average depend on unhurried service. Bar seating and high-top conversions often have different natural turn dynamics; model them separately.

## See also

- [`../agents/foh-boh-operations-specialist.md`](../agents/foh-boh-operations-specialist.md) — owns the service-flow and turn-time analysis.
- [`../agents/restaurant-finance-analyst.md`](../agents/restaurant-finance-analyst.md) — owns the revenue-per-seat-per-hour calculation and the P&L impact model.

## Provenance

Revenue-per-available-seat-hour (RevPASH) and turn-time management are standard concepts in restaurant revenue management, adapted from hospitality yield management; the lever-ordered framework reflects restaurant consulting practice.

---

_Last reviewed: 2026-06-05 by `claude`_
