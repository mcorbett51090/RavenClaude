# Skilled-trades-contracting scenarios bank

> Unverified, dated, scope-tagged narratives from real (or realistic) trade-contractor consulting engagements. Enabled as part of the value-add build-out (2026-06-05).

This directory holds **scenarios** — engagement war stories of "the contractor had problem X, here was the situation, these were the constraints, we tried A/B/C, D moved the number." Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with a mandatory unverified-scenario preamble (see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md))

Unlike a code-vertical scenarios bank (a 403, a token error), these are **contracting-operations engagements**: a job that lost money, a mispriced estimate, an underused crew, an overhead-recovery gap. The "Resolution" is an analytical move plus a measured outcome, not a code fix.

## The schema (mirrors the marketplace 9-field scenario schema)

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: skilled-trades-contracting
product: <estimating | field-operations | job-costing | pricing | dispatch>
product_version: "n/a"          # non-code vertical — no product version
scope: trade-specific | segment-specific | likely-general
tags: [list of 3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Context              (trade, segment, size, constraints — the non-code analogue of "Permissions context")
## Attempts
## Resolution
```

> **Privacy:** scenarios carry **no** customer-identifying info, no homeowner/jobsite PII, no real company names or revenue figures attributable to a named contractor. Numbers are illustrative ranges, marked `[ESTIMATE]`, or carry a public-benchmark source. This mirrors the marketplace `/wrap` scrub discipline and CLAUDE.md §2 (the team stores no customer records).

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-job-margin-erosion-change-orders.md`](2026-06-05-job-margin-erosion-change-orders.md) | likely-general | job-costing, change-order, margin-erosion, scope-creep, labor-variance | medium |
| [`2026-06-05-markup-vs-margin-pricing-correction.md`](2026-06-05-markup-vs-margin-pricing-correction.md) | likely-general | markup, margin, pricing, estimating, flat-rate | medium |
| [`2026-06-05-dispatch-utilization-improvement.md`](2026-06-05-dispatch-utilization-improvement.md) | likely-general | dispatch, billable-efficiency, utilization, scheduling, truck-stocking | medium |
| [`2026-06-05-overhead-recovery-pricing-gap.md`](2026-06-05-overhead-recovery-pricing-gap.md) | likely-general | overhead, recovery, loaded-rate, pricing, net-margin | medium |

## Promotion path

When ≥2 independent scenarios (different engagements / quarters) corroborate the same finding, an agent may propose promoting the lesson into [`../best-practices/`](../best-practices/) or a [`../knowledge/`](../knowledge/) decision tree. As of this bank's creation, promotion is manual — leave the scenario in place even after the rule is canonicalized (the narrative stays useful as context).

## How agents use this bank

Per [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md): surface a matching scenario only as a *secondary* source, always behind the unverified-scenario preamble, and never let a scenario override the cited knowledge bank or the contractor's own licensed/operational judgment (CLAUDE.md §2).
