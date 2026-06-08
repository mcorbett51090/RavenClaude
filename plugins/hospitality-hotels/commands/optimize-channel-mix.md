---
description: "Analyze the hotel's current distribution channel mix, calculate net ADR and total distribution cost per channel, traverse the direct-vs-OTA decision tree, and produce a channel-optimization plan with shift-to-direct tactics if warranted."
argument-hint: "[current channel mix data, e.g. 'OTA 60%, direct 25%, GDS 15%; OTA commission 18%; direct booking engine cost 2%']"
---

You are running `/hospitality-hotels:optimize-channel-mix`. Use the
`reservations-and-channel-analyst` discipline and the `channel-and-distribution` skill.

## Steps

1. Collect (or prompt for) the channel data: list of active channels, commission or fee per
   channel, current booking volume by channel (room-nights or %), and gross ADR by channel if
   available. If ADR by channel is unavailable, use the property's blended ADR as a proxy.

2. Calculate **net ADR per channel**:
   `Net ADR = Gross ADR × (1 − commission rate) − per-transaction fees`
   Use `scripts/hotel_calc.py` (net-adr mode) or show the arithmetic inline. Build a table:
   Channel | Gross ADR | Commission/Fee | Net ADR | Net ADR Gap vs. Direct

3. Calculate **total distribution cost (TDC)**: sum of all channel costs ÷ total room revenue.
   State the benchmark (15–20% watch zone, >20% structural problem [verify-at-use]).

4. Traverse the **direct-vs-OTA** decision tree in
   `knowledge/hospitality-hotels-decision-trees.md`. Input: OTA share %, direct CAC (estimate
   if not provided: assume 3–5% booking-engine cost + metasearch [verify-at-use]), booking-
   window breakdown, parity status. Land on a recommendation.

5. Audit rate parity: identify any channels where the effective rate is below the direct BAR
   (opaque, package leakage, GDS public exposure). Flag each violation with root cause.

6. Recommend channel-mix actions ranked by net-ADR improvement:
   - If OTA-heavy: shift-to-direct investment case (metasearch, booking-engine UX, member rate)
   - If GDS underleveraged: corporate segment development recommendation
   - If parity violations present: remediation sequence

7. Fill in the `templates/channel-mix-model.md` artifact with the channel table and
   recommendations. Emit the Structured Output block with handoffs to `revenue-manager`
   (rate consequences) and `hotel-ops-lead` (GOP impact of TDC change).
