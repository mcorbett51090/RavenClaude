# platform-engineering-idp

A **Platform Engineering (IDP) specialist team** for a platform engineering lead, DevEx analyst, or eng manager accountable for developer productivity and platform adoption. It treats the platform as a product with developers as customers, paves golden paths instead of issuing mandates, measures DevEx with DORA and lead time rather than opinions, and runs the platform on SLOs and an error budget like any service.

> Inherits the [`ravenclaude-core`](../ravenclaude-core/) protocols (claim-grounding, structured output, decision review). Maturity-explicit, stack-flexible (greenfield platform | ticket-ops escape | scaling team | multi-tenant).

## What you get

| Surface | Contents |
|---|---|
| **4 agents** | `platform-eng-lead`, `golden-path-architect`, `developer-experience-analyst`, `platform-reliability-specialist` |
| **5 skills / commands** | `classify-dora` · `measure-adoption` · `design-golden-path` · `quantify-toil` · `set-platform-slos` |
| **4-file knowledge bank** | KPI glossary · unit economics · 2025–2026 context · Mermaid decision trees |
| **4 templates** | scorecard · exec readout · golden-path-spec.md · platform-slo-sheet.md |
| **1 advisory hook** | flags anti-patterns (unbaselined metric, unsourced benchmark, internal credentials/PII) in generated deliverables |
| **`scripts/platform_engineering_idp_calc.py`** | stdlib calculator — `dora` · `adoption` · `toil` |

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install platform-engineering-idp@ravenclaude
```

## Quickstart

> "We built a platform but nobody's using it — why?"

The `platform-eng-lead` scopes the problem, routes to `golden-path-architect` (or a sibling specialist), and synthesizes a ranked action plan with owners, dates, and expected metric movement.

## What it is not

a general SRE on-call rotation, a cloud-cost FinOps function, or a security-compliance authority. It does not run production incident command, set cloud budgets, or make security/compliance determinations — those route to the qualified authority.
