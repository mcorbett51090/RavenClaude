# Precision-agriculture scenarios bank

> Unverified, dated, scope-tagged narratives from real (or realistic) precision-ag / farm-operations consulting engagements. Enabled as part of the value-add build-out (2026-06-05).

This directory holds **scenarios** — engagement war stories of "the operation had problem X, here was the situation, these were the constraints, we tried A/B/C, D moved the number." Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with a mandatory unverified-scenario preamble (see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md))

Unlike a code-vertical scenarios bank (a 403, a token error), these are **farm-operations engagements**: a breakeven squeeze, a variable-rate ROI question, a nutrient-budget overspend, an irrigation-water cost, an imagery false alarm. The "Resolution" is an analytical move plus a measured outcome, not a code fix.

## The schema (mirrors the marketplace 9-field scenario schema)

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: precision-agriculture
product: <farm-economics | agronomy | precision-tech | irrigation | marketing>
product_version: "n/a"          # non-code vertical — no product version
scope: farm-specific | segment-specific | likely-general
tags: [list of 3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Context              (segment, acres, crop, constraints — the non-code analogue of "Permissions context")
## Attempts
## Resolution
```

> **Privacy:** scenarios carry **no** grower-identifying info, no farm names, no field GPS, and no revenue figures attributable to a named operation. Numbers are illustrative ranges, marked `[ESTIMATE]`, or carry a public-benchmark source with a retrieval date. This mirrors the marketplace `/wrap` scrub discipline and CLAUDE.md §2 (the team stores no grower PII).

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-breakeven-vs-input-cost-spike.md`](2026-06-05-breakeven-vs-input-cost-spike.md) | likely-general | breakeven, input-cost, corn, margin, per-acre | medium |
| [`2026-06-05-vrt-seeding-rate-roi.md`](2026-06-05-vrt-seeding-rate-roi.md) | likely-general | variable-rate, seeding, roi, zones, return-to-seed | medium |
| [`2026-06-05-nutrient-budget-overspend.md`](2026-06-05-nutrient-budget-overspend.md) | likely-general | fertility, soil-test, nitrogen, removal-rate, nutrient-budget | medium |
| [`2026-06-05-irrigation-water-cost.md`](2026-06-05-irrigation-water-cost.md) | segment-specific | irrigation, soil-moisture-sensor, water-cost, scheduling, roi | medium |
| [`2026-06-05-imagery-scouting-false-alarm.md`](2026-06-05-imagery-scouting-false-alarm.md) | likely-general | ndvi, imagery, scouting, false-alarm, ground-truth | medium |

## Promotion path

When ≥2 independent scenarios (different engagements / quarters) corroborate the same finding, an agent may propose promoting the lesson into [`../best-practices/`](../best-practices/) or a [`../knowledge/`](../knowledge/) decision tree. As of this bank's creation, promotion is manual — leave the scenario in place even after the rule is canonicalized (the narrative stays useful as context).

## How agents use this bank

Per [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md): surface a matching scenario only as a *secondary* source, always behind the unverified-scenario preamble, and never let a scenario override the cited knowledge bank or a licensed agronomist's / certified crop adviser's judgment (CLAUDE.md §2).
