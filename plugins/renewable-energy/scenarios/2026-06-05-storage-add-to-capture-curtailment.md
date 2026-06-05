---
scenario_id: 2026-06-05-storage-add-to-capture-curtailment
contributed_at: 2026-06-05
plugin: renewable-energy
product: storage
product_version: "n/a"
scope: likely-general
tags: [storage, bess, curtailment, dispatch, hybrid]
confidence: medium
reviewed: false
---

## Problem

A solar project in a high-penetration zone was seeing midday production **curtailed** (clipped or paid near-zero/negative) and the developer wanted to "add a battery to capture it." The risk: sizing the battery on a flat $/kWh rule of thumb and a hand-wave "store the curtailed energy" thesis, without modeling the actual dispatch value, round-trip losses, and degradation that decide whether the BESS pays (CLAUDE.md §3 #7 — storage changes the economics; value the dispatch, not just the kWh).

## Context

- Segment: utility-scale solar + co-located storage (DC- or AC-coupled hybrid) in a curtailment-prone, high-spread market.
- Constraint: a battery's value is **dispatch-specific** — arbitrage (charge cheap/clipped midday, discharge at the evening peak), curtailment recapture, capacity, and ancillary, each with different revenue predictability. Curtailment recapture only pays if there's a **price spread** to discharge into; storing energy that has nowhere profitable to go is cost, not value. Round-trip efficiency (~85–95% [verify-at-use]) and cycle-driven degradation eat into every stored kWh, and standalone/co-located BESS is ITC-eligible (~30% base, through the 2033+ tech-neutral window) [verify-at-use], which materially changes the net cost.
- The developer was reasoning "we curtail X MWh, so a battery that holds X MWh recovers X × price" — ignoring the spread requirement, the RTE haircut, and the degradation reserve.

## Attempts

- Tried: defined the **primary dispatch use-case first** (here: midday-clipping recapture + evening-peak arbitrage) before sizing, per the storage-dispatch decision tree — because the use-case, not the curtailed volume, sizes the battery. Outcome: the value driver was the *peak spread*, not the raw curtailed MWh.
- Tried: modeled dispatch value **net of round-trip efficiency and a cycle-degradation reserve**, and netted the ITC against the BESS capital. Outcome: the honest net value was lower than the flat-$/kWh thesis but still positive at the modeled spread.
- Tried: sized the battery to the **economic** discharge window (the hours the spread actually pays), not to total curtailment, and checked the interconnection limit (a co-located battery can ease the export constraint that *caused* the curtailment). Outcome: a smaller, spread-sized battery beat the "hold all the curtailed energy" battery on IRR.

## Resolution

The project added a **spread-sized battery dispatched for clipping-recapture + peak arbitrage**, netted of RTE and degradation and with the ITC modeled explicitly — not a flat-$/kWh battery sized to total curtailed volume. The output was a dated dispatch model showing the value by use-case, the RTE/degradation haircut, and the net-of-ITC cost (CLAUDE.md §3 #7).

**Action for the next consultant hitting this pattern:** **value the dispatch, not the curtailed kWh — define the primary use-case, then size to the economic discharge window net of round-trip efficiency and degradation, with the ITC modeled explicitly.** A battery only "captures curtailment" if there's a price spread to discharge into; absent the spread it's cost. Run the storage-dispatch use-case tree first — see [`../knowledge/renewables-decision-trees.md`](../knowledge/renewables-decision-trees.md) "Storage Dispatch Use-Case Selection" and the new [`../knowledge/renewables-add-storage-decision-tree.md`](../knowledge/renewables-add-storage-decision-tree.md). The storage lane is owned by [`energy-finance-analyst`](../agents/energy-finance-analyst.md) with a grid assist from [`grid-interconnection-specialist`](../agents/grid-interconnection-specialist.md).

**Sources (retrieved 2026-06-05):**
- NREL — *Cost Projections for Utility-Scale Battery Storage* (2025 benchmark, ~$334/kWh 4-hour): https://docs.nrel.gov/docs/fy25osti/93281.pdf
- Crux — *Battery Energy Storage System tax credits* (standalone BESS ITC eligibility): https://www.cruxclimate.com/insights/battery-energy-storage-system-tax-credits
- CAISO — *2024 Special Report on Battery Storage* (curtailment-recapture / dispatch context): https://www.caiso.com/documents/2024-special-report-on-battery-storage-may-29-2025.pdf

BESS capital cost, round-trip efficiency, degradation, the ITC rate/window, and market spreads are technology- and market-specific and move quarterly — treat every figure as `[verify-at-use]` and ground in the project's market and supplier quotes (§3 #7, #8).
