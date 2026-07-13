# moving-relocation-operations

> The **operator's team** for Claude Code — the two agents that run a household-goods moving company as a business and answer *"how do I quote and run this move, and is it authorized, disclosed, documented, and defensible?"* Two agents: the **moving-operations-lead** (estimating, crew & truck scheduling and dispatch, capacity/utilization, job-type mix, packing/materials) and the **moving-compliance-and-claims-specialist** (DOT/FMCSA operating authority + state licensing, tariffs, valuation coverage vs insurance, the Bill of Lading / required federal disclosures, and the claims process).

Part of the [RavenClaude](../../README.md) marketplace. Extends `ravenclaude-core`.

## What it does

| You ask | It returns |
|---|---|
| "How do I quote this 3-bedroom move — binding or hourly?" | A cube-sheet-driven estimate: cube/weight build, the estimate-type choice (binding / non-binding / not-to-exceed / hourly), local vs long-distance pricing basis, packing/materials, and a margin check |
| "How do I schedule my crews and trucks next week?" | A dispatch schedule: crew sizing to cube+access, truck assignment, local vs long-haul routing, a utilization target with overrun buffer, and the dispatch board |
| "Should I chase more interstate work or stay local hourly?" | A job-type-mix recommendation (local hourly / long-distance-interstate / corporate relocation / commercial-office) with the crew, authority, and margin implications |
| "Do I need a USDOT/MC number to move a customer across state lines?" | An authority read: interstate FMCSA operating authority (USDOT + MC) vs the state-by-state intrastate licensing variance — flagged to the licensing authority / counsel, *not legal advice* |
| "What's the difference between released value and full-value protection?" | A valuation explainer: released value (~60¢/lb, the default liability limit) vs full-value protection, how each is disclosed/priced, and why valuation is a liability level, **not** insurance |
| "A customer says we damaged their furniture — how do I handle the claim?" | A claims workflow: the filing window, the governing valuation basis, documentation, the settlement timeline, and the dispute/arbitration path — state/federal-flagged and *not legal advice* |

**Two rules it never breaks:** *build the estimate from an inventory (the cube sheet is the whole job)* and *valuation is a liability level, not insurance*. And one caveat it always states: **DOT/FMCSA authority, tariff, valuation, and licensing are regulated — this is operational guidance, not legal advice.**

## What's inside

- **2 agents** — `moving-operations-lead` (runs the job: estimating, crew & truck scheduling and dispatch, capacity/utilization, job-type mix, packing/materials) and `moving-compliance-and-claims-specialist` (runs the regulated + risk side: DOT/FMCSA authority + state licensing, tariffs, valuation vs insurance, the Bill of Lading / required federal disclosures, claims).
- **3 skills** — `build-move-estimate`, `schedule-crews-and-dispatch`, `manage-valuation-liability-and-claims`.
- **2 knowledge files** — a Mermaid moving & relocation decision tree (estimating vs dispatch/capacity vs job-type-mix vs valuation/liability vs compliance/authority vs claims, with the interstate-vs-intrastate fork) and a 2026 moving-patterns reference (estimate types, cube-sheet vs weight, released-vs-full-value valuation, FMCSA authority + USDOT/MC + intrastate variance, required federal disclosures, tariffs, van-line vs independent, moving software, lead/booking economics, seasonality, the claims process).
- **2 templates** — a move estimate & cube sheet and a valuation & claims timeline (state/federal-flagged, retrieval-dated, not-legal-advice).

## Where it sits

```
fleet-logistics             →  generic vehicle-fleet telematics / maintenance / routing   ("run the FLEET")
field-service-management    →  generic non-moving crew dispatch / work orders             ("dispatch the CREW")
freight-forwarding-sales    →  freight — LTL / FTL / international                         ("move the FREIGHT")
marketing-operations        →  lead-gen / paid-search campaigns / brand / creative        ("run the CAMPAIGN")
accounting-bookkeeping      →  the books / P&L / sales tax                                ("keep the BOOKS")
moving-relocation-operations (HERE)  →  run the moving BUSINESS: ops + compliance        ("quote & run the MOVE, keep it legal")
```

This plugin operates the moving *business* — the estimate, the crews and trucks, the job-type mix, the operating authority, the valuation, the disclosures, the claims — and stays clear of the *generic vehicle fleet* (fleet-logistics), generic *dispatch* (field-service-management), and *freight* (freight-forwarding-sales).

## Domain stance

Concept-first (cube sheet vs weight, binding / non-binding / not-to-exceed / hourly estimates, local hourly vs long-distance weight-and-distance pricing, crew/truck utilization, released-vs-full-value valuation as a liability level not insurance, the interstate-FMCSA / intrastate-state-licensing divide, the claims process), fluent across the van-line vs independent models and the moving software (**SmartMoving, MoveitPro, Elromco, Supermove**). **DOT/FMCSA operating authority, tariffs, valuation coverage, and state licensing are regulated**, the rules change, and the moving-software feature sets are volatile — every such claim carries a **state/federal and/or retrieval date**, and the authority/valuation/licensing mechanics are **operational guidance, not legal advice**: route the legal/licensing determination to counsel, the state licensing authority, and/or FMCSA.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install moving-relocation-operations@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.
