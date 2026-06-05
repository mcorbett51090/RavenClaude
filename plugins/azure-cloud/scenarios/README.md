# Azure Cloud scenarios bank

> Unverified, dated, scope-tagged narratives from real Azure engagements. War stories of "we hit X problem, here was the estate, these were our constraints, we tried A/B/C, D worked."

This directory holds **scenarios** — field notes from real Azure infrastructure & platform work. Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with the mandatory unverified-scenario preamble

For the full architecture and the retrieval pattern, see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md). Canonical knowledge lives in [`../knowledge/`](../knowledge/) and `docs/best-practices/`; scenarios never replace it. Azure ships constantly — every volatile capability/SKU/limit in a scenario is dated and marked `[verify-at-use]`, and identity/network-security findings still route to `ravenclaude-core/security-reviewer` (the team's mandatory seam).

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: azure-cloud
product: <entra | azure-rbac | cost-management | networking | landing-zone | storage | key-vault | generic | etc.>
product_version: <"2026.05" | "n/a" | "unknown">
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
| [`2026-06-05-entra-over-privileged-owner-assignment.md`](2026-06-05-entra-over-privileged-owner-assignment.md) | likely-general | entra, rbac, owner, pim, least-privilege | high |
| [`2026-06-05-cost-spike-log-analytics-and-orphans.md`](2026-06-05-cost-spike-log-analytics-and-orphans.md) | likely-general | finops, cost-management, log-analytics, rightsizing, orphaned | high |
| [`2026-06-05-private-endpoint-dns-resolution-failure.md`](2026-06-05-private-endpoint-dns-resolution-failure.md) | likely-general | private-endpoint, private-dns, hub-spoke, nsg, key-vault | high |
| [`2026-06-05-workloads-before-landing-zone-retrofit.md`](2026-06-05-workloads-before-landing-zone-retrofit.md) | likely-general | landing-zone, caf, management-group, subscription-vending, governance | medium |

## Promotion path

When ≥2 independent scenarios (different `contributed_at` quarters, different engagements) corroborate the same finding, an agent proposes promotion to a `knowledge/` decision tree or `docs/best-practices/`. As of this bank's first version, promotion is manual and the scenarios stay in place after a rule is canonicalized — the narrative remains useful context.
