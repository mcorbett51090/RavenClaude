# wealth-management-ria

A **Wealth Management (RIA Practice) specialist team** for an RIA practice principal, COO, or operations lead accountable for organic growth, advisor capacity, client retention, and compliance cadence. It separates net-new flows from market appreciation as the real growth signal, segments clients by profitability not AUM alone, applies a defensible fee schedule consistently, sizes advisor capacity by households, and treats the compliance cadence as non-negotiable.

> Inherits the [`ravenclaude-core`](../ravenclaude-core/) protocols (claim-grounding, structured output, decision review). Fee-model-explicit, segment-flexible (AUM-fee | flat-fee | hybrid; mass-affluent | HNW | UHNW).

## What you get

| Surface | Contents |
|---|---|
| **4 agents** | `ria-practice-lead`, `aum-revenue-analyst`, `client-segmentation-specialist`, `compliance-cadence-specialist` |
| **5 skills / commands** | `decompose-aum-growth` · `model-fee-revenue` · `segment-client-profitability` · `size-advisor-capacity` · `track-compliance-cadence` |
| **4-file knowledge bank** | KPI glossary · unit economics · 2025–2026 context · Mermaid decision trees |
| **4 templates** | scorecard · exec readout · aum-bridge.md · client-segmentation.md |
| **1 advisory hook** | flags anti-patterns (unbaselined metric, unsourced benchmark, client financial PII) in generated deliverables |
| **`scripts/riaops_calc.py`** | stdlib calculator — `aum-revenue` · `advisor-capacity` · `client-profitability` |

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install wealth-management-ria@ravenclaude
```

## Quickstart

> "Our AUM is up nicely — but is the practice actually growing, or is it just the market?"

The `ria-practice-lead` scopes the problem, routes to `aum-revenue-analyst` (or a sibling specialist), and synthesizes a ranked action plan with owners, dates, and expected metric movement.

## What it is not

an investment-advice or portfolio-management function, a financial-planning service, or a compliance/legal authority. It does not give investment advice, recommend securities, render fiduciary determinations, or interpret SEC/state regulations. Investment, fiduciary, and SEC/state determinations route to compliance counsel.
