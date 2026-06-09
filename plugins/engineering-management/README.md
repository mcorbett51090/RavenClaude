# engineering-management

An **Engineering Management specialist team** for an engineering manager, team lead, or director accountable for a software team's people, throughput, and codebase health. It runs the craft a non-technical manager can't do for an engineering team: structured 1:1s, calibrated growth and performance reviews, hiring loops, healthy on-call and flow, and tech-debt-vs-roadmap trade-offs — with DORA used as a *health signal to improve the system*, never an individual stack-rank weapon.

> Inherits the [`ravenclaude-core`](../ravenclaude-core/) protocols (claim-grounding, structured output, decision review). Domain-neutral (any software team), situation-explicit (new-EM | growing-team | underperformance | reorg | tech-debt-vs-roadmap). Deepens — does not replace — [`people-operations-hr`](../people-operations-hr/) and [`project-management`](../project-management/).

## What you get

| Surface | Contents |
|---|---|
| **4 agents** | `engineering-manager-lead`, `people-and-growth-manager`, `delivery-and-execution-manager`, `technical-health-manager` |
| **5 skills / commands** | `run-one-on-one` · `write-performance-review` · `design-hiring-loop` · `improve-team-flow` · `decide-tech-debt` |
| **4-file knowledge bank** | KPI glossary (DORA/flow/people) · economics · 2025–2026 frameworks context · Mermaid decision trees |
| **4 templates** | 1:1 agenda · growth plan · perf-review · tech-debt decision memo |
| **1 advisory hook** | flags anti-patterns (a verdict-not-hypothesis about a person, a velocity-ranked individual, an unsourced benchmark) in generated deliverables |
| **`scripts/engineering_management_calc.py`** | stdlib calculator — `oncall-load` · `attrition-cost` · `tech-debt` |

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install engineering-management@ravenclaude
```

## Quickstart

> "I just became an EM of a 6-person team that keeps missing dates and one person is struggling — where do I start?"

The `engineering-manager-lead` scopes the problem (is this a people, delivery, or technical-health question?), routes to the right specialist, and synthesizes a ranked plan with owners, dates, and expected change — every claim about a person framed as a hypothesis to test, never a verdict.

## What it is not

an HR/legal authority, a substitute for a real human conversation, or an IC architect. It does not make termination/legal/comp determinations or own the technical design itself — those route to the qualified authority (`people-operations-hr` for HR/legal; `ravenclaude-core/architect` for the architecture). Management deliverables about a real person are **drafts for a human to own**, never autonomous verdicts.
