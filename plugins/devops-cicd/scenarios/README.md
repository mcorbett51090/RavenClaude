# DevOps & CI/CD scenarios bank

> Unverified, dated, scope-tagged narratives from real delivery-pipeline engagements. War stories of "we hit X problem, here was the situation, these were our constraints, we tried A/B/C, D worked."

This directory holds **scenarios** — field notes from real CI/CD work. Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a _secondary_ source — always surfaced with the mandatory unverified-scenario preamble

For the full architecture and the retrieval pattern, see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md). Canonical knowledge lives in [`../knowledge/`](../knowledge/) and `docs/best-practices/`; scenarios never replace it.

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: devops-cicd
product: <github-actions | gitlab-ci | argo-cd | flux | docker | generic | etc.>
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
| [`2026-06-05-flaky-pipeline-stabilization.md`](2026-06-05-flaky-pipeline-stabilization.md) | likely-general | flaky-tests, required-checks, quarantine, retry, ci-trust | high |
| [`2026-06-05-slow-build-cache-strategy.md`](2026-06-05-slow-build-cache-strategy.md) | likely-general | build-cache, cache-key, docker-layer, monorepo, ci-speed | high |
| [`2026-06-05-canary-rollback-no-health-signal.md`](2026-06-05-canary-rollback-no-health-signal.md) | likely-general | canary, rollback, slo, health-gate, progressive-delivery | medium |
| [`2026-06-05-secrets-in-ci-leak-remediation.md`](2026-06-05-secrets-in-ci-leak-remediation.md) | likely-general | secrets, oidc, leaked-credential, rotation, supply-chain | high |

## Promotion path

When ≥2 independent scenarios (different `contributed_at` quarters, different engagements) corroborate the same finding, an agent proposes promotion to a `knowledge/` decision tree or `docs/best-practices/`. As of this bank's first version, promotion is manual and the scenarios stay in place after a rule is canonicalized — the narrative remains useful context.
