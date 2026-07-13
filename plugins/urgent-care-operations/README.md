# urgent-care-operations

> The **operator's team** for Claude Code — the two agents that run a walk-in / episodic urgent care center as a business and answer *"how do I move patients through this center, and how do I earn every dollar each visit can?"* Two agents: the **urgent-care-operations-lead** (patient throughput and door-to-door time, split-flow/fast-track, staffing to the demand curve, ancillary services, scope of service, multi-site) and the **urgent-care-revenue-and-payer-specialist** (payer mix and in-network contracting, occupational-medicine employer contracts, visit-level economics, self-pay/price transparency).

Part of the [RavenClaude](../../README.md) marketplace. Extends `ravenclaude-core`.

## What it does

| You ask | It returns |
|---|---|
| "My wait times are killing my reviews — how do I fix throughput?" | A throughput plan: door-to-door time segmented (door-to-triage, triage-to-provider, provider-to-discharge), a split-flow/fast-track design, and the demand-curve staffing that follows — attack the longest segment, not headcount |
| "How do I staff to the afternoon and respiratory-season surge?" | A provider + MA/tech staffing matrix matched to the intraday and seasonal demand curve, with provider productivity (patients/provider-hour) and the trough/peak trade-off |
| "How do I win and price occupational-medicine employer contracts?" | An occ-med line plan: the employer sales motion, the pre-employment-physical / drug-screen / injury-care / workers'-comp menu, pricing, scheduling, and the capacity it demands — treated as its own high-margin business |
| "What should my payer mix be, and why is revenue-per-visit flat?" | A payer-mix read + in-network contracting priorities, and a revenue-per-visit diagnosis across the three drivers (E/M level distribution, ancillary capture, contracted rate) — with the coding/billing call handed to medical-revenue-cycle |
| "Should I add on-site x-ray or a POCT lab?" | An ancillary-services decision: capex, staffing, scope, and throughput-time cost against the revenue-per-visit and in-house-retention payback |
| "How do I set self-pay pricing?" | A transparent, defensible self-pay / price-transparency schedule set against the local market |

**Three rules it never breaks:** *door-to-door time is the product* (segment it and attack the longest segment before adding staff), *occupational medicine is a distinct high-margin contracted line* (sold, scheduled, and capacitized on its own), and *payer mix is destiny for the acute line* (read the mix and contracts before chasing volume). And one caveat it always states: **this is operational and economic guidance — clinical protocols, coding/billing determinations, and licensing questions are flagged to a professional, not decided here.**

## What's inside

- **2 agents** — `urgent-care-operations-lead` (runs the center: throughput/door-to-door time, split-flow/fast-track, demand-curve staffing, ancillary services, scope of service, multi-site) and `urgent-care-revenue-and-payer-specialist` (runs the money: payer mix and in-network contracting, occ-med employer contracts, visit economics, self-pay/price transparency).
- **3 skills** — `optimize-throughput-and-staffing`, `structure-payer-and-occmed-contracts`, `design-ancillary-services-and-scope`.
- **2 knowledge files** — a Mermaid urgent-care operations decision tree (throughput vs staffing-model vs ancillary/scope vs payer/occ-med vs multi-site, with sub-branches) and a 2026 urgent-care-patterns reference (door-to-door benchmarks, provider productivity, demand-curve staffing, split-flow, occ-med, POCT/x-ray, EMR/PM platforms, UCA, payer/contracting, self-pay/price transparency).
- **2 templates** — a throughput & staffing plan and a payer & occ-med contract plan.

## Where it sits

```
medical-revenue-cycle       →  CPT/E/M coding · claims · denials · medical-necessity   ("determine the CODE & the CLAIM")
behavioral-health-practice  →  therapy / psychiatry practice operations                ("run the BEHAVIORAL-HEALTH practice")
senior-care-operations      →  residential senior living / assisted living / SNF       ("operate the RESIDENTIAL-SENIOR facility")
insurance-life-health-benefits → employee-benefits / health-plan design                ("design the BENEFIT plan")
accounting-bookkeeping      →  the books / P&L                                         ("keep the BOOKS")
urgent-care-operations (HERE) → run the urgent-care BUSINESS: throughput + revenue     ("operate the CENTER & earn its visits")
```

This plugin operates the urgent-care *business* — the throughput, the staffing to the demand curve, the occ-med line, the payer mix, the visit economics, the ancillary/scope decisions — and stays clear of the *revenue-cycle mechanics* (medical-revenue-cycle), the *behavioral-health* variant (behavioral-health-practice), and the *residential-senior* variant (senior-care-operations).

## Domain stance

Concept-first (door-to-door time and its segments, split-flow/fast-track, staffing to the intraday/seasonal demand curve, provider productivity, occupational medicine as a distinct high-margin contracted line, payer mix and in-network contracting, revenue-per-visit as E/M-distribution × ancillary-capture × contracted-rate, ancillary/scope decisions, self-pay/price transparency), fluent across the urgent-care EMR/PM platforms (**Experity — the Practice Velocity / DocuTAP lineage — and Athenahealth**) and the industry benchmarks (**Urgent Care Association / UCA**). **This is advisory only:** clinical protocols route to the medical director / a clinician, coding and billing determinations route to `medical-revenue-cycle`, and licensing / corporate-practice-of-medicine / contract-law questions route to counsel — every EMR/PM feature, UCA benchmark, occ-med price, payer norm, and regulatory rule carries a **retrieval date** and is re-verified before a client commitment.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install urgent-care-operations@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.
