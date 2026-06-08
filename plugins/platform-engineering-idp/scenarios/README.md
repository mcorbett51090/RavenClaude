# Platform Engineering & IDP scenarios bank

> Unverified, dated, scope-tagged narratives from real platform-engineering engagements. War stories
> of "we hit X problem, here was the situation, these were our constraints, we tried A/B/C, D worked."

This directory holds **scenarios** — field notes from real platform work. Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a _secondary_ source — always surfaced with the mandatory
  unverified-scenario preamble

For the full architecture and the retrieval pattern, see
[`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md).
Canonical knowledge lives in [`../knowledge/`](../knowledge/) and `docs/best-practices/`; scenarios
never replace it.

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: platform-engineering-idp
product: <backstage | port | crossplane | argo-cd | generic | etc.>
product_version: <"2026.04" | "unknown">
scope: tenant-specific | version-specific | likely-general
tags: [3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Context
## Attempts
## Resolution
```

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-08-low-portal-adoption.md`](2026-06-08-low-portal-adoption.md) | likely-general | backstage, adoption, portal, catalog-freshness, devex | high |
| [`2026-06-08-golden-path-became-a-cage.md`](2026-06-08-golden-path-became-a-cage.md) | likely-general | golden-path, escape-hatch, shadow-platform, paved-road | high |
| [`2026-06-08-ticket-driven-self-service.md`](2026-06-08-ticket-driven-self-service.md) | likely-general | self-service, crossplane, guardrails, service-desk, infra | medium |
| [`2026-06-08-vanity-platform-metrics.md`](2026-06-08-vanity-platform-metrics.md) | likely-general | devex, dora, space, vanity-metrics, adoption-funnel | high |

## Promotion path

When ≥2 independent scenarios (different `contributed_at` quarters, different engagements) corroborate
the same finding, an agent proposes promotion to a `knowledge/` decision tree or `docs/best-practices/`.
Promotion is manual and the scenarios stay in place after a rule is canonicalized — the narrative
remains useful context.
