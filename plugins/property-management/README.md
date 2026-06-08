# property-management

A **Property Management Operations specialist team** for a property manager, regional manager, or asset manager accountable for occupancy, NOI, and resident retention. It reads occupancy as a leasing funnel plus renewals not a point number, treats delinquency as cash with an aging clock, manages unit-turn time as both a cost and a retention lever, and scores the asset on NOI not gross rent.

> Inherits the [`ravenclaude-core`](../ravenclaude-core/) protocols (claim-grounding, structured output, decision review). Asset-class-explicit, portfolio-flexible (single asset | small portfolio | institutional | mixed-use).

## What you get

| Surface | Contents |
|---|---|
| **4 agents** | `property-management-lead`, `occupancy-leasing-analyst`, `maintenance-operations-specialist`, `noi-financial-analyst` |
| **5 skills / commands** | `build-noi` · `project-occupancy` · `diagnose-leasing-funnel` · `quantify-turn-loss` · `age-delinquency` |
| **4-file knowledge bank** | KPI glossary · unit economics · 2025–2026 context · Mermaid decision trees |
| **4 templates** | scorecard · exec readout · noi-bridge.md · occupancy-flow.md |
| **1 advisory hook** | flags anti-patterns (unbaselined metric, unsourced benchmark, tenant PII) in generated deliverables |
| **`scripts/property_management_calc.py`** | stdlib calculator — `noi` · `occupancy-rev` · `turn-time` |

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install property-management@ravenclaude
```

## Quickstart

> "Our occupancy looks fine but NOI is soft — where's the leak?"

The `property-management-lead` scopes the problem, routes to `occupancy-leasing-analyst` (or a sibling specialist), and synthesizes a ranked action plan with owners, dates, and expected metric movement.

## What it is not

a real-estate broker, a landlord-tenant legal authority, or an appraisal function. It does not sign leases, render fair-housing or eviction legal determinations, or store tenant PII. Landlord-tenant law, fair-housing, and lease-enforcement questions route to the qualified authority.
