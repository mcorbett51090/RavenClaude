---
scenario_id: 2026-06-08-turn-clock-started-at-empty-not-notice
contributed_at: 2026-06-08
plugin: property-management-residential
product: generic
product_version: "unknown"
scope: likely-general
tags: [vacancy, turn, make-ready, days-vacant, leasing]
confidence: high
reviewed: false
---

## Problem

A mid-size portfolio measured "turn time" from the day a unit went physically empty to the day the make-ready finished, and only started marketing once the unit was rent-ready. Units that had given 30 days' notice sat un-marketed for that whole month, then the turn began, then marketing began — stacking three sequential delays. Days-vacant ran 45-60 days on units that should have re-leased in two weeks, and the owner statements showed vacancy loss nobody could explain because the metric being optimized (turn time, measured from empty) was the wrong clock.

## Constraints context

- The make-ready vendor and the leasing team worked in sequence, not in parallel.
- The reported KPI was "turn time" measured from move-out, which looked healthy (~10 days) while days-vacant was terrible.
- Pre-marketing during the notice period was seen as "showing a unit we can't deliver yet," so nobody did it.

## Attempts

- Tried: pushing the make-ready vendor to work faster. Helped the turn-time KPI but barely moved days-vacant, because the long pole was the un-marketed notice period, not the make-ready.
- Tried: optimizing turn-cost (cheaper vendors). Failed — it traded a small cost saving for slower turns and MORE vacancy loss, which dwarfed the saving.
- Tried: starting the turn clock at NOTICE, pre-marketing during the notice period, and sequencing the make-ready to finish AT lease-up rather than before it — measuring against days-vacant and the vacancy-loss dollar number, not turn-cost in isolation. This worked.

## Resolution

Moving the clock to notice and pre-marketing the unit while the outgoing tenant was still in place collapsed the three sequential delays into overlapping ones. Days-vacant dropped from 45-60 to under 20 on the next cohort. The opex/capex split on the make-ready scope was routed to the books question (renovation-grade lines are capex and stay out of NOI), and any habitability/safety item in the scope went through maintenance triage as priority — a turn never ships an unsafe unit.

## Lesson

Vacancy is the most expensive thing in the portfolio, and the turn clock starts at notice, not at empty. Optimize against the vacancy-loss number, not turn-cost or a turn-time KPI measured from move-out. Pre-market during the notice period and sequence the make-ready to finish at lease-up. Renovation-grade turn lines are capex and stay out of NOI — that opex/capex split is a books question for `finance`.
