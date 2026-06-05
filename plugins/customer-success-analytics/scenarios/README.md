# Customer-success-analytics scenarios bank

> Unverified, dated, scope-tagged narratives from real (or realistic) CS-analytics consulting engagements. Enabled as part of the value-add build-out (2026-06-05).

This directory holds **scenarios** — engagement war stories of "the team had problem X, here was the situation, these were the constraints, we tried A/B/C, D moved the number." Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with a mandatory unverified-scenario preamble (see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md))

Unlike a code-vertical scenarios bank (a 403, a token error), these are **CS-analytics engagements**: a health score that doesn't predict churn, an NRR number masking logo loss, a renewal forecast that missed, a false-positive risk tier, a usage-data identity gap that routes to the `data-platform` seam. The "Resolution" is an analytical / modeling move plus a measured outcome, not a code fix.

## The schema (mirrors the marketplace 9-field scenario schema)

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: customer-success-analytics
product: <health-tier | retention-metrics | renewal-workflow | signal-design | identity-seam>
product_version: "n/a"          # non-code domain layer — no product version
scope: account-specific | segment-specific | likely-general
tags: [list of 3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Context              (segment, book size, constraints — the non-code analogue of "Permissions context")
## Attempts
## Resolution
```

> **Privacy:** scenarios carry **no** client-identifying info, no account/contact PII, no real company names or revenue figures attributable to a named customer. Numbers are illustrative ranges, marked `[ESTIMATE]`, or carry a public-benchmark source. This mirrors the marketplace `/wrap` scrub discipline and the plugin's no-raw-PII house opinions (CLAUDE.md §4 #11, §4 #7).

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-health-score-not-predicting-churn.md`](2026-06-05-health-score-not-predicting-churn.md) | likely-general | health-score, lagging-signal, back-test, false-confidence, retune | medium |
| [`2026-06-05-nrr-masking-logo-churn.md`](2026-06-05-nrr-masking-logo-churn.md) | likely-general | nrr, grr, logo-churn, expansion-concentration, board-metric | medium |
| [`2026-06-05-renewal-forecast-miss-single-thread.md`](2026-06-05-renewal-forecast-miss-single-thread.md) | likely-general | renewal-forecast, single-thread, decision-maker, champion-silence, commit | medium |
| [`2026-06-05-false-positive-risk-tier-segment.md`](2026-06-05-false-positive-risk-tier-segment.md) | segment-specific | false-positive, segment-override, threshold, alert-fatigue, recalibrate | medium |
| [`2026-06-05-usage-data-identity-gap-data-platform-seam.md`](2026-06-05-usage-data-identity-gap-data-platform-seam.md) | likely-general | identity-resolution, usage-data, data-platform-seam, bridge-xref, null-not-zero | high |

## Promotion path

When ≥2 independent scenarios (different engagements / quarters) corroborate the same finding, an agent may propose promoting the lesson into [`../best-practices/`](../best-practices/) or a [`../knowledge/`](../knowledge/) decision tree. As of this bank's creation, promotion is manual — leave the scenario in place even after the rule is canonicalized (the narrative stays useful as context).

## How agents use this bank

Per [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md): surface a matching scenario only as a *secondary* source, always behind the unverified-scenario preamble, and never let a scenario override the cited knowledge bank or a `best-practices/` rule. The most-likely-to-benefit agents — `cs-analytics-architect`, `churn-signal-analyst` — should check the bank when a situation matches.
