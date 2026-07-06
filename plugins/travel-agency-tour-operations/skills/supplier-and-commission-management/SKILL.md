---
name: supplier-and-commission-management
description: "Make earned margin real: maintain a booked-vs-paid commission ledger by supplier, chase gaps on a cadence, handle net vs commissionable pricing correctly, understand BSP/ARC air settlement, and steer the mix to preferred-supplier/consortia programs. Commission terms are verify-at-use per supplier agreement."
---

# Supplier & Commission Management

Commission that is booked but never collected is the quietest agency leak. This skill closes it and steers the mix to what pays.

## The loop

1. **Ledger booked vs paid.** For every booking, record earned commission (rate × commissionable value) and reconcile against what the supplier actually paid. The gap is the recovery worklist — see the commission-recovery chase tree in [`../../knowledge/travel-agency-decision-trees.md`](../../knowledge/travel-agency-decision-trees.md).
2. **Chase on a cadence.** Commission mostly comes due post-travel. Run the sequence: match the commission statement → open a claim for missing/short payments → escalate per the supplier agreement. Timing is `[verify-at-use]` per supplier.
3. **Price net vs commissionable correctly.** Net rate → margin via markup; commissionable/retail rate → margin via paid percentage. Record which model each supplier uses so nothing is under-collected.
4. **Know the air rail.** Air settles through **BSP** (IATA, international) or **ARC** (US); bare-air commission is often minimal — see [`../../knowledge/travel-agency-reference-2026.md`](../../knowledge/travel-agency-reference-2026.md) (verify-at-use).
5. **Steer to preferred suppliers / consortia.** Weight bookings to programs with higher base commission, overrides/bonuses, and client amenities where they fit the trip.

## Metrics

| Metric | Reads | Note |
|---|---|---|
| Commission capture rate | paid / earned | The core leak indicator; target near 100% |
| Days-to-collect | booking → commission paid | Long tails hide write-offs |
| Preferred-supplier share | % booked to preferred/consortia | Higher share -> more override + amenity |
| Override / bonus earned | volume-tier and promo bonuses collected | Often left on the table |

## Anti-patterns

- Trusting suppliers to pay what they owe without a ledger.
- Confusing net and commissionable pricing (silent margin loss).
- Expecting commission from a bare-air segment the rail never pays it on.

## See also

- [`../itinerary-design-and-quoting/SKILL.md`](../itinerary-design-and-quoting/SKILL.md), [`../../templates/supplier-commission-tracker.md`](../../templates/supplier-commission-tracker.md).
- Best practice: [`../../best-practices/chase-every-commission-it-is-your-margin.md`](../../best-practices/chase-every-commission-it-is-your-margin.md).
