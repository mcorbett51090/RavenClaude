# hotel-hospitality-operations

A **Hotel & Hospitality Operations specialist team** for a general manager, revenue manager, or owner accountable for RevPAR, GOPPAR, and guest satisfaction. It optimizes RevPAR as the product of ADR and occupancy not one alone, manages channel mix at net rate, reads the booking pace curve, staffs labor to occupancy by hours-per-occupied-room, and scores profit on GOPPAR.

> Inherits the [`ravenclaude-core`](../ravenclaude-core/) protocols (claim-grounding, structured output, decision review). Segment-explicit, property-flexible (select-service | full-service | resort | independent | branded).

## What you get

| Surface | Contents |
|---|---|
| **4 agents** | `hotel-operations-lead`, `revenue-management-analyst`, `labor-productivity-specialist`, `guest-experience-specialist` |
| **5 skills / commands** | `read-revpar` · `compare-channels` · `read-booking-pace` · `size-labor` · `link-experience-revenue` |
| **4-file knowledge bank** | KPI glossary · unit economics · 2025–2026 context · Mermaid decision trees |
| **4 templates** | scorecard · exec readout · revpar-channel.md · labor-productivity.md |
| **1 advisory hook** | flags anti-patterns (unbaselined metric, unsourced benchmark, guest PII) in generated deliverables |
| **`scripts/hotel_hospitality_operations_calc.py`** | stdlib calculator — `revpar` · `channel-cost` · `labor` |

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install hotel-hospitality-operations@ravenclaude
```

## Quickstart

> "Occupancy is up but profit isn't — where's it going?"

The `hotel-operations-lead` scopes the problem, routes to `revenue-management-analyst` (or a sibling specialist), and synthesizes a ranked action plan with owners, dates, and expected metric movement.

## What it is not

a brand-standard compliance authority, a labor-law authority, or a STR/comp-set data vendor. It does not set franchise brand standards, render wage-and-hour or labor-law determinations, or store guest PII. Labor-law, brand-contract, and ADA/legal questions route to the qualified authority.
