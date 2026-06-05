# Small-firm legal practice scenarios bank

> Unverified, dated, scope-tagged narratives from real (or realistic) small-firm legal-practice consulting engagements. Enabled as part of the value-add build-out (2026-06-05).

This directory holds **scenarios** — engagement war stories of "the practice had problem X, here was the situation, these were the constraints, we tried A/B/C, D moved the number." Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with a mandatory unverified-scenario preamble (see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md))

Unlike a code-vertical scenarios bank (a 403, a token error), these are **practice-operations engagements**: a realization leak, an intake/conflict miss, a trust-account reconciliation gap, a utilization/capacity squeeze. The "Resolution" is an analytical move plus a measured outcome, not a code fix.

## The schema (mirrors the marketplace 9-field scenario schema)

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: legal-small-firm
product: <practice-operations | intake | trust-accounting | finance | capacity>
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

> **Privacy:** scenarios carry **no** client confidences, no party-identifying info, no real firm names or revenue figures attributable to a named firm. Numbers are illustrative ranges, marked `[ESTIMATE]`, or carry a public-benchmark source. This mirrors the marketplace `/wrap` scrub discipline and CLAUDE.md §2 (the team stores no client confidences and forms no attorney-client relationship). Nothing in this bank is legal advice — every output is decision-support for the responsible attorney (§3 #3).

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-realization-rate-recovery.md`](2026-06-05-realization-rate-recovery.md) | likely-general | realization, write-down, billing-cadence, effective-rate, collections | medium |
| [`2026-06-05-intake-conflict-and-fit-miss.md`](2026-06-05-intake-conflict-and-fit-miss.md) | likely-general | intake, conflict-check, client-fit, scope, malpractice-risk | medium |
| [`2026-06-05-iolta-three-way-reconciliation-gap.md`](2026-06-05-iolta-three-way-reconciliation-gap.md) | likely-general | iolta, trust-accounting, three-way-reconciliation, rule-1-15, ethics | medium |
| [`2026-06-05-utilization-capacity-squeeze.md`](2026-06-05-utilization-capacity-squeeze.md) | likely-general | utilization, non-billable, capacity, delegation, hiring | medium |

## Promotion path

When ≥2 independent scenarios (different engagements / quarters) corroborate the same finding, an agent may propose promoting the lesson into [`../best-practices/`](../best-practices/) or a [`../knowledge/`](../knowledge/) decision tree. As of this bank's creation, promotion is manual — leave the scenario in place even after the rule is canonicalized (the narrative stays useful as context).

## How agents use this bank

Per [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md): surface a matching scenario only as a *secondary* source, always behind the unverified-scenario preamble, and never let a scenario override the cited knowledge bank, the applicable rules of professional conduct, or the responsible attorney's professional judgment (CLAUDE.md §2, §3 #6). Anything touching trust accounting, conflicts, confidentiality, or ethics routes to the attorney and the applicable bar rules.
