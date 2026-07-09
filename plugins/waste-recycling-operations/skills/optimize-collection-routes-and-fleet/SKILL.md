---
name: optimize-collection-routes-and-fleet
description: Raise route density and cut cost-per-stop for a collection territory by measuring stops-per-hour and windshield time, sequencing and balancing routes, choosing static vs dynamic routing (RouteWare / Routeware-AMCS / Trux), and matching the fleet mix (front / rear / side-load ASL / roll-off, RNG/EV) to each stream. Reach for this when the user asks "how do we get more stops per hour?", "static or dynamic routing?", "cut windshield time", or "what truck for this stream?". Used by `route-and-diversion-specialist` (primary, route half) and `waste-operations-lead` (fleet half).
---

# Skill: optimize-collection-routes-and-fleet

> **Invoked by:** `route-and-diversion-specialist` (primary on the route half) and `waste-operations-lead` (co-driver on the fleet half).
>
> **When to invoke:** "How do we get more stops per hour?"; "cut our windshield time"; "static or dynamic routing?"; "what truck mix for these streams?"; any move from "our collection is inefficient" to a denser, cheaper operation.
>
> **Output:** a route-optimization plan (density / stops-per-hour target, windshield-time cut, sequencing, static vs dynamic + tool) and the fleet mix that serves each stream, with cost-per-stop as the KPI and the flip conditions named.

## Procedure

1. **Measure the baseline before proposing anything.** Pull current **stops per hour**, **windshield time** (drive-to-route + between-clusters + to-disposal), route balance across trucks, and **cost per stop**. A route plan built on guessed numbers is a guess — get the telematics/RouteWare data first.
2. **Match the truck to the stream and container.** Side-load / automated (ASL) for cart-based residential (the labor + safety win), rear-load for manual/alley, front-load for commercial dumpsters, roll-off for C&D/temporary. Traverse [`../../knowledge/waste-operations-decision-tree.md`](../../knowledge/waste-operations-decision-tree.md) — don't put an ASL on a route the carts/streets don't support.
3. **Attack density — it's the profit driver.** Tighten service-area geography, cluster stops, and **balance** the routes (an overloaded route beside a light one wastes capacity). Density × stops-per-hour is what cost-per-stop rolls up from.
4. **Cut windshield time.** Reduce disposal round-trips (a **transfer station** consolidates loads so trucks don't drive the full haul), sequence to minimize deadhead, and check depot/disposal siting. Unproductive drive time is pure cost.
5. **Choose static vs dynamic routing deliberately.** **Static** (fixed daily routes, re-balanced periodically) for predictable residential subscription; **dynamic** (re-sequenced from demand + telematics) for on-call commercial and roll-off. Name the tool (RouteWare / Routeware-AMCS / Trux) and the mode — don't default to whatever ships out of the box.
6. **Set the fleet posture.** The truck mix by stream, the maintenance cadence (refuse duty cycles are brutal — PM keeps the fleet available and safe), and any RNG/EV call grounded in duty cycle + infrastructure + incentives (hand the alt-fuel decision to `waste-operations-lead` if it drives a capital plan).
7. **State the KPI and the flip conditions.** Cost-per-stop is the number; name the 1-2 facts that would change the routing/fleet call (a new transfer station, a service-area growth that unbalances static routes, an alt-fuel incentive). Capture it in [`../../templates/route-optimization-plan.md`](../../templates/route-optimization-plan.md).

## Worked example

> User: "Residential subscription MSW + recycling, ~110 stops/hour, drivers say they spend too long driving to the landfill. Static routes, RouteWare. How do we improve?"

- **Baseline:** 110 stops/hour, high windshield time flagged on the disposal round-trip — the tell is drive-to-disposal, not service time.
- **Truck:** already cart-based residential → **side-load ASL** is the right fit; confirm carts are standardized (a set-out discipline gap caps stops/hour).
- **Density:** re-balance the static routes (check for an overloaded vs light imbalance) and cluster; target ~130–140 stops/hour with tighter sequencing.
- **Windshield time:** the biggest lever here is the disposal round-trip — evaluate a **transfer station** so trucks tip locally and a trailer long-hauls, cutting the per-load drive. (Hand the transfer-station-vs-direct-haul economics to `manage-disposal-and-regulatory-compliance`.)
- **Routing:** keep **static** (predictable subscription) but re-balance in RouteWare; reserve **dynamic** for the commercial/roll-off book.
- **KPI:** cost-per-stop. **Flip condition:** if the territory grows and static routes drift out of balance, re-optimize; if a transfer station opens closer, revisit the disposal round-trip.

## Guardrails

- Measure stops/hour + windshield time before recommending — never optimize on guessed numbers.
- Density and windshield time drive cost-per-stop — **optimize the route before the vehicle** (a faster truck on a sparse route loses).
- Match the truck to the stream + container; an ASL needs standardized carts + street geometry.
- Static vs dynamic is a deliberate choice by demand predictability, not a tool default.
- The disposal round-trip is often the biggest windshield-time lever — cross-reference [`manage-disposal-and-regulatory-compliance`](../manage-disposal-and-regulatory-compliance/SKILL.md) for the transfer-station economics.
- Volatile facts (alt-fuel incentives, tooling feature sets) carry a **retrieval date**. See [`../../knowledge/waste-recycling-patterns-2026.md`](../../knowledge/waste-recycling-patterns-2026.md).
