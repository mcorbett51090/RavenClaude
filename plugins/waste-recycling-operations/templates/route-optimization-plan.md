# Route optimization plan — <territory / service area>

> The plan captured when tightening a collection operation. Pairs with
> [`diversion-and-cost-analysis.md`](diversion-and-cost-analysis.md) (what the diverted
> tonnage is worth). The rule this plan enforces: **route density is the profit driver —
> optimize the route before the vehicle.**

**Owner:** <name / route supervisor> · **Date:** <YYYY-MM-DD> · **Routing tool:** <RouteWare / Routeware-AMCS / Trux / other> · **Status:** draft / approved / implemented

## Territory & streams
- **Service area:** <geography · # of stops · residential / commercial / roll-off split>
- **Streams collected:** <MSW / single-stream recycling / organics / C&D>
- **Disposal / diversion endpoints:** <landfill · transfer station · MRF · compost/AD>

## Baseline (measure before optimizing — never guess)
| Metric | Today | Target | Source |
|---|---|---|---|
| Stops per hour | <n> | <n> | <telematics / RouteWare> |
| Windshield time (drive/route) | <hrs or %> | <lower> | <telematics> |
| Route balance (stops/tons per truck) | <spread> | <balanced> | <route data> |
| Cost per stop (the KPI) | <$> | <$> | <finance + ops> |

## Fleet mix (match the truck to the stream + container)
| Route / stream | Truck type | Crew | Rationale |
|---|---|---|---|
| <residential cart> | side-load / ASL | 1 | cart-based · labor + safety win |
| <manual/alley> | rear-load | <n> | flexible · higher lifting exposure |
| <commercial dumpster> | front-load | 1 | 2–8yd containers |
| <C&D / temporary> | roll-off | 1 | 10–40yd boxes, on-call |

- **Alt-fuel posture:** <diesel / RNG / EV + duty-cycle rationale — escalate a capital plan to waste-operations-lead>
- **Maintenance cadence:** <PM interval — refuse duty cycles are brutal; availability + safety depend on it>

## Density & windshield-time moves
- **Density:** <re-cluster / re-balance overloaded vs light routes / geography tightening>
- **Windshield time:** <reduce disposal round-trips (transfer station?) · sequencing · depot/disposal siting>
- **Sequencing:** <the specific re-sequence in the routing tool>

## Routing mode
- **Static vs dynamic:** <static for predictable residential subscription · dynamic for on-call commercial/roll-off>
- **Tool + configuration:** <RouteWare / Routeware-AMCS / Trux · the config, not the default>
- **Re-balance trigger:** <when static routes drift out of balance as the territory grows>

## KPI & expected impact
- **KPI:** cost per stop → <expected change>
- **Secondary:** stops/hour <→ target> · windshield time <→ lower>

## Seams (not this plan)
- **Transfer-station vs direct-haul economics · Subtitle D compliance · safety:** manage-disposal-and-regulatory-compliance / waste-operations-lead
- **What the diverted tonnage is worth · contamination:** improve-diversion-and-recycling-economics / route-and-diversion-specialist
- **Generic fleet telematics / DOT as a cross-industry function:** fleet-logistics

## Flip conditions
- <the 1-2 facts (new transfer station, territory growth, alt-fuel incentive) that would change the routing/fleet call>

## Open questions / risks
- <list>

**Sign-off:** <reviewer> · <date>
