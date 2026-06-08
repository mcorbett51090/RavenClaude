---
name: work-order-triage
description: "Classify residential work orders by safety and habitability first (emergency vs. routine vs. deferred), run the emergency/habitability response (no heat/water/power/gas/lock), schedule preventive maintenance, dispatch vendors, and scope unit turns — flagging warranty-of-habitability as a legal question to counsel."
---

# Work-Order Triage

## Triage by safety and habitability first, cost second
Classify every work order by risk to person and to habitability before cost or convenience. Emergency → dispatch now; urgent (will worsen) → 24-72h; routine → schedule; defer → log **with the reason and a revisit date**, never silently drop. Cost is the tie-breaker between equally-urgent items, never the gate in front of an urgent one.

## Emergencies & habitability
No heat in winter, no water, no power, sewage, gas leak, and no working lock are habitability/emergency events with a duty to act fast — they never sit in the routine queue. When in doubt, treat as emergency and escalate; under-reacting to a gas smell is the unrecoverable error. Whether a condition legally breaches the warranty of habitability is a **counsel** question — flag it; the operational urgency does not wait on the legal answer.

## Preventive maintenance
A PM schedule (HVAC/filters, water heaters, smoke/CO detectors, seasonal/gutters, unit inspections) with cadence pays for itself in deferred emergencies; justify it by the reactive cost and habitability risk it removes.

## Vendor dispatch & unit turns
Match the work to a vendor, hand the licensed trade work + scope to `skilled-trades-contracting`, and follow up to closure — every open work order has a state and a next action. A unit turn (clean, paint, repair, re-key, make-ready) starts the clock at **notice**, not at empty; cost the turn and route capex-vs-opex to `owner-and-portfolio-reporting-analyst` / `finance`.

## Output
A triage classification (emergency / urgent / routine / deferred), a PM schedule, a dispatch plan, or a turn scope — with any warranty-of-habitability legal question flagged to counsel. The actual repair routes to `skilled-trades-contracting`; the cost numbers to the reporting analyst.
