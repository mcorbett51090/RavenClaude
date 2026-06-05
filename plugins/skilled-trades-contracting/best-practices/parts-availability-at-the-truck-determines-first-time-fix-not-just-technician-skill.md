# Parts Availability at the Truck Determines First-Time-Fix, Not Just Technician Skill

**Status:** Pattern
**Domain:** Skilled trades contracting / field operations
**Applies to:** `skilled-trades-contracting`

---

## Why this exists

First-time-fix rate is often treated as a technician competency metric — the tech either knew how to fix it or didn't. In practice, the single most common cause of a callback or a same-day return trip is a missing part, not a missing skill. A tech who diagnoses correctly but doesn't carry the part has to return — and that return trip is a free truck roll, a scheduling disruption, and a customer experience failure. Truck stock — what is on each service vehicle, at what replenishment threshold, and how it is managed — directly determines first-time-fix rate independent of technician skill level. A poorly stocked truck is a built-in callback machine.

## How to apply

Manage truck stock as a structured inventory system with par levels, not as whatever happens to be left from the last job:

```
Truck Stock Audit — Vehicle [#] Technician: [Name] Date: [YYYY-MM-DD]
──────────────────────────────────────────────────────────────────────
Category          │ Item                        │ Par qty │ Current │ Reorder?
──────────────────┼─────────────────────────────┼─────────┼─────────┼────────
Capacitors        │ Run capacitor, 5μF–50μF std │ 5 ea    │         │
(HVAC)            │ Start capacitor, 88–108μF   │ 2 ea    │         │
                  │ Dual-run capacitor combo     │ 3 ea    │         │
──────────────────┼─────────────────────────────┼─────────┼─────────┼────────
Contactors (HVAC) │ 1-pole, 2-pole standard      │ 3 ea    │         │
──────────────────┼─────────────────────────────┼─────────┼─────────┼────────
Electrical        │ Breakers (common amperages)  │ 2 ea    │         │
                  │ Wire connectors, terminals   │ assorted│         │
──────────────────┼─────────────────────────────┼─────────┼─────────┼────────
Fittings / valves │ Common sizes for trade       │ [set]   │         │
──────────────────┼─────────────────────────────┼─────────┼─────────┼────────
Safety / PPE      │ Gloves, glasses, respirator  │ 1 set   │         │
──────────────────┼─────────────────────────────┼─────────┼─────────┼────────
Consumables       │ Wire nuts, tape, lubricant   │ min set │         │
```

**First-time-fix root cause analysis (for each callback):**

| Job # | Tech | Callback reason | Missing part? | Part name | Stocked next time? |
|---|---|---|---|---|---|
| | | | Y / N | | Y / N |

**Do:**
- Set truck-stock par levels based on actual job data — pull 6 months of parts-used reports from the job-management system and stock to the top 80% of most-used items by frequency.
- Audit truck stock weekly (or at the Monday morning pull-up) — missing parts tend to accumulate silently between audits.
- Track "parts not on truck" as a separate callback reason code in the dispatch/CRM system — it isolates the supply problem from the skill problem and creates a data trail for par-level adjustments.
- Assign the cost of a callback to the truck-stock budget line, not the labor budget, when the root cause is a missing part — the financial accountability drives the stocking behavior.

**Don't:**
- Blame the tech for a callback caused by a missing part that was not on the vehicle and not available at the supply house in a reasonable time window.
- Set truck stock purely on historical average usage without adjusting for seasonal demand — an HVAC truck stocked for shoulder-season repair volume will run short on capacitors and contactors during a summer heat wave.
- Ignore shrink and theft in truck stock — a truck that should have a part and doesn't is a trust-and-accountability issue as much as a replenishment issue; weekly audits surface it.

## Edge cases / when the rule does NOT apply

Commercial service contractors doing project work (new installs, large replacements) typically work from job-specific material lists pulled to the site in advance — truck stock par levels are less relevant than the job-staging and procurement process. Specialty trade contractors (refrigeration, high-voltage, specialty gas) with low call volume and high-value, low-frequency parts may find that stocking from a central supply chain is more economical than truck stock — the principle still applies, but the mechanism is warehouse-pull rather than truck-stocked par.

## See also
- [`../agents/field-operations-specialist.md`](../agents/field-operations-specialist.md) — owns dispatch, truck utilization, and first-time-fix metrics.
- [`../agents/trade-business-analyst.md`](../agents/trade-business-analyst.md) — tracks the callback rate and its cost impact in job costing.
- [`../knowledge/trades-economics.md`](../knowledge/trades-economics.md) — covers first-time-fix rate economics and callback cost quantification.

## Provenance

Codifies the truck-stock-driven first-time-fix discipline from ACCA and ServiceTitan/Hatch field-service management training; par-level management from actual call data is the standard recommendation in trade contractor business coaching programs [unverified — training knowledge].

---

_Last reviewed: 2026-06-05 by `claude`_
