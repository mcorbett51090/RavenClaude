# EdTech Partner Success scenarios bank

> Unverified, dated, scope-tagged narratives from real (or realistic) EdTech Partner-Success engagements. Enabled as part of the value-add build-out (2026-06-05) — this replaces the §8b "TODO (planned)" block in [`../CLAUDE.md`](../CLAUDE.md).

This directory holds **scenarios** — engagement war stories of "the partner had problem X, here was the situation, these were the constraints, we tried A/B/C, D moved the number." Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with a mandatory unverified-scenario preamble (see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md))

Unlike a code-vertical scenarios bank (a 403, a token error), these are **partner-success engagements**: a low-utilization renewal risk, an implementation slipping past time-to-value, an efficacy-data gap at renewal, an expansion blocked by champion churn. The "Resolution" is a PSM analytical move plus a measured outcome, not a code fix.

## The schema (mirrors the marketplace 9-field scenario schema)

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: edtech-partner-success
product: <onboarding | adoption | health-scoring | renewal | expansion | efficacy-outcomes | qbr>
product_version: "n/a"          # non-code vertical — no product version
scope: partner-specific | segment-specific | likely-general
tags: [list of 3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Context              (segment, size, constraints — the non-code analogue of "Permissions context")
## Attempts
## Resolution
```

> **Privacy / FERPA:** scenarios carry **no** partner-identifying info, no district / institution names, no student or family PII, and no real contract figures attributable to a named partner. Numbers are illustrative ranges, marked `[ESTIMATE]`, or carry a public-benchmark source with a retrieval date. Any hypothetical student-touching example uses **synthetic identifiers only** (CLAUDE.md §2 routing rule + the `parent-comms-jurisdictional-bear-traps.md` three-bucket model). This mirrors the marketplace `/wrap` scrub discipline.

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-low-seat-utilization-renewal-risk.md`](2026-06-05-low-seat-utilization-renewal-risk.md) | likely-general | seat-utilization, license-activation, renewal-risk, k12, evidence | medium |
| [`2026-06-05-implementation-slipping-past-time-to-value.md`](2026-06-05-implementation-slipping-past-time-to-value.md) | likely-general | onboarding, time-to-value, rostering, train-the-trainer, go-live | medium |
| [`2026-06-05-efficacy-data-gap-at-renewal.md`](2026-06-05-efficacy-data-gap-at-renewal.md) | likely-general | efficacy, outcomes, essa-evidence, renewal-defense, baseline | medium |
| [`2026-06-05-expansion-blocked-by-champion-churn.md`](2026-06-05-expansion-blocked-by-champion-churn.md) | likely-general | expansion, champion-churn, sponsor-mapping, superintendent-turnover, multi-thread | medium |

## Promotion path

When ≥2 independent scenarios (different engagements / quarters) corroborate the same finding, an agent may propose promoting the lesson into [`../best-practices/`](../best-practices/) or a [`../knowledge/`](../knowledge/) decision tree. As of this bank's creation, promotion is manual — leave the scenario in place even after the rule is canonicalized (the narrative stays useful as context).

## How agents use this bank

Per [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md): surface a matching scenario only as a *secondary* source, always behind the unverified-scenario preamble, and never let a scenario override the cited knowledge bank (`../knowledge/`), the canonical decision trees (`../knowledge/partner-success-decision-trees.md`, `../knowledge/partner-health-decline-which-play.md`), or a FERPA / privacy judgment (CLAUDE.md §2). The most-likely-to-benefit agents — `edtech-partner-success-manager`, `learning-analytics-analyst`, `success-playbook-designer`, `partner-profile-curator` — should check the bank when a situation matches.
