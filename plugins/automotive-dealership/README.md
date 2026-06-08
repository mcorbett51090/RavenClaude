# automotive-dealership

A **Automotive Dealership Operations specialist team** for a dealer principal, general manager, or department director accountable for total gross, fixed-ops absorption, and inventory turn. It runs the store on fixed-ops not new-car gross, manages inventory days-supply and floorplan as carrying-cost cash, reads total gross per unit as front plus back, and treats service absorption as the survival metric.

> Inherits the [`ravenclaude-core`](../ravenclaude-core/) protocols (claim-grounding, structured output, decision review). Department-explicit, store-flexible (single rooftop | group | new-only | new+used | high-line).

## What you get

| Surface | Contents |
|---|---|
| **4 agents** | `dealership-operations-lead`, `sales-desking-analyst`, `fixed-ops-service-specialist`, `fi-products-specialist` |
| **5 skills / commands** | `read-days-supply` · `compute-total-gross` · `compute-absorption` · `diagnose-sales-funnel` · `frame-fi-penetration` |
| **4-file knowledge bank** | KPI glossary · unit economics · 2025–2026 context · Mermaid decision trees |
| **4 templates** | scorecard · exec readout · inventory-floorplan.md · total-gross-worksheet.md |
| **1 advisory hook** | flags anti-patterns (unbaselined metric, unsourced benchmark, customer PII) in generated deliverables |
| **`scripts/automotive_dealership_calc.py`** | stdlib calculator — `days-supply` · `absorption` · `gross-per-unit` |

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install automotive-dealership@ravenclaude
```

## Quickstart

> "New-car margins are thin — how do we make the store more profitable?"

The `dealership-operations-lead` scopes the problem, routes to `sales-desking-analyst` (or a sibling specialist), and synthesizes a ranked action plan with owners, dates, and expected metric movement.

## What it is not

an F&I legal/compliance authority, a lender, or a vehicle-valuation appraiser. It does not set F&I product pricing law, render lending or advertising-compliance determinations, or store customer PII. F&I regulatory, lending, and advertising-compliance questions route to counsel.
