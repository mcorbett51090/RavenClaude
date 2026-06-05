# Dental practice scenarios bank

> Unverified, dated, scope-tagged narratives from real (or realistic) dental-practice consulting engagements. Enabled as part of the value-add build-out (2026-06-05).

This directory holds **scenarios** — engagement war stories of "the practice had problem X, here was the situation, these were the constraints, we tried A/B/C, D moved the number." Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with a mandatory unverified-scenario preamble (see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md))

Unlike a code-vertical scenarios bank (a 403, a token error), these are **practice-operations engagements**: a hygiene-recall leak, a case-acceptance drop, a PPO-vs-FFS mix decision, a production-per-hour capacity read. The "Resolution" is an analytical move plus a measured outcome, not a code fix.

## The schema (mirrors the marketplace 9-field scenario schema)

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: dental-practice
product: <practice-operations | case-acceptance | revenue-cycle | hygiene | finance>
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

> **Privacy:** scenarios carry **no** client-identifying info, no patient PII, no real practice names or revenue figures attributable to a named clinic. Numbers are illustrative ranges, marked `[ESTIMATE]`, or carry a public-benchmark source. This mirrors the marketplace `/wrap` scrub discipline and CLAUDE.md §2 (the team stores no patient records / PHI).

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-hygiene-recall-reactivation.md`](2026-06-05-hygiene-recall-reactivation.md) | likely-general | hygiene, recall, reappointment, reactivation, unscheduled-treatment | medium |
| [`2026-06-05-case-acceptance-presentation-fix.md`](2026-06-05-case-acceptance-presentation-fix.md) | likely-general | case-acceptance, treatment-presentation, sequencing, financial-options, conversion | medium |
| [`2026-06-05-ppo-vs-ffs-payer-mix.md`](2026-06-05-ppo-vs-ffs-payer-mix.md) | likely-general | ppo, write-off, payer-mix, fee-negotiation, ffs, effective-fee | medium |
| [`2026-06-05-production-per-hour-schedule-read.md`](2026-06-05-production-per-hour-schedule-read.md) | likely-general | production-per-hour, schedule-utilization, capacity, hygiene-production, doctor-time | medium |

## Promotion path

When ≥2 independent scenarios (different engagements / quarters) corroborate the same finding, an agent may propose promoting the lesson into [`../best-practices/`](../best-practices/) or a [`../knowledge/`](../knowledge/) decision tree. As of this bank's creation, promotion is manual — leave the scenario in place even after the rule is canonicalized (the narrative stays useful as context).

## How agents use this bank

Per [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md): surface a matching scenario only as a *secondary* source, always behind the unverified-scenario preamble, and never let a scenario override the cited knowledge bank or a licensed dentist's clinical judgment (CLAUDE.md §2).
