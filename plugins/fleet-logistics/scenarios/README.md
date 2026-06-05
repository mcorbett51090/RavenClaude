# Fleet & logistics scenarios bank

> Unverified, dated, scope-tagged narratives from real (or realistic) fleet/logistics consulting engagements. Enabled as part of the value-add build-out (2026-06-05).

This directory holds **scenarios** — engagement war stories of "the carrier had problem X, here was the situation, these were the constraints, we tried A/B/C, D moved the number." Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with a mandatory unverified-scenario preamble (see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md))

Unlike a code-vertical scenarios bank (a 403, a token error), these are **fleet-operations engagements**: a cost-per-mile creep, an empty-mile leak, a maintenance-deferral failure, a turnover bleed, an hours-of-service compliance gap. The "Resolution" is an analytical move plus a measured outcome, not a code fix.

## The schema (mirrors the marketplace 9-field scenario schema)

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: fleet-logistics
product: <cost-analysis | dispatch-routing | maintenance | driver-retention | compliance>
product_version: "n/a"          # non-code vertical — no product version
scope: carrier-specific | segment-specific | likely-general
tags: [list of 3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Context              (segment, size, constraints — the non-code analogue of "Permissions context")
## Attempts
## Resolution
```

> **Privacy:** scenarios carry **no** client-identifying info, no driver PII, no real carrier names, no DOT/MC numbers, and no revenue figures attributable to a named carrier. Numbers are illustrative ranges, marked `[ESTIMATE]`, or carry a public-benchmark source. This mirrors the marketplace `/wrap` scrub discipline and CLAUDE.md §2 (the team stores no driver PII and is not a DOT/FMCSA authority).

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-cost-per-mile-creep-deadhead.md`](2026-06-05-cost-per-mile-creep-deadhead.md) | likely-general | cost-per-mile, deadhead, utilization, backhaul, lane-profitability | medium |
| [`2026-06-05-pm-deferral-breakdown-spiral.md`](2026-06-05-pm-deferral-breakdown-spiral.md) | likely-general | preventive-maintenance, downtime, maintenance-cpm, roadside, reactive-repair | medium |
| [`2026-06-05-driver-turnover-bleed.md`](2026-06-05-driver-turnover-bleed.md) | likely-general | driver-turnover, retention, unseated-truck, recruiting, unit-economics | medium |
| [`2026-06-05-hos-eld-compliance-gap.md`](2026-06-05-hos-eld-compliance-gap.md) | likely-general | hours-of-service, eld, fmcsa, compliance, csa-score, out-of-service | medium |

## Promotion path

When ≥2 independent scenarios (different engagements / quarters) corroborate the same finding, an agent may propose promoting the lesson into [`../best-practices/`](../best-practices/) or a [`../knowledge/`](../knowledge/) decision tree. As of this bank's creation, promotion is manual — leave the scenario in place even after the rule is canonicalized (the narrative stays useful as context).

## How agents use this bank

Per [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md): surface a matching scenario only as a *secondary* source, always behind the unverified-scenario preamble, and never let a scenario override the cited knowledge bank or a fleet/safety/legal authority's judgment (CLAUDE.md §2). HOS/ELD and DOT-compliance scenarios are decision-support only — the team is not a DOT/FMCSA authority and does not rule on hours-of-service.
