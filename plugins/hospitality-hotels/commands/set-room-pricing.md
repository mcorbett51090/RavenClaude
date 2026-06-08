---
description: "Run a room-pricing decision for a specific date range: assess the demand signal, position vs. comp set, traverse the raise-or-hold-rate tree, and output a BAR recommendation with RevPAR impact estimate."
argument-hint: "[date range, e.g. 'July 4th weekend', and available context: OTB occupancy %, comp-set rate, event calendar]"
---

You are running `/hospitality-hotels:set-room-pricing`. Use the `revenue-manager` discipline and
the `revenue-management-and-pricing` skill.

## Steps

1. Gather the demand context from the user (or infer from the argument): date range, current
   on-the-books (OTB) occupancy % and room-nights, same-time-last-year (STLY) comparison if
   available, current BAR, and comp-set rate snapshot.

2. Identify any demand-calendar events (citywide, local events, holidays, compression periods)
   for the date range. Treat any compression indicator (OTB pace significantly above forecast
   or STLY) as a rate-raise signal.

3. Traverse the **raise-or-hold-rate** decision tree in
   `knowledge/hospitality-hotels-decision-trees.md` top-to-bottom. Document the branch taken
   at each node. Land on a leaf (raise / hold / lower) with the basis stated.

4. Recommend the BAR move (or confirmation to hold): state the proposed BAR, the demand basis
   (OTB pace, comp-set position, days-to-arrival), and any length-of-stay controls if the
   period is a compression date.

5. Calculate the RevPAR impact using `scripts/hotel_calc.py` (or manual formula). Show:
   - Current: ADR × current occupancy forecast = RevPAR
   - Revised: new BAR × revised occupancy forecast = RevPAR
   - Delta: RevPAR improvement per available room-night

6. Flag anti-patterns: if no demand basis can be provided, state clearly that the recommendation
   requires OTB data before execution. Do not set a rate on intuition alone.

7. Emit the Structured Output block with handoffs to `reservations-and-channel-analyst` (for
   channel-cost implications of the new rate) and `hotel-ops-lead` (for GOP impact if the
   decision is material).
