# Nonprofit fundraising scenarios bank

> Unverified, dated, scope-tagged narratives from real (or realistic) development/fundraising consulting engagements. Added as part of the value-add build-out (2026-06-05).

This directory holds **scenarios** — engagement war stories of "the development office had problem X, here was the situation, these were the constraints, we tried A/B/C, D moved the number." Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with a mandatory unverified-scenario preamble (see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md))

Unlike a code-vertical scenarios bank (a 403, a token error), these are **development-office engagements**: a retention slide, a major-gift pipeline that won't fill, an annual-fund renewal slump, a campaign goal nobody has stress-tested. The "Resolution" is an analytical move plus a measured outcome, not a code fix.

## The schema (mirrors the marketplace 9-field scenario schema)

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: nonprofit-fundraising
product: <annual-fund | major-gifts | grants | events | capital-campaign | analytics>
product_version: "n/a"          # non-code vertical — no product version
scope: practice-specific | segment-specific | likely-general
tags: [list of 3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Context              (segment, size, constraints — the non-code analogue of "Permissions context")
## Attempts
## Resolution
```

> **Privacy:** scenarios carry **no** donor-identifying info, no PII, no real org names or gift figures attributable to a named nonprofit. Numbers are illustrative ranges, marked `[ESTIMATE]`, or carry a public-benchmark source. This mirrors the marketplace `/wrap` scrub discipline and CLAUDE.md §2 (the team stores no donor records).

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-donor-retention-turnaround.md`](2026-06-05-donor-retention-turnaround.md) | likely-general | retention, leaky-bucket, first-time-donor, acknowledgment, cohort | medium |
| [`2026-06-05-major-gift-pipeline-build.md`](2026-06-05-major-gift-pipeline-build.md) | likely-general | major-gifts, moves-management, portfolio, pipeline, qualification | medium |
| [`2026-06-05-annual-fund-renewal-lift.md`](2026-06-05-annual-fund-renewal-lift.md) | likely-general | annual-fund, renewal, upgrade, segmentation, lybunt-sybunt | medium |
| [`2026-06-05-campaign-feasibility-gift-pyramid.md`](2026-06-05-campaign-feasibility-gift-pyramid.md) | likely-general | capital-campaign, feasibility, gift-pyramid, gift-range, lead-gift | medium |

## Promotion path

When ≥2 independent scenarios (different engagements / quarters) corroborate the same finding, an agent may propose promoting the lesson into [`../best-practices/`](../best-practices/) or a [`../knowledge/`](../knowledge/) decision tree. As of this bank's creation, promotion is manual — leave the scenario in place even after the rule is canonicalized (the narrative stays useful as context).

## How agents use this bank

Per [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md): surface a matching scenario only as a *secondary* source, always behind the unverified-scenario preamble, and never let a scenario override the cited knowledge bank or a development director's documented judgment (CLAUDE.md §2). The most-likely-to-benefit specialists — `major-gifts-strategist`, `nonprofit-finance-analyst`, `development-lead` — should check the bank when a situation matches.
