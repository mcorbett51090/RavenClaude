# Idle Time Is a Fuel and Engine Cost, Not Just a Habit

**Status:** Pattern
**Domain:** Fuel management / maintenance
**Applies to:** `fleet-logistics`

---

## Why this exists

Idling is routinely described as a driver behavior problem. It is also a quantifiable fuel cost and an engine-wear accelerant that belongs in the maintenance CPM model. A diesel truck idling consumes approximately 0.8 gallons per hour [unverified — training knowledge]. A driver idling 3 hours per day across 250 working days burns roughly 600 gallons per year — at $3.80/gal, that is ~$2,280 per truck before the engine-wear premium. Fleets that manage idle time as a cost line — with telematics data and an idle threshold policy — consistently recover 1–3% of fuel spend per truck.

## How to apply

Quantify idle cost before intervening:

```
Annual idle fuel cost per truck (estimate):
  Idle hours/day × gallons/hour × operating days × diesel price/gallon
  Example: 2.5 h/day × 0.8 gal/h × 250 days × $3.80/gal = $1,900/truck/year

Fleet-level impact:
  Per-truck cost × fleet size = total recoverable fuel spend
```

Policy implementation checklist:
1. Pull telematics idle reports by driver and by lane/location (shipper docks often drive idle, not driver choice).
2. Set a fleet idle threshold (e.g., >5 min engine-on with zero speed triggers a flag).
3. Distinguish sleeper-cab idle (comfort — legitimate) from drive-cycle idle (habit — addressable with APUs or fuel-neutral alternatives).
4. Track idle % as a monthly metric alongside MPG; improvements in both compound.

**Do:**
- Attribute idle by location (shipper/receiver dock vs. rest stop vs. yard) — most actionable idle is dock-driven, which is a shipper/dispatch problem, not a driver problem.
- Include APU (auxiliary power unit) cost in the ROI calculation: an APU at ~$8,000–$12,000 [unverified — training knowledge] pays back in 2–3 years on a high-idle sleeper route.
- Report idle CPM as a separate fuel sub-metric in the CPM model.

**Don't:**
- Penalize drivers for shipper-driven idle without first routing the issue to the shipper relationship.
- Treat idle management as a compliance program rather than a cost-recovery program — the framing matters for driver buy-in.

## Edge cases / when the rule does NOT apply

Refrigerated (reefer) units run separate from the tractor engine and are managed differently — reefer idle is an operational requirement, not an addressable behavior. Extreme weather climates may make a portion of cab idle non-negotiable for driver safety; the policy threshold should reflect the climate of the operating region.

## See also

- [`../agents/fleet-maintenance-specialist.md`](../agents/fleet-maintenance-specialist.md) — owns engine-wear impact of idle on maintenance CPM.
- [`../agents/logistics-cost-analyst.md`](../agents/logistics-cost-analyst.md) — owns the idle CPM calculation and scorecard integration.
- [`./fuel-is-the-swing-variable-manage-it-dont-just-absorb-it.md`](./fuel-is-the-swing-variable-manage-it-dont-just-absorb-it.md) — idle time is one of the addressable fuel levers catalogued in that rule.

## Provenance

Fuel consumption figures are standard industry estimates (DOE/FHWA idle-reduction programs; SmartWay guidelines). CPM modeling practice is consistent with ATRI operational cost methodology.

---

_Last reviewed: 2026-06-05 by `claude`_
