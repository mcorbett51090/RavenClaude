# API Engineering scenarios bank

> Unverified, dated, scope-tagged narratives from real API-engineering engagements. War stories of "we shipped/found X problem, here was the situation, these were our constraints, we tried A/B/C, D worked."

This directory holds **scenarios** — field notes from real API design / build / secure / test / operate work. Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with the mandatory unverified-scenario preamble

For the full architecture and the retrieval pattern, see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md). Canonical knowledge lives in [`../knowledge/`](../knowledge/) and [`../best-practices/`](../best-practices/); scenarios never replace it, and never override a `ravenclaude-core/security-reviewer` verdict.

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: api-engineering
product: <rest-openapi | graphql | grpc | webhooks | asyncapi | generic | etc.>
product_version: <"2026.04" | "unknown">
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
| [`2026-06-05-breaking-change-shipped-as-additive.md`](2026-06-05-breaking-change-shipped-as-additive.md) | likely-general | versioning, breaking-change, tolerant-reader, enum, contract-drift | high |
| [`2026-06-05-offset-pagination-deep-page-collapse.md`](2026-06-05-offset-pagination-deep-page-collapse.md) | likely-general | pagination, cursor, offset, keyset, rate-limit, performance | high |
| [`2026-06-05-bola-idor-on-nested-resource.md`](2026-06-05-bola-idor-on-nested-resource.md) | likely-general | bola, idor, owasp-api1, authorization, jwt, multi-tenant | high |
| [`2026-06-05-webhook-retries-without-idempotency.md`](2026-06-05-webhook-retries-without-idempotency.md) | likely-general | webhooks, idempotency, retries, signature, at-least-once | high |

These four map to the lifecycle the team owns: **design** (versioning a breaking change), **build** (cursor pagination), **secure** (BOLA/IDOR — escalate the verdict to `security-reviewer`), and the producer side of **operate** (at-least-once webhooks). Each ends with a cross-reference to the canonical knowledge tree + best-practice it complements.

## Promotion path

When ≥2 independent scenarios (different `contributed_at` quarters, different engagements) corroborate the same finding, an agent proposes promotion to a `knowledge/` decision tree or `best-practices/` rule. As of this bank's first version, promotion is manual and the scenarios stay in place after a rule is canonicalized — the narrative remains useful context. A security scenario never auto-promotes into a verdict; the control may be canonicalized, but the acceptability call stays with `ravenclaude-core/security-reviewer`.
