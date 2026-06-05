# AWS Cloud scenarios bank

> Unverified, dated, scope-tagged narratives from real (or realistic) AWS engagements. Enabled as part of the value-add build-out (2026-06-05).

This directory holds **scenarios** — field notes of "we hit problem X on AWS, here was the situation, these were the constraints, we tried A/B/C, D resolved it." Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with the mandatory unverified-scenario preamble (see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md))

These are **cloud/infra engagements**: an over-permissioned IAM role, a cost spike, a connectivity failure, a public-exposure finding. The "Resolution" is an architectural/operational move plus a verifiable outcome — not a code fix. Canonical guidance still lives in [`../knowledge/`](../knowledge/) and [`../best-practices/`](../best-practices/); scenarios never replace it.

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: aws-cloud
product: <iam | vpc | s3 | finops | organizations | ec2 | lambda | ecs | eks | generic>
product_version: "n/a"          # AWS is a continuously-deployed platform — no product version
scope: account-specific | region-specific | likely-general
tags: [3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Context              (estate shape, account model, constraints — the cloud analogue of "Permissions context")
## Attempts
## Resolution
```

> **Privacy:** scenarios carry **no** account IDs, ARNs with real account numbers, access keys, real bucket names, or customer-identifying info. Numbers are illustrative ranges or marked `[ESTIMATE]`. This mirrors the marketplace `/wrap` scrub discipline; anything touching a real credential, finding, or account routes to `ravenclaude-core/security-reviewer`.

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-over-permissioned-role-wildcard.md`](2026-06-05-over-permissioned-role-wildcard.md) | likely-general | iam, least-privilege, wildcard, access-analyzer, permission-boundary | high |
| [`2026-06-05-nat-gateway-cost-spike.md`](2026-06-05-nat-gateway-cost-spike.md) | likely-general | finops, nat-gateway, vpc-endpoints, data-transfer, cost-spike | high |
| [`2026-06-05-cross-account-vpc-connectivity-failure.md`](2026-06-05-cross-account-vpc-connectivity-failure.md) | likely-general | vpc, transit-gateway, routing, security-group, connectivity | medium |
| [`2026-06-05-public-s3-bucket-exposure.md`](2026-06-05-public-s3-bucket-exposure.md) | likely-general | s3, public-access, block-public-access, data-exposure, scp | high |

## Promotion path

When ≥2 independent scenarios (different engagements / quarters) corroborate the same finding, an agent may propose promoting the lesson into [`../best-practices/`](../best-practices/) or a [`../knowledge/`](../knowledge/) decision tree. Promotion is manual — leave the scenario in place even after the rule is canonicalized (the narrative stays useful as context).

## How agents use this bank

Per [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md): surface a matching scenario only as a *secondary* source, always behind the unverified-scenario preamble, and never let a scenario override the cited knowledge bank or `security-reviewer`'s verdict on a posture finding. The most-likely-to-benefit specialists — `aws-iam-identity-engineer`, `aws-network-engineer`, `aws-ops-finops-engineer` — should check the bank when a situation matches.
