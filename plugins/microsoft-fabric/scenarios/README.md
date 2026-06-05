# Microsoft Fabric scenarios bank

> Unverified, dated, scope-tagged narratives from real (or realistic) Microsoft Fabric engagements. Enabled as part of the value-add build-out (2026-06-05) — supersedes the prior `CLAUDE.md` §8a "scenarios — TODO (planned)" placeholder.

This directory holds **scenarios** — engagement war stories of "the tenant hit problem X, here was the situation, these were the constraints, we tried A/B/C, D fixed it." Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with the mandatory unverified-scenario preamble (see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md))

Unlike a pure-code scenario (a 403, a token error), these are **Fabric platform engagements**: a capacity throttling event, a Direct Lake fallback, a OneLake medallion-modeling call, a deployment-pipeline ALM gotcha. The "Resolution" is a design/operational move plus a measured outcome, grounded in the cited Microsoft Learn docs — never a recommendation that contradicts the canonical [`../knowledge/`](../knowledge/) bank or [`../best-practices/`](../best-practices/) rules.

## The schema (the marketplace 9-field scenario schema)

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: microsoft-fabric
product: <fabric-capacity | direct-lake | onelake | data-factory | rti | warehouse | lakehouse | alm>
product_version: <"2026.05" | "n/a">    # Fabric ships monthly; date GA/preview-sensitive claims
scope: tenant-specific | sku-specific | likely-general
tags: [3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Constraints context     (capacity SKU, region, security plane, store, mode — the non-code analogue of "Permissions context")
## Attempts
## Resolution
```

> **Privacy:** scenarios carry **no** tenant-identifying info, no real workspace/capacity names, no connection strings, no service-principal IDs, and no client revenue/CU-cost figures attributable to a named tenant. Numbers are illustrative ranges or carry a public Microsoft Learn source. This mirrors the marketplace `/wrap` scrub discipline and CLAUDE.md §10 (`security-reviewer` owns any auth/secret/PII surface). Fabric ships monthly — every GA/preview-sensitive claim is dated and `[verify-at-use]` (house opinion #9).

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-capacity-cu-throttling-background-rejection.md`](2026-06-05-capacity-cu-throttling-background-rejection.md) | likely-general | capacity, cu, throttling, smoothing, background-rejection, isolation | high |
| [`2026-06-05-direct-lake-fallback-to-directquery.md`](2026-06-05-direct-lake-fallback-to-directquery.md) | likely-general | direct-lake, directquery-fallback, rls, sql-endpoint, on-onelake | high |
| [`2026-06-05-onelake-shortcut-medallion-modeling.md`](2026-06-05-onelake-shortcut-medallion-modeling.md) | likely-general | onelake, shortcut, medallion, one-copy, mirroring, gold | medium |
| [`2026-06-05-deployment-pipeline-alm-autobind-break.md`](2026-06-05-deployment-pipeline-alm-autobind-break.md) | likely-general | alm, deployment-pipeline, autobind, parameterize, git-integration, prod | medium |

## Promotion path

When ≥2 independent scenarios (different engagements / quarters) corroborate the same finding, an agent may propose promoting the lesson into [`../best-practices/`](../best-practices/) or a [`../knowledge/`](../knowledge/) decision tree. As of this bank's creation, promotion is manual — leave the scenario in place even after the rule is canonicalized (the narrative stays useful as context). Most of these scenarios *already* map to an existing best-practice rule (cited in each file's Resolution); the scenario is the field-note complement to the canonical rule, not a replacement.

## How agents use this bank

Per [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md): surface a matching scenario only as a *secondary* source, always behind the unverified-scenario preamble, and never let a scenario override the cited knowledge bank or a `security-reviewer` verdict (CLAUDE.md §10). The most-likely-to-benefit specialists — `fabric-admin` (capacity/ALM/security), `fabric-semantic-model-engineer` (Direct Lake), `fabric-architect` (OneLake topology) — check the bank when a situation matches.
