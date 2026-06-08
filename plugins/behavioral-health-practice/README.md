# behavioral-health-practice

A **Behavioral Health Practice specialist team** for a practice administrator, clinical operations lead, or owner-clinician accountable for access, utilization, documentation compliance, and margin. It manages no-shows as a flow not an accident, reads intake-to-first-appointment access time as the conversion lever, ties documentation to both compliance and billing, staffs caseload to demand, and reads payer mix as the margin driver.

> Inherits the [`ravenclaude-core`](../ravenclaude-core/) protocols (claim-grounding, structured output, decision review). Setting-explicit, modality-flexible (in-person | telehealth | hybrid; solo | group | clinic).

## What you get

| Surface | Contents |
|---|---|
| **4 agents** | `behavioral-health-practice-lead`, `intake-access-analyst`, `clinical-documentation-compliance-specialist`, `payer-billing-specialist` |
| **5 skills / commands** | `manage-no-show-flow` · `shorten-access-time` · `audit-documentation-billing` · `size-caseload` · `model-payer-mix` |
| **4-file knowledge bank** | KPI glossary · unit economics · 2025–2026 context · Mermaid decision trees |
| **4 templates** | scorecard · exec readout · no-show-recovery-plan.md · payer-mix-margin-model.md |
| **1 advisory hook** | flags anti-patterns (unbaselined metric, unsourced benchmark, patient PHI) in generated deliverables |
| **`scripts/behavioral_health_practice_calc.py`** | stdlib calculator — `no-show` · `caseload` · `payer-mix` |

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install behavioral-health-practice@ravenclaude
```

## Quickstart

> "Our schedule looks full but revenue and access are both slipping — where's the gap?"

The `behavioral-health-practice-lead` scopes the problem, routes to `intake-access-analyst` (or a sibling specialist), and synthesizes a ranked action plan with owners, dates, and expected metric movement.

## What it is not

an EHR, a clinical authority, or a legal/compliance authority. It does not diagnose, set treatment plans, make medical-necessity determinations, or store patient PHI. Clinical, licensing, and legal/compliance determinations route to the licensed clinician, the licensing board, or counsel.
