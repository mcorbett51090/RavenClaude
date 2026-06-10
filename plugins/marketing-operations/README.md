# marketing-operations

A **Marketing Operations specialist team** for a marketing-ops leader, demand-gen analyst, or founder accountable for pipeline contribution, CAC efficiency, and funnel conversion. It reads MQL→SQL→opp→win as a funnel system and fixes the leaking stage, states the attribution model before reporting a number, gates spend on LTV:CAC and payback, and reports pipeline/revenue contribution rather than lead volume.

> Inherits the [`ravenclaude-core`](../ravenclaude-core/) protocols (claim-grounding, structured output, decision review). Model-explicit, motion-flexible (inbound | outbound | ABM | PLG | hybrid).

## What you get

| Surface | Contents |
|---|---|
| **4 agents** | `marketing-ops-lead`, `demand-gen-funnel-analyst`, `attribution-analytics-specialist`, `martech-campaign-architect` |
| **5 skills / commands** | `diagnose-funnel` · `size-demand` · `read-cac-ltv` · `evaluate-channel-mix` · `audit-attribution-data` |
| **4-file knowledge bank** | KPI glossary · unit economics · 2025–2026 context · Mermaid decision trees |
| **4 templates** | scorecard · exec readout · funnel-worksheet.md · channel-economics.md |
| **1 advisory hook** | flags anti-patterns (unbaselined metric, unsourced benchmark, customer/lead PII) in generated deliverables |
| **`scripts/marketingops_calc.py`** | stdlib calculator — `funnel` · `cac-ltv` · `channel-roi` |

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install marketing-operations@ravenclaude
```

## Quickstart

> "We're generating tons of leads but pipeline is flat — where's the gap?"

The `marketing-ops-lead` scopes the problem, routes to `demand-gen-funnel-analyst` (or a sibling specialist), and synthesizes a ranked action plan with owners, dates, and expected metric movement.

## What it is not

a creative/brand agency, a paid-media buying desk, or a sales/RevOps function. It does not write copy, manage ad accounts, set sales quota, or store customer/lead PII. Contract, privacy-law, and revenue-recognition questions route to the qualified authority.
