# finops-cloud-cost

A **FinOps & Cloud Cost specialist team** for a FinOps lead, cloud cost analyst, or engineering finance partner accountable for cloud spend, allocation, and unit economics. It allocates spend before optimizing it, reads unit economics rather than the total bill, treats commitments as a portfolio decision made after rightsizing, and kills waste first.

> Inherits the [`ravenclaude-core`](../ravenclaude-core/) protocols (claim-grounding, structured output, decision review). Provider-flexible, stage-explicit (single-account startup | tagged enterprise | multi-cloud | post-commit optimization).

## What you get

| Surface | Contents |
|---|---|
| **4 agents** | `finops-lead`, `cost-allocation-analyst`, `commitment-planning-specialist`, `unit-economics-strategist` |
| **5 skills / commands** | `measure-allocation` · `read-unit-economics` · `harvest-waste` · `plan-commitments` · `forecast-and-alert` |
| **4-file knowledge bank** | KPI glossary · unit economics · 2025–2026 context · Mermaid decision trees |
| **4 templates** | scorecard · exec readout · commitment-plan.md · unit-economics-sheet.md |
| **1 advisory hook** | flags anti-patterns (unbaselined metric, unsourced benchmark, billing/account PII) in generated deliverables |
| **`scripts/finops_cloud_cost_calc.py`** | stdlib calculator — `commitment` · `unit-cost` · `rightsizing` |

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install finops-cloud-cost@ravenclaude
```

## Quickstart

> "Our cloud bill is up 40% — where do we even start?"

The `finops-lead` scopes the problem, routes to `cost-allocation-analyst` (or a sibling specialist), and synthesizes a ranked action plan with owners, dates, and expected metric movement.

## What it is not

a cloud architecture authority, an accounting/tax function, or a procurement/contract-negotiation desk. It does not design infrastructure, set GAAP cost accounting, or sign cloud contracts — those route to the qualified authority.
