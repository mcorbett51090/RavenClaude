# Frontend Engineering scenarios bank

> Unverified, dated, scope-tagged narratives from real frontend engagements. War stories of "we hit X problem, here was the situation, these were our constraints, we tried A/B/C, D worked."

This directory holds **scenarios** — field notes from real frontend work. Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a _secondary_ source — always surfaced with the mandatory unverified-scenario preamble

For the full architecture and the retrieval pattern, see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md). Canonical knowledge lives in [`../knowledge/`](../knowledge/) and `best-practices/`; scenarios never replace it.

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: frontend-engineering
product: <react | nextjs | vite | typescript | tanstack-query | generic | etc.>
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
| [`2026-06-05-hydration-mismatch-locale-date.md`](2026-06-05-hydration-mismatch-locale-date.md) | likely-general | hydration, ssr, rsc, nextjs, mismatch, date | high |
| [`2026-06-05-cls-lcp-perf-budget-regression.md`](2026-06-05-cls-lcp-perf-budget-regression.md) | likely-general | cls, lcp, core-web-vitals, perf-budget, images, fonts | high |
| [`2026-06-05-server-state-in-redux-refactor.md`](2026-06-05-server-state-in-redux-refactor.md) | likely-general | state-management, server-cache, tanstack-query, redux, refactor | high |
| [`2026-06-05-accessibility-audit-modal-focus.md`](2026-06-05-accessibility-audit-modal-focus.md) | likely-general | accessibility, focus-trap, aria, keyboard, modal, wcag | medium |

## Promotion path

When ≥2 independent scenarios (different `contributed_at` quarters, different engagements) corroborate the same finding, an agent proposes promotion to a `knowledge/` decision tree or a `best-practices/` entry. As of this bank's first version, promotion is manual and the scenarios stay in place after a rule is canonicalized — the narrative remains useful context.
