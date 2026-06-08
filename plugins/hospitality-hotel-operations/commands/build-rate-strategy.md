---
description: "Build a hotel rate strategy on RevPAR (read against GOPPAR): the demand forecast, the BAR/rate ladder, net-ADR channel mix, and the overbooking/yield call."
argument-hint: "[property + segment mix + current KPIs (RevPAR/ADR/Occ) + channel/OTA cost + the date range]"
---

You are running `/hospitality-hotel-operations:build-rate-strategy`. Use `revenue-manager` + the `revenue-management-and-rate-strategy` skill.

## Steps
1. State the KPI baseline (RevPAR / ADR / Occupancy / GOPPAR) and the demand picture: seasonality, day-of-week, events, current pickup pace. If no forecast exists, frame one (route the statistical method to `applied-statistics`).
2. Build the rate ladder — the BAR by date tied to the forecast, with LOS/advance-purchase fences for soft demand. Set the discount-vs-hold rule on RevPAR after give-back and GOPPAR.
3. Analyze channel mix on **net ADR** (rate − commission/channel cost − give-back); recommend a direct-vs-OTA shift that doesn't strand demand the OTAs uniquely reach.
4. Make the overbooking call: size to the forecasted no-show rate, name the walk-cost and the walk-protocol dependency (route to `hotel-operations-lead`), and the limit beyond which it isn't worth it.
5. Route handoffs: labor schedule + walk-protocol → hotel-operations-lead, forecast method → applied-statistics, KPI pipeline → data-platform.
6. Emit the rate-strategy brief + the Structured Output block (with `KPI impact:` and `Handoff to neighbours:`).
