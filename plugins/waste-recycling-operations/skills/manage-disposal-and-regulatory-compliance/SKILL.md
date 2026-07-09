---
name: manage-disposal-and-regulatory-compliance
description: Choose the disposal path (direct-haul to a Subtitle D landfill vs consolidate through a transfer station) and manage its economics (tipping fees, landfill airspace, leachate/gas) and its RCRA Subtitle D compliance, scale/weigh-ticket controls, and DOT/CDL + hopper/backing/lifting safety program — while routing hazardous Subtitle C streams OUT of scope. Reach for this when the user asks "landfill direct or through a transfer station?", "manage tipping fees / airspace", "stay Subtitle-D compliant", or "cut our injury rate". Used by `waste-operations-lead` (primary).
---

# Skill: manage-disposal-and-regulatory-compliance

> **Invoked by:** `waste-operations-lead` (primary). Also consulted by `route-and-diversion-specialist` when a diversion mandate forces a disposal change and when the disposal round-trip is the route's windshield-time lever.
>
> **When to invoke:** "Direct-haul or transfer station?"; "manage our tipping fees / airspace"; "what are our Subtitle D obligations?"; "cut our injury rate"; any move from "we have a stream to get rid of" to a compliant, safe, cost-controlled disposal path.
>
> **Output:** the disposal-path decision + its tipping-fee/airspace/leachate-gas economics + the RCRA Subtitle D compliance obligations + scale/weigh-ticket controls + the DOT/CDL & hopper-safety program — with any hazardous Subtitle C stream routed OUT.

## Procedure

1. **Run the scope gate FIRST — Subtitle D or Subtitle C?** Confirm the stream is **RCRA Subtitle D non-hazardous** solid waste. If it's characteristically or listed **hazardous (Subtitle C)**, route it OUT to a hazardous-waste specialist and stop — do not improvise a hazardous-incident response. When uncertain about characterization, treat as Subtitle C until proven otherwise.
2. **Choose the disposal path by haul economics.** **Direct-haul** to a Subtitle D landfill for short hauls / lower volume; **transfer station** to consolidate collection loads into long-haul trailers where distance/volume make the extra handling cheaper (and it cuts collection-truck windshield time). Traverse [`../../knowledge/waste-operations-decision-tree.md`](../../knowledge/waste-operations-decision-tree.md).
3. **Manage the landfill economics.** Weigh **tipping fees** ($/ton, volatile — retrieve current), **airspace** (the finite, depleting, appreciating asset every buried ton spends), and the **leachate collection + landfill-gas capture** obligations. A disposal plan that ignores airspace treats an exhaustible asset as infinite.
4. **Make the scale the source of truth.** Every load weighed in/out; the **weigh ticket** anchors tipping-fee billing, tonnage pricing, and diversion measurement. No estimated tonnage where a scale reading exists — controls on scale calibration and ticket reconciliation.
5. **Meet the Subtitle D compliance obligations.** Liners, leachate management, landfill-gas (methane) capture (to RNG/flare), groundwater monitoring, daily cover — operating obligations, not optional. Name the ones the operation owns.
6. **Design the safety program in — the injury rate demands it.** DOT/CDL driver rules (HOS, inspection, qualification), **hopper/blade** lockout, **backing** protocols (cameras/spotters/route design that minimizes reversing), lifting controls (ASL over manual where feasible), and hearing conservation. Safety is the operating model, not a poster.
7. **Capture it and name the flip conditions.** Record the disposal path, economics, compliance obligations, and safety controls in [`../../templates/diversion-and-cost-analysis.md`](../../templates/diversion-and-cost-analysis.md) (disposal-cost half); name the 1-2 facts that would change the path (a new transfer station, a landfill closure, a tipping-fee move).

## Worked example

> User: "We direct-haul residential MSW 45 miles to the regional landfill. Tipping fee keeps rising and drivers spend the afternoon driving. Options?"

- **Scope gate:** residential MSW = Subtitle D non-hazardous → in scope. (Had it been a hazardous stream, route OUT.)
- **Disposal path:** a **45-mile direct-haul** with collection trucks is a classic transfer-station case — tip locally into walking-floor trailers, long-haul in bulk. Model the extra handling cost per ton against the collection-truck windshield-time + fuel saved.
- **Economics:** current tipping fee ($/ton) [retrieve current] × tonnage vs the transfer-station tip + trailer haul; factor the landfill's **airspace** trajectory (a filling cell means a rising gate rate ahead).
- **Compliance:** confirm the Subtitle D obligations sit with the landfill operator; the hauler owns weigh-ticket reconciliation and manifest accuracy.
- **Safety:** the afternoon long-haul adds driver fatigue/HOS exposure — the transfer-station move also *reduces* a safety risk, not just a cost.
- **Flip condition:** if a closer landfill/transfer station opens or the tipping-fee gap narrows, revisit direct-haul.

## Guardrails

- Run the **Subtitle D vs Subtitle C** scope gate first — hazardous is OUT of scope, always routed out, never improvised.
- Landfill **airspace** is finite and depleting — never model disposal as if the cell were infinite.
- The **weigh ticket** is the source of truth — no estimated tonnage where a scale reading exists.
- Transfer-station-vs-direct-haul is a haul-economics decision — model the extra handling cost against windshield-time + fuel saved.
- **Safety is designed in** — the industry's injury rate is real; treat DOT/CDL + hopper/backing/lifting as operating design, not paperwork.
- Volatile facts (tipping fees, airspace valuations, alt-fuel incentives, statutes) carry a **retrieval date**. See [`../../knowledge/waste-recycling-patterns-2026.md`](../../knowledge/waste-recycling-patterns-2026.md).
