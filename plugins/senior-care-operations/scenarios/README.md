# Senior-care operations scenarios bank

> Unverified, dated, scope-tagged narratives from real (or realistic) senior-care operations engagements. Enabled as part of the value-add build-out (2026-06-05).

This directory holds **scenarios** — engagement war stories of "the community had problem X, here was the situation, these were the constraints, we tried A/B/C, D moved the number." Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with a mandatory unverified-scenario preamble (see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md))

Unlike a code-vertical scenarios bank (a 403, a token error), these are **operations engagements**: an occupancy slide, a staffing-to-acuity mismatch, a leaking move-in funnel, a payer-mix margin problem. The "Resolution" is an analytical move plus a measured outcome, not a code fix.

## The schema (mirrors the marketplace 9-field scenario schema)

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: senior-care-operations
product: <census | staffing | sales-funnel | finance | quality-compliance>
product_version: "n/a"          # non-code vertical — no product version
scope: community-specific | segment-specific | likely-general
tags: [list of 3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Context              (segment, size, constraints — the non-code analogue of "Permissions context")
## Attempts
## Resolution
```

> **Privacy:** scenarios carry **no** client-identifying info, no resident PHI/PII, no real community names or revenue figures attributable to a named building. Numbers are illustrative ranges, marked `[ESTIMATE]`, or carry a public-benchmark source. This mirrors the marketplace `/wrap` scrub discipline and CLAUDE.md §2 (the team stores no resident records).

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-occupancy-slide-segment-recovery.md`](2026-06-05-occupancy-slide-segment-recovery.md) | likely-general | occupancy, census, move-out, segment, sales-funnel | medium |
| [`2026-06-05-staffing-ppd-to-acuity-alignment.md`](2026-06-05-staffing-ppd-to-acuity-alignment.md) | likely-general | staffing, ppd, acuity, agency-labor, labor-cost | medium |
| [`2026-06-05-move-in-funnel-conversion-leak.md`](2026-06-05-move-in-funnel-conversion-leak.md) | likely-general | move-in, conversion, tour, inquiry, sales-funnel, lead-response | medium |
| [`2026-06-05-payer-mix-margin-rebalance.md`](2026-06-05-payer-mix-margin-rebalance.md) | likely-general | payer-mix, medicaid, medicare, private-pay, margin, snf | medium |

## Promotion path

When ≥2 independent scenarios (different engagements / quarters) corroborate the same finding, an agent may propose promoting the lesson into [`../best-practices/`](../best-practices/) or a [`../knowledge/`](../knowledge/) decision tree. As of this bank's creation, promotion is manual — leave the scenario in place even after the rule is canonicalized (the narrative stays useful as context).

## How agents use this bank

Per [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md): surface a matching scenario only as a *secondary* source, always behind the unverified-scenario preamble, and never let a scenario override the cited knowledge bank or a licensed clinician's / state surveyor's authority (CLAUDE.md §2). The most-likely-to-benefit specialists — `census-occupancy-strategist`, `senior-care-finance-analyst`, `clinical-care-compliance-specialist` — should check the bank when a situation matches.
