# Cannabis operations scenarios bank

> Unverified, dated, scope-tagged narratives from real (or realistic) cannabis-operations consulting engagements. Enabled as part of the value-add build-out (2026-06-05).

This directory holds **scenarios** — engagement war stories of "the operator had problem X, here was the situation, these were the constraints, we tried A/B/C, D moved the number." Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with a mandatory unverified-scenario preamble (see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md))

Unlike a code-vertical scenarios bank (a 403, a token error), these are **operations engagements**: a track-and-trace reconciliation break, a 280E COGS-allocation gap, a thin-margin store, a failed-lab-test yield hit. The "Resolution" is an analytical move plus a measured outcome, not a code fix.

## The schema (mirrors the marketplace 9-field scenario schema)

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: cannabis-operations
product: <seed-to-sale | compliance | retail | finance | cultivation>
product_version: "n/a"          # non-code vertical — no product version
scope: state-specific | segment-specific | likely-general
tags: [list of 3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Context              (segment, state, size, constraints — the non-code analogue of "Permissions context")
## Attempts
## Resolution
```

> **Privacy:** scenarios carry **no** client-identifying info, no license numbers, no real operator names or revenue figures attributable to a named business. Numbers are illustrative ranges, marked `[ESTIMATE]`, or carry a public-benchmark source. This mirrors the marketplace `/wrap` scrub discipline and CLAUDE.md §2 (the team stores no client records, no PII).

## State-specificity (the cannabis twist on `scope`)

Cannabis rules **change at the state line** (CLAUDE.md §3 #3), so the `scope` field carries an extra burden here: a `state-specific` scenario (e.g. "Colorado requires daily retail reconciliation") must **not** be generalized to another state. A `likely-general` scenario captures a pattern that holds across most states (e.g. "paper-only inventory counts can't survive a track-and-trace audit"), but the *thresholds and corrective steps* inside it are still `[verify-at-use]` against the specific state's regulator.

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-metrc-reconciliation-break.md`](2026-06-05-metrc-reconciliation-break.md) | likely-general | metrc, track-and-trace, reconciliation, discrepancy, audit | medium |
| [`2026-06-05-280e-cogs-allocation-gap.md`](2026-06-05-280e-cogs-allocation-gap.md) | likely-general | 280e, cogs, 471, effective-tax-rate, cpa | medium |
| [`2026-06-05-dispensary-margin-discount-spiral.md`](2026-06-05-dispensary-margin-discount-spiral.md) | likely-general | margin, basket, discounting, category-mix, turns | medium |
| [`2026-06-05-failed-lab-test-yield-hit.md`](2026-06-05-failed-lab-test-yield-hit.md) | segment-specific | testing, remediation, microbial, yield, cultivation | medium |

## Promotion path

When ≥2 independent scenarios (different engagements / quarters) corroborate the same finding, an agent may propose promoting the lesson into [`../best-practices/`](../best-practices/) or a [`../knowledge/`](../knowledge/) decision tree. As of this bank's creation, promotion is manual — leave the scenario in place even after the rule is canonicalized (the narrative stays useful as context).

## How agents use this bank

Per [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md): surface a matching scenario only as a *secondary* source, always behind the unverified-scenario preamble, and never let a scenario override the cited knowledge bank, the operator's qualified cannabis counsel/CPA, or a state regulator's actual rule (CLAUDE.md §2, §3 #3).
