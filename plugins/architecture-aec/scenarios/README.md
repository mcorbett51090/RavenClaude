# Architecture / AEC scenarios bank

> Unverified, dated, scope-tagged narratives from real (or realistic) architecture/AEC engagements. Enabled as part of the value-add build-out (2026-06-05).

This directory holds **scenarios** — engagement war stories of "the project/firm had problem X, here was the situation, these were the constraints, we tried A/B/C, D moved the number." Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with a mandatory unverified-scenario preamble (see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md))

Unlike a code-vertical scenarios bank (a 403, a token error), these are **practice-and-project engagements**: an RFI/submittal backlog delaying a schedule, change-order creep eroding margin, a design-coordination clash driving rework, a delivery-method selection. The "Resolution" is an analytical move plus a measured outcome, not a code fix. Code/life-safety judgment always routes to the licensed professional of record (CLAUDE.md §2, §3 #7).

## The schema (mirrors the marketplace 9-field scenario schema)

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: architecture-aec
product: <project-delivery | construction-documents | firm-economics | design-phase | scope-management>
product_version: "n/a"          # non-code vertical — no product version
scope: project-specific | segment-specific | likely-general
tags: [list of 3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Context              (segment, size, constraints — the non-code analogue of "Permissions context")
## Attempts
## Resolution
```

> **Privacy:** scenarios carry **no** client-identifying info, no owner/project names, no real fees or contract values attributable to a named firm or project. Numbers are illustrative ranges, marked `[ESTIMATE]`, or carry a public-benchmark source. This mirrors the marketplace `/wrap` scrub discipline and CLAUDE.md §2 (the team stores no client records).

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-rfi-submittal-backlog-schedule-slip.md`](2026-06-05-rfi-submittal-backlog-schedule-slip.md) | likely-general | rfi, submittal, turnaround, schedule, coordination, ca | medium |
| [`2026-06-05-change-order-creep-margin-erosion.md`](2026-06-05-change-order-creep-margin-erosion.md) | likely-general | change-order, scope-creep, additional-services, margin, asa | medium |
| [`2026-06-05-design-coordination-clash-rework.md`](2026-06-05-design-coordination-clash-rework.md) | likely-general | coordination, clash, constructability, rework, mep, 50-95-review | medium |
| [`2026-06-05-delivery-method-selection-cmar.md`](2026-06-05-delivery-method-selection-cmar.md) | likely-general | delivery-method, cmar, design-build, gmp, estimate-class | medium |

## Promotion path

When ≥2 independent scenarios (different engagements / quarters) corroborate the same finding, an agent may propose promoting the lesson into [`../best-practices/`](../best-practices/) or a [`../knowledge/`](../knowledge/) decision tree. As of this bank's creation, promotion is manual — leave the scenario in place even after the rule is canonicalized (the narrative stays useful as context).

## How agents use this bank

Per [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md): surface a matching scenario only as a *secondary* source, always behind the unverified-scenario preamble, and never let a scenario override the cited knowledge bank or a licensed architect/engineer's professional judgment (CLAUDE.md §2, §3 #7).
