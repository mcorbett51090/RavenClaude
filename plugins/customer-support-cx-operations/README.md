# customer-support-cx-operations

A **Customer Support & CX Operations specialist team** for a support-ops leader, CX manager, or founder accountable for cost-to-serve, SLA attainment, and customer satisfaction. It deflects with self-service before adding headcount, staffs to forecast volume and target occupancy rather than a fixed agent:ticket ratio, reads CSAT/NPS segmented not blended, and treats backlog and SLA as a flow of arrivals against handle capacity.

> Inherits the [`ravenclaude-core`](../ravenclaude-core/) protocols (claim-grounding, structured output, decision review). Channel-explicit, scale-flexible (email | chat | voice | self-service | omnichannel).

## What you get

| Surface | Contents |
|---|---|
| **4 agents** | `support-ops-lead`, `ticket-deflection-analyst`, `queue-staffing-specialist`, `csat-quality-strategist` |
| **5 skills / commands** | `model-deflection` · `size-staffing` · `project-backlog` · `read-satisfaction` · `design-qa-program` |
| **4-file knowledge bank** | KPI glossary · unit economics · 2025–2026 context · Mermaid decision trees |
| **4 templates** | scorecard · exec readout · staffing-worksheet.md · csat-quality-readout.md |
| **1 advisory hook** | flags anti-patterns (unbaselined metric, unsourced benchmark, customer PII) in generated deliverables |
| **`scripts/supportops_calc.py`** | stdlib calculator — `staffing` · `deflection` · `sla-backlog` |

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install customer-support-cx-operations@ravenclaude
```

## Quickstart

> "Our queue is backing up and SLAs are slipping — do we just hire more agents?"

The `support-ops-lead` scopes the problem, routes to `ticket-deflection-analyst` (or a sibling specialist), and synthesizes a ranked action plan with owners, dates, and expected metric movement.

## What it is not

a live help desk, a product-bug triage team, or a contact-center telephony vendor. It does not answer customer tickets, write KB articles, configure the phone system, or store customer PII. Refund/contract/warranty and privacy-law determinations route to the qualified authority.
