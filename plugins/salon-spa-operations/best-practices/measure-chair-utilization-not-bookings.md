# Measure chair utilization, not bookings

**Status:** Absolute rule
**Domain:** Booking / capacity
**Applies to:** `salon-spa-operations`

---

## Why this exists

"We're busy" is not "we're full." A salon can feel busy and still leak revenue through empty mid-week chairs and 15-30 minute gaps between appointments — time that can never be resold. Booking counts hide this; utilization (booked vs *available* hours) exposes it. The gap between the two is the cheapest revenue in the building, because the chair, the rent, and often the stylist are already paid for.

## How to apply

- **Track booked vs available hours** per stylist per day, not just appointment counts.
- **Set a utilization target** (see the dated benchmark range — re-verify before quoting).
- **Diagnose the empty chair before fixing it:** too little *demand* (a `marketing-operations` seam, plus off-peak/mix levers) vs a *scheduling* failure (online booking, gaps, color-overlap capacity, skill/shift fit, no-shows).
- **Fill gaps** with shorter buffers, stacked add-ons, and color processing-time overlap booked as capacity.

**Do:** manage to utilization-with-quality (keep recovery time, not just density).
**Don't:** call a gap-free but exhausting calendar "full" — late runs and bad experiences cost rebookings.

## Edge cases / when the rule does NOT apply

A deliberately premium/low-volume model (long appointments, white space by design) optimizes ticket and experience over raw utilization — name that as the strategy, don't drift into it by accident.

## See also

- [`../knowledge/salon-spa-operations-decision-trees.md`](../knowledge/salon-spa-operations-decision-trees.md) (empty-chair tree)
- [`./book-the-color-processing-gap-dont-double-book-it.md`](./book-the-color-processing-gap-dont-double-book-it.md)

## Provenance

Codifies the `booking-and-retention-analyst` house opinion ("a booked chair is not a full chair").

---

_Last reviewed: 2026-06-25 by `claude`_
