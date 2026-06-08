# mortgage-lending

A **Mortgage Lending Operations specialist team** for a production manager, ops leader, or owner accountable for pull-through, cycle time, capacity, and cost-to-originate. It reads pull-through as the funnel and fixes the fallout stage, ties cycle time to capacity and borrower satisfaction, manages lock/pipeline risk, holds cost-to-originate as the unit economic that survives rate cycles, and routes every compliance question to counsel.

> Inherits the [`ravenclaude-core`](../ravenclaude-core/) protocols (claim-grounding, structured output, decision review). Channel-explicit, segment-flexible (retail | wholesale | correspondent; purchase | refi | hybrid).

## What you get

| Surface | Contents |
|---|---|
| **4 agents** | `mortgage-lending-lead`, `pipeline-pullthrough-analyst`, `processing-cycle-specialist`, `compliance-quality-specialist` |
| **5 skills / commands** | `diagnose-pullthrough` · `size-cycle-capacity` · `model-cost-to-originate` · `frame-pipeline-risk` · `route-compliance` |
| **4-file knowledge bank** | KPI glossary · unit economics · 2025–2026 context · Mermaid decision trees |
| **4 templates** | scorecard · exec readout · pullthrough-funnel.md · cost-to-originate-model.md |
| **1 advisory hook** | flags anti-patterns (unbaselined metric, unsourced benchmark, borrower PII / NPI) in generated deliverables |
| **`scripts/mortgage_lending_calc.py`** | stdlib calculator — `pullthrough` · `cycle-capacity` · `cost-to-originate` |

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install mortgage-lending@ravenclaude
```

## Quickstart

> "Our pull-through is dropping and cycle time is climbing — where's the gap?"

The `mortgage-lending-lead` scopes the problem, routes to `pipeline-pullthrough-analyst` (or a sibling specialist), and synthesizes a ranked action plan with owners, dates, and expected metric movement.

## What it is not

a compliance, legal, or fair-lending authority, and not an underwriting decision-maker. It does not make credit/underwriting decisions, render TRID/ECOA/HMDA/fair-lending determinations, or store borrower PII/NPI. Compliance, legal, fair-lending, and underwriting determinations route to counsel, the compliance authority, and the licensed underwriter.
