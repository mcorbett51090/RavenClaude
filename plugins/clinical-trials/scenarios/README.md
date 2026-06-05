# Clinical trials scenarios bank

> Unverified, dated, scope-tagged narratives from real (or realistic) clinical-trial consulting engagements. Enabled as part of the value-add build-out (2026-06-05).

This directory holds **scenarios** — engagement war stories of "the trial had problem X, here was the situation, these were the constraints, we tried A/B/C, D moved the number." Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with a mandatory unverified-scenario preamble (see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md))

Unlike a code-vertical scenarios bank (a 403, a token error), these are **clinical-operations engagements**: an enrollment shortfall, a protocol-deviation pattern, a monitoring-plan gap, an IRB/IND submission deficiency. The "Resolution" is an analytical / operational move plus a measured outcome, not a code fix.

## The schema (mirrors the marketplace 9-field scenario schema)

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: clinical-trials
product: <protocol-feasibility | recruitment | site-activation | monitoring | regulatory-submission | retention>
product_version: "n/a"          # non-code vertical — no product version
scope: trial-specific | segment-specific | likely-general
tags: [list of 3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Context              (phase, therapeutic area, constraints — the non-code analogue of "Permissions context")
## Attempts
## Resolution
```

> **Privacy:** scenarios carry **no** sponsor/CRO-identifying info, no patient PHI, no real site names, no compound names, and no revenue/contract figures attributable to a named organization. Numbers are illustrative ranges, marked `[ESTIMATE]`, or carry a public-benchmark source. This mirrors the marketplace `/wrap` scrub discipline and CLAUDE.md §2 (the team stores no patient PHI and is not an EDC/CTMS).

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-enrollment-shortfall-recovery.md`](2026-06-05-enrollment-shortfall-recovery.md) | likely-general | enrollment, recruitment-funnel, rescue, eligibility, site-activation | medium |
| [`2026-06-05-protocol-deviation-capa.md`](2026-06-05-protocol-deviation-capa.md) | likely-general | protocol-deviation, capa, gcp, monitoring, root-cause | medium |
| [`2026-06-05-risk-based-monitoring-plan.md`](2026-06-05-risk-based-monitoring-plan.md) | likely-general | risk-based-monitoring, ich-e6r3, centralized-monitoring, sdv, quality-by-design | medium |
| [`2026-06-05-irb-submission-gaps.md`](2026-06-05-irb-submission-gaps.md) | likely-general | irb, ind, informed-consent, submission-readiness, clinical-hold | medium |

## Promotion path

When ≥2 independent scenarios (different engagements / quarters) corroborate the same finding, an agent may propose promoting the lesson into [`../best-practices/`](../best-practices/) or a [`../knowledge/`](../knowledge/) decision tree. As of this bank's creation, promotion is manual — leave the scenario in place even after the rule is canonicalized (the narrative stays useful as context).

## How agents use this bank

Per [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md): surface a matching scenario only as a *secondary* source, always behind the unverified-scenario preamble, and never let a scenario override the cited knowledge bank or a sponsor's medical/regulatory authority (CLAUDE.md §2). The most-likely-to-benefit specialists — `clinical-operations-manager`, `protocol-design-specialist`, `regulatory-submissions-specialist` — should check the bank when a situation matches.
