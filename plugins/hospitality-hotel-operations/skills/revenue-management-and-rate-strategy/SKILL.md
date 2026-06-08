---
name: revenue-management-and-rate-strategy
description: "Maximize rooms revenue on RevPAR read against GOPPAR: the KPI set (RevPAR / ADR / Occ / GOPPAR), the BAR / rate ladder and pricing strategy, channel and OTA economics on net ADR, demand forecasting, and the overbooking / yield decision."
---

# Revenue Management & Rate Strategy

## The KPI set
RevPAR = ADR × Occupancy = room revenue ÷ available rooms is the north-star. ADR = room revenue ÷ rooms sold; Occupancy = rooms sold ÷ available rooms; GOPPAR = gross operating profit ÷ available rooms is the profit check. A full hotel at a giveaway rate and an empty hotel at rack both fail — optimize RevPAR, read it against GOPPAR so you don't buy occupancy with unprofitable cost.

## Forecast first
The demand forecast (seasonality, day-of-week, events, pickup pace) is the spine: it drives the rate ladder, the overbooking call, and the labor schedule. Frame the forecast and the business question here; route the statistical method (the model, confidence intervals) to `applied-statistics`. A forecast that doesn't change a decision is a report.

## Rate strategy — price to demand
Build the BAR / rate ladder off your own demand curve and pickup, not a competitor's number (comp-set is an input, not the strategy). Use length-of-stay and advance-purchase fences for soft demand instead of an open BAR cut. Discount only when the lower rate raises RevPAR after the give-back *and* the incremental occupancy is profitable on GOPPAR.

## Channel & OTA economics — net ADR
Compare every channel and offer on net ADR (headline rate − commission/channel cost − loyalty/discount give-back), never gross. Drive direct-booking share to cut distribution cost, but never strand the demand the OTAs uniquely reach — the OTA is a paid acquisition channel with a known cost, used deliberately.

## Overbooking & yield
Overbook only to a forecasted no-show/cancellation rate, only when the yield upside beats the expected walk cost + brand damage, and only with an operations-owned walk-protocol (route to `hotel-operations-lead`). Never past the walk the property can absorb gracefully.

## Output
A rate strategy: the demand forecast, the BAR/rate ladder, net-ADR channel mix, the overbooking call, and the RevPAR target read against GOPPAR. Route the walk-protocol/labor schedule to `hotel-operations-lead`, the forecast method to `applied-statistics`, the KPI pipeline to `data-platform`.
