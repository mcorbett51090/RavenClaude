# pharmacy-operations

A **Pharmacy Operations specialist team** for a pharmacy manager, PIC, or operations leader accountable for throughput, safety, inventory, margin, and adherence/star metrics. It holds fill throughput and verification safety as both the job, reads days-on-hand as tied-up cash and stockout risk, computes the real margin after acquisition cost and DIR fees, treats adherence as outcomes and star ratings, and staffs to script volume plus clinical-service time.

> Inherits the [`ravenclaude-core`](../ravenclaude-core/) protocols (claim-grounding, structured output, decision review). Setting-explicit, mix-flexible (community | retail-chain | specialty | 340B; high-volume | clinical-services).

## What you get

| Surface | Contents |
|---|---|
| **4 agents** | `pharmacy-operations-lead`, `fill-workflow-analyst`, `inventory-reimbursement-specialist`, `adherence-clinical-specialist` |
| **5 skills / commands** | `size-throughput-staffing` · `compute-real-margin` · `balance-inventory` · `translate-adherence` · `protect-dispensing-safety` |
| **4-file knowledge bank** | KPI glossary · unit economics · 2025–2026 context · Mermaid decision trees |
| **4 templates** | scorecard · exec readout · staffing-safety-model.md · real-margin-model.md |
| **1 advisory hook** | flags anti-patterns (unbaselined metric, unsourced benchmark, patient PHI) in generated deliverables |
| **`scripts/pharmacy_operations_calc.py`** | stdlib calculator — `throughput-staffing` · `margin` · `adherence` |

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install pharmacy-operations@ravenclaude
```

## Quickstart

> "Our fill volume is up but margin and our star measures are slipping — where's the gap?"

The `pharmacy-operations-lead` scopes the problem, routes to `fill-workflow-analyst` (or a sibling specialist), and synthesizes a ranked action plan with owners, dates, and expected metric movement.

## What it is not

a clinical authority or an EHR. It does not make dispensing or clinical decisions, render drug-therapy or substitution judgments, or store patient PHI. Dispensing, clinical, and drug-therapy determinations route to the licensed pharmacist.
