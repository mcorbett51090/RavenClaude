# QA & Test Automation scenarios bank

> Unverified, dated, scope-tagged narratives from real test-automation engagements. War stories of "we hit X problem, here was the situation, these were our constraints, we tried A/B/C, D worked."

This directory holds **scenarios** — field notes from real QA / test-automation work. Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with the mandatory unverified-scenario preamble

For the full architecture and the retrieval pattern, see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md). Canonical knowledge lives in [`../knowledge/`](../knowledge/) and `docs/best-practices/`; scenarios never replace it.

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: qa-test-automation
product: <playwright | cypress | jest | pytest | stryker | pact | generic | etc.>
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
| [`2026-06-05-flaky-test-quarantine-graveyard.md`](2026-06-05-flaky-test-quarantine-graveyard.md) | likely-general | flaky, quarantine, ci-signal, retry, determinism, ownership | high |
| [`2026-06-05-ice-cream-cone-slow-suite.md`](2026-06-05-ice-cream-cone-slow-suite.md) | likely-general | test-pyramid, ice-cream-cone, e2e, slow-suite, feedback-loop, parallelization | high |
| [`2026-06-05-contract-test-drift.md`](2026-06-05-contract-test-drift.md) | likely-general | contract-test, pact, provider-verification, api-seam, integration, ci-gating | medium |
| [`2026-06-05-coverage-gaming-no-assertions.md`](2026-06-05-coverage-gaming-no-assertions.md) | likely-general | coverage, mutation-testing, coverage-gaming, assertions, test-quality, ci-gating | high |

## Promotion path

When ≥2 independent scenarios (different `contributed_at` quarters, different engagements) corroborate the same finding, an agent proposes promotion to a `knowledge/` decision tree or `docs/best-practices/`. As of this bank's version, promotion is manual and the scenarios stay in place after a rule is canonicalized — the narrative remains useful context.
