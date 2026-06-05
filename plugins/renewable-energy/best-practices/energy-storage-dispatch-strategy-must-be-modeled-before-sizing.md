# Energy Storage Dispatch Strategy Must Be Modeled Before Sizing

**Status:** Absolute rule
**Domain:** Renewable energy / battery storage
**Applies to:** `renewable-energy`

---

## Why this exists

Battery storage projects are routinely sized to a round number — "4-hour battery" or "1:1 solar-to-storage ratio" — without modeling the actual dispatch use case that drives value. A 4-hour battery providing demand-charge management for a C&I customer with a 15-minute peak window is radically different from a 4-hour battery providing energy arbitrage in a wholesale market with a 4-hour evening ramp. The same nameplate capacity generates entirely different revenue streams, degrades at different rates (deep cycles vs. shallow cycles), and is sized optimally at entirely different MWh levels depending on the dispatch strategy. Sizing before dispatch modeling picks the wrong battery.

## How to apply

Run the dispatch model before the equipment spec in four steps:

**Step 1 — Identify the value stack by use case:**

| Use case | Cycle depth | Typical daily cycles | Value driver |
|---|---|---|---|
| Demand-charge reduction (C&I) | Shallow (10–40% DoD) | 0.5–1 | Peak demand reduction ($/kW-month) |
| Energy arbitrage (wholesale) | Deep (80–95% DoD) | 1–2 | Price spread ($/MWh) |
| Frequency regulation (ancillary) | Very shallow (5–15% DoD) | 10–30 | RegD/RegA capacity payment |
| Backup power / resilience | Deep (100% DoD) | Rare | Insurance value / uptime |
| Solar self-consumption (behind-meter) | Moderate (40–70% DoD) | 1 | Retail rate arbitrage ($/kWh) |

**Step 2 — Model the dispatch, then derive the size:**

```
Storage Sizing Worksheet — [Project] [Use Case]
────────────────────────────────────────────────
Primary use case: ___
Peak shaving target (C&I): ___ kW demand reduction
  → Required discharge rate:  ___ kW (= target demand reduction)
  → Required duration:        ___ hours (= peak event duration)
  → Required capacity:        ___ kWh (= rate × duration ÷ round-trip efficiency)
  → Round-trip efficiency assumption: ___% (source: ___)

Energy arbitrage (wholesale):
  Average daily price spread: $___ /MWh (source + date: ___)
  Optimal dispatch hours/day: ___
  Required capacity:          ___ MWh
  Annual revenue estimate:    $___ (spread × capacity × cycles × days)

Step 3 — Degradation and augmentation:
  Year 1 capacity:            ___ kWh
  Annual degradation rate:    ___% (manufacturer warranty: ___% at ___ cycles)
  Year 10 effective capacity: ___ kWh
  Augmentation required:      [ ] Yes — at year ___ to maintain use-case performance
  Augmentation cost (year ___): $___  (include in pro-forma: [ ] Yes  [ ] No)

Step 4 — IRR sensitivity to sizing:
  Model at -25%, base, +25% storage size vs. same dispatch strategy
  Base IRR: ___%;  Undersized IRR: ___%  (revenue miss);  Oversized IRR: ___% (capex waste)
```

**Do:**
- Model the dispatch load profile from actual interval data (15-min or hourly) for C&I projects — synthetic load profiles significantly misestimate demand-charge savings.
- Include degradation in every dispatch model; a battery that can no longer hit the required discharge window by year 5 is undersized at year 0.
- Evaluate the value stack explicitly: a battery that does demand-charge reduction AND solar self-consumption AND limited arbitrage needs a dispatch optimization algorithm — specify it before the PPA or host agreement is signed.
- Confirm that the dispatch strategy is compatible with the ITC eligibility requirements: a standalone storage system charging predominantly from the grid is not ITC-eligible under current rules.

**Don't:**
- Size the battery as "one hour" or "four hours" without knowing the specific dispatch event duration — the same duration rating means different things in different markets.
- Ignore degradation in the economics — a battery warrantied to 80% at 3,000 cycles will not deliver the year-1 revenue model in year 8 without augmentation or re-dispatch.
- Use the battery manufacturer's claimed cycle count at maximum DoD as the production-case assumption; use the manufacturer's cycle curve at the actual DoD for the modeled dispatch.

## Edge cases / when the rule does NOT apply

Residential backup-only storage with no dispatch optimization (no solar, no TOU rate structure) does not require a dispatch model — size to the critical load circuit and the backup duration needed. Utility-scale storage participating in a single ancillary service with a defined dispatch rule set by the ISO may use the ISO dispatch rule rather than a custom model.

## See also
- [`../agents/energy-finance-analyst.md`](../agents/energy-finance-analyst.md) — builds the storage dispatch model and pro-forma.
- [`../agents/solar-project-developer.md`](../agents/solar-project-developer.md) — sequences the storage sizing relative to the solar design and offtake structure.
- [`../knowledge/renewables-economics.md`](../knowledge/renewables-economics.md) — covers storage value-stack economics and degradation modeling.

## Provenance

Codifies the storage dispatch-first sizing principle from NREL (National Renewable Energy Laboratory) storage valuation methodology and EPRI storage dispatch modeling guidance; the degradation-adjusted sizing approach is standard in Tier 1 project finance due diligence [unverified — training knowledge].

---

_Last reviewed: 2026-06-05 by `claude`_
