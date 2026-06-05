# Process-improvement scenarios bank

> Unverified, dated, scope-tagged narratives from real (or realistic) Lean Six Sigma engagements. Enabled as part of the value-add build-out (2026-06-05).

This directory holds **scenarios** — engagement war stories of "the process had problem X, here was the situation, these were the constraints, we tried A/B/C, D moved the number." Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with a mandatory unverified-scenario preamble (see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md))

Unlike a code-vertical scenarios bank (a 403, a token error), these are **process-improvement engagements**: a capability study that fails its threshold, a control chart triggering tampering, a DMAIC stuck at Analyze, a control plan that didn't hold, a value-stream bottleneck attacked in the wrong place. The "Resolution" is an analytical move plus a measured outcome, not a code fix.

## The schema (mirrors the marketplace 9-field scenario schema)

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: process-improvement
product: <dmaic | spc-capability | lean-vsm | control-plan | root-cause>
product_version: "n/a"          # non-code vertical — no product version
scope: practice-specific | segment-specific | likely-general
tags: [list of 3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Context              (process, sector, constraints — the non-code analogue of "Permissions context")
## Attempts
## Resolution
```

> **Privacy:** scenarios carry **no** client-identifying info, no proprietary process data, no real company names or revenue figures attributable to a named org. Numbers are illustrative ranges, marked `[ESTIMATE]`, or carry a public-benchmark/standard source. This mirrors the marketplace `/wrap` scrub discipline and the team's no-confidential-operational-data posture.

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-capability-study-fails-threshold.md`](2026-06-05-capability-study-fails-threshold.md) | likely-general | capability, cpk, centering, spread, spc | medium |
| [`2026-06-05-control-chart-tampering.md`](2026-06-05-control-chart-tampering.md) | likely-general | spc, tampering, common-cause, over-adjustment, deming | medium |
| [`2026-06-05-dmaic-stuck-at-analyze.md`](2026-06-05-dmaic-stuck-at-analyze.md) | likely-general | dmaic, analyze, root-cause, hypothesis-test, statistics-seam | medium |
| [`2026-06-05-control-plan-didnt-hold.md`](2026-06-05-control-plan-didnt-hold.md) | likely-general | control-plan, sustain, regression, owner, standard-work | medium |
| [`2026-06-05-vsm-wrong-constraint.md`](2026-06-05-vsm-wrong-constraint.md) | likely-general | vsm, constraint, bottleneck, lead-time, theory-of-constraints | medium |

## Promotion path

When ≥2 independent scenarios (different engagements / quarters) corroborate the same finding, an agent may propose promoting the lesson into [`../best-practices/`](../best-practices/) or a [`../knowledge/`](../knowledge/) decision tree. As of this bank's creation, promotion is manual — leave the scenario in place even after the rule is canonicalized (the narrative stays useful as context).

## How agents use this bank

Per [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md): surface a matching scenario only as a *secondary* source, always behind the unverified-scenario preamble, and never let a scenario override the cited knowledge bank or the statistics seam to `applied-statistics` (CLAUDE.md §8). The most-likely-to-benefit personas — `lean-six-sigma-blackbelt` and `process-analyst` — should check the bank when a situation matches.
