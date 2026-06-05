# Film & video production scenarios bank

> Unverified, dated, scope-tagged narratives from real (or realistic) film/video production engagements. Enabled as part of the value-add build-out (2026-06-05).

This directory holds **scenarios** — engagement war stories of "the production had problem X, here was the situation, these were the constraints, we tried A/B/C, D moved the number." Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with a mandatory unverified-scenario preamble (see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md))

Unlike a code-vertical scenarios bank (a 403, a token error), these are **production-management engagements**: a shoot-day overage, a fixed-bid scope squeeze, a post-pipeline bottleneck, a contingency burn before wrap. The "Resolution" is an analytical / producing move plus a measured outcome, not a code fix.

## The schema (mirrors the marketplace 9-field scenario schema)

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: film-video-production
product: <budgeting | scheduling | post-production | finance | deliverables>
product_version: "n/a"          # non-code vertical — no product version
scope: production-specific | segment-specific | likely-general
tags: [list of 3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Context              (segment, size, constraints — the non-code analogue of "Permissions context")
## Attempts
## Resolution
```

> **Privacy:** scenarios carry **no** client-identifying info, no cast/crew PII, no real production titles or budget figures attributable to a named project. Numbers are illustrative ranges, marked `[ESTIMATE]`, or carry a public-benchmark source. This mirrors the marketplace `/wrap` scrub discipline and CLAUDE.md section 2 (the team stores no cast/crew records).

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-shoot-day-overtime-spiral.md`](2026-06-05-shoot-day-overtime-spiral.md) | likely-general | overtime, turnaround, shoot-day, fringe, schedule | medium |
| [`2026-06-05-fixed-bid-scope-vs-budget.md`](2026-06-05-fixed-bid-scope-vs-budget.md) | likely-general | fixed-bid, scope-creep, change-order, commercial, contingency | medium |
| [`2026-06-05-post-pipeline-delivery-slip.md`](2026-06-05-post-pipeline-delivery-slip.md) | likely-general | post-pipeline, picture-lock, vfx, critical-path, delivery | medium |
| [`2026-06-05-contingency-burn-before-wrap.md`](2026-06-05-contingency-burn-before-wrap.md) | likely-general | contingency, cost-report, burn-rate, weather-day, forecast | medium |

## Promotion path

When ≥2 independent scenarios (different engagements / quarters) corroborate the same finding, an agent may propose promoting the lesson into [`../best-practices/`](../best-practices/) or a [`../knowledge/`](../knowledge/) decision tree. As of this bank's creation, promotion is manual — leave the scenario in place even after the rule is canonicalized (the narrative stays useful as context).

## How agents use this bank

Per [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md): surface a matching scenario only as a *secondary* source, always behind the unverified-scenario preamble, and never let a scenario override the cited knowledge bank or a producer's / union representative's authority (CLAUDE.md section 2).
