# Terraform & IaC scenarios bank

> Unverified, dated, scope-tagged narratives from real infrastructure-as-code engagements. War stories of "we hit X problem, here was the situation, these were our constraints, we tried A/B/C, D worked."

This directory holds **scenarios** — field notes from real Terraform/OpenTofu work. Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with the mandatory unverified-scenario preamble

For the full architecture and the retrieval pattern, see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md). Canonical knowledge lives in [`../knowledge/`](../knowledge/) and `best-practices/`; scenarios never replace it. A state-mutating operation in any scenario (`import`, `state rm`, `state mv`, force-unlock, destroy) is **high-blast** and routes to the operator's review per the Capability Grounding Protocol — the narrative is context, not an auto-runnable recipe.

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: terraform-iac
product: <terraform | opentofu | terragrunt | s3-backend | gcs-backend | azurerm-backend | opa-conftest | generic | etc.>
product_version: <"1.9" | "unknown">
scope: tenant-specific | version-specific | likely-general
tags: [3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Constraints context
## Attempts
## Resolution
```

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-state-drift-import-recovery.md`](2026-06-05-state-drift-import-recovery.md) | likely-general | drift, import, out-of-band, codify, plan-review | high |
| [`2026-06-05-backend-migration-state-lock.md`](2026-06-05-backend-migration-state-lock.md) | likely-general | backend-migration, state-lock, force-unlock, remote-state, locking | high |
| [`2026-06-05-destroy-blast-radius-plan-review.md`](2026-06-05-destroy-blast-radius-plan-review.md) | likely-general | destroy, blast-radius, plan-review, state-isolation, lifecycle | high |
| [`2026-06-05-secrets-in-state-remediation.md`](2026-06-05-secrets-in-state-remediation.md) | likely-general | secrets-in-state, remediation, rotation, encryption, sensitive | medium |

## Promotion path

When ≥2 independent scenarios (different `contributed_at` quarters, different engagements) corroborate the same finding, an agent proposes promotion to a `knowledge/` decision tree or `best-practices/`. As of this bank's first version, promotion is manual and the scenarios stay in place after a rule is canonicalized — the narrative remains useful context.
