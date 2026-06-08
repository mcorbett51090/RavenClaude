# Overbooking is a calculated risk, not a gamble

**Status:** Pattern
**Domain:** Hotel inventory management — overbooking policy
**Applies to:** `hospitality-hotels`

---

## Why this exists

Hotels face a predictable and quantifiable rate of no-shows and last-minute cancellations. Rooms
that go empty because of no-shows are revenue lost forever on perishable inventory. Overbooking —
accepting more reservations than available rooms — is the standard industry practice to recover
this lost revenue. Done correctly with historical data and a walk-cost model, it is a net-positive
revenue strategy. Done as a fixed percentage applied without data ("we always overbook by 3%"),
it is a gamble that can damage loyal guests, trigger online complaints, and create regulatory
and brand risk.

The distinction is: **overbooking with a model** is a calculated risk that a rational operator
manages. **Overbooking by intuition** is a gamble that the operator has not examined.

## How to apply

- **Do:** Build the model before setting any overbook level. Required inputs:
  1. 12-month no-show rate (from PMS history) — the percentage of reservations that do not
     arrive and do not cancel within the allowed window
  2. Same-day cancellation rate — cancellations received on the day of arrival
  3. Expected same-day rebookings — walk-ins or same-day new reservations that partially offset
  4. Walk cost — the per-walk cost: relocation rate, compensation (cash, voucher, or F&B credit),
     loyalty points cost, and estimated reputational cost
- **Do:** Calculate the expected RevPAR uplift of the overbook level and compare it to the
  expected walk cost at that overbook level. Overbook only where the math is positive.
- **Do:** Build and maintain a walk-recovery playbook before implementing any overbook policy:
  preferred relocation property, staff empowerment level, communication script, compensation
  standard.
- **Do:** Review the model monthly — no-show rates change by season, segment, and booking-window.

**Don't:**

- Set an overbook level as a fixed percentage with no historical basis.
- Overbook without a walk-recovery playbook in place.
- Apply the same overbook level across all segments and booking windows — a transient leisure
  booking made 60 days out has a different cancellation probability than a same-day walk-in.
- Ignore the loyalty impact of a walk: a member walked from their confirmed reservation has a
  cost that extends well beyond the night's room revenue.

## Edge cases / when the rule does NOT apply

- **New property (< 12 months of history):** insufficient data to build a reliable model. Use a
  conservative hold-back approach (accept overbooking only to 1–2 rooms above capacity) until
  12 months of data are available.
- **Branded properties with brand-standard walk policies:** some brands have brand-standard walk
  penalties (compensation levels, relocation standards) that define the walk-cost floor. Use the
  brand standard as the walk-cost floor, not an estimate.

## See also

- [`./revpar-is-the-north-star-not-occupancy-alone.md`](./revpar-is-the-north-star-not-occupancy-alone.md)
- [`./the-guest-experience-is-the-product.md`](./the-guest-experience-is-the-product.md)
- [`../knowledge/hospitality-hotels-decision-trees.md`](../knowledge/hospitality-hotels-decision-trees.md) — overbook-or-not tree
- [`../scripts/hotel_calc.py`](../scripts/hotel_calc.py) — displacement mode models overbook RevPAR uplift vs. walk cost

## Provenance

Yield-management literature (the EMSR-b method and its hotel-specific applications in Williamson
1992; Talluri and van Ryzin 2004) establishes overbooking as a standard RM technique. The walk-
cost model framework is standard in the HSMAI CRME curriculum. The "calculated risk, not a gamble"
framing distinguishes evidence-based RM practice from intuition-based operations.

---

_Last reviewed: 2026-06-08 by `claude`._
