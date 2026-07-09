# waste-recycling-operations

> The **hauling & diversion operations layer** for Claude Code — the team that answers *"how do we collect, haul, dispose of, and divert waste profitably, safely, and in compliance?"* and builds the operating model, routes, and diversion economics that make the answer defensible. Two agents: the **waste-operations-lead** (streams, fleet, disposal, Subtitle D compliance, safety) and the **route-and-diversion-specialist** (route density, diversion rate, MRF & recycling commodity economics, contamination).

Part of the [RavenClaude](../../README.md) marketplace. Extends `ravenclaude-core`.

## What it does

| You ask | It returns |
|---|---|
| "How should we structure collection across residential, commercial, and roll-off?" | A stream-by-stream service model (container, cadence, truck type, disposal endpoint) with the pricing lever named |
| "Direct-haul to the landfill or run through a transfer station?" | A disposal decision with the tipping-fee, airspace, and leachate/gas implications and the Subtitle D obligations |
| "What truck mix do we run, and should we go RNG or EV?" | A fleet plan (front/rear/side-load ASL/roll-off) + maintenance cadence + an alt-fuel call grounded in duty cycle |
| "Our routes are inefficient — how do we get more stops per hour?" | A route-optimization plan: density/stops-per-hour targets, windshield-time cuts, sequencing, static vs dynamic routing |
| "What's our real diversion rate and how do we raise it?" | A diversion rate measured from weigh tickets, the streams dragging it, and a lift plan with the cost implications |
| "Our MRF revenue is underwater — bale prices low, contamination high." | A recycling-economics call: contamination reduction + commodity exposure by grade + the pricing response, dated prices |

**Two rules it never breaks:** *route density is the profit driver* (optimize the route before the vehicle) and *contamination is the killer of recycling economics* (a clean single-stream load is revenue; a dirty one is a disposal cost). And a scope line it never crosses: **RCRA Subtitle D non-hazardous only — hazardous Subtitle C is routed out.**

## What's inside

- **2 agents** — `waste-operations-lead` (collection streams, fleet, transfer/landfill disposal, Subtitle D compliance, DOT/CDL & hopper safety) and `route-and-diversion-specialist` (route density/stops-per-hour, diversion-rate measurement, MRF & commodity economics, contamination reduction).
- **3 skills** — `optimize-collection-routes-and-fleet`, `manage-disposal-and-regulatory-compliance`, `improve-diversion-and-recycling-economics`.
- **2 knowledge files** — a Mermaid waste-operations decision tree (stream→truck, direct-haul vs transfer station, static vs dynamic routing, landfill vs divert, the Subtitle-D-vs-C scope gate) and a 2026 waste-recycling-patterns reference (route-density math, fleet types, disposal/tipping-fee/airspace economics, MRF & commodity markets post-National-Sword, contamination, diversion measurement, EPR/SB 1383/landfill bans, safety, tooling map).
- **2 templates** — a route-optimization plan and a diversion-and-cost analysis.

## Where it sits in the operation

```
fleet-logistics             →  generic telematics / DOT / vehicle routing  ("cross-industry fleet")
esg-sustainability-reporting →  corporate ESG / diversion as a REPORTED metric ("what we disclose")
hazardous-waste (Subtitle C) →  characteristic/listed hazardous + incidents   ("out of scope — routed OUT")
waste-recycling-operations (HERE) →  collect / haul / dispose / DIVERT the non-hazardous stream  ("run the trucks profitably")
```

This plugin is the **hauling & diversion operations layer**: it runs the trucks and disposal that `fleet-logistics` supplies telematics for, produces the diversion tonnage that `esg-sustainability-reporting` discloses, and stays firmly on the **RCRA Subtitle D non-hazardous** side of the line — hazardous Subtitle C handling and incident response are adjacent and out of scope.

## Domain stance

Concept-first (route density & cost-per-stop, static-vs-dynamic routing, the truck-to-stream match, tipping-fee/airspace/leachate-gas economics, diversion measurement from weigh tickets, contamination-as-the-killer, commodity exposure by grade, Subtitle D compliance, and the industry's safety reality), fluent across the collection streams (MSW, single-stream recycling, organics/food waste, C&D), the fleet types (front/rear/side-load ASL, roll-off, RNG/EV), the routing tools (**RouteWare / Routeware-AMCS / Trux**), and the recycling commodity grades (**OCC/cardboard, PET, HDPE, aluminum, mixed paper**). Volatile facts — tipping fees, bale/commodity prices, EPR/landfill-ban/SB 1383 statutes, alt-fuel incentives — carry retrieval dates; re-verify before pinning in a client deliverable.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install waste-recycling-operations@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.
