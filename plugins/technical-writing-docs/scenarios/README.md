# Technical Writing & Docs scenarios bank

> Unverified, dated, scope-tagged narratives from real documentation engagements. War stories of "the docs were X broken, here was the situation, these were our constraints, we tried A/B/C, D worked."

This directory holds **scenarios** — field notes from real docs work. Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with the mandatory unverified-scenario preamble

For the full architecture and the retrieval pattern, see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md). Canonical knowledge lives in [`../knowledge/`](../knowledge/), [`../best-practices/`](../best-practices/), and `docs/best-practices/`; scenarios never replace it.

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: technical-writing-docs
product: <diataxis | docusaurus | mkdocs | mintlify | vale | openapi | redocly | generic | etc.>
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
| [`2026-06-05-api-docs-drift-from-code.md`](2026-06-05-api-docs-drift-from-code.md) | likely-general | api-docs, drift, openapi, spec-driven, ci-gate, examples | high |
| [`2026-06-05-no-information-architecture.md`](2026-06-05-no-information-architecture.md) | likely-general | information-architecture, diataxis, navigation, search, findability | high |
| [`2026-06-05-tutorial-reference-confusion.md`](2026-06-05-tutorial-reference-confusion.md) | likely-general | diataxis, tutorial, reference, content-type, time-to-first-success | medium |
| [`2026-06-05-docs-review-bottleneck.md`](2026-06-05-docs-review-bottleneck.md) | likely-general | docs-as-code, review-bottleneck, vale, ci, style-linter, terminology | medium |

## Promotion path

When ≥2 independent scenarios (different `contributed_at` quarters, different engagements) corroborate the same finding, an agent proposes promotion to a `knowledge/` decision tree or `best-practices/` rule. As of this bank's first version, promotion is manual and the scenarios stay in place after a rule is canonicalized — the narrative remains useful context.
