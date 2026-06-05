# Procurement & sourcing scenarios bank

> Unverified, dated, scope-tagged narratives from real (or realistic) procurement / strategic-sourcing engagements. Enabled as part of the value-add build-out (2026-06-05).

This directory holds **scenarios** — engagement war stories of "the function had problem X, here was the situation, these were the constraints, we tried A/B/C, D moved the number." Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with a mandatory unverified-scenario preamble (see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md))

Unlike a code-vertical scenarios bank (a 403, a token error), these are **procurement engagements**: a savings-leakage problem, a single-source supply exposure, a maverick-spend / non-compliance leak, a should-cost / TCO teardown, a supplier-scorecard gap. The "Resolution" is an analytical move plus a measured outcome, not a code fix.

## The schema (mirrors the marketplace 9-field scenario schema)

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: procurement-sourcing
product: <savings | supply-risk | spend-analytics | sourcing | category-strategy>
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

> **Privacy:** scenarios carry **no** client-identifying info, no supplier PII, no real company names, contract values, or supplier names attributable to a named client. Numbers are illustrative ranges, marked `[ESTIMATE]`, or carry a public-benchmark source. This mirrors the marketplace `/wrap` scrub discipline and CLAUDE.md §2 (the team stores no supplier PII / contracts).

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-negotiated-vs-realized-savings-leakage.md`](2026-06-05-negotiated-vs-realized-savings-leakage.md) | likely-general | savings, realization, leakage, maverick-spend, finance-baseline | medium |
| [`2026-06-05-single-source-supply-risk-dual-source.md`](2026-06-05-single-source-supply-risk-dual-source.md) | likely-general | single-source, supply-risk, dual-source, continuity, bottleneck | medium |
| [`2026-06-05-maverick-spend-noncompliance.md`](2026-06-05-maverick-spend-noncompliance.md) | likely-general | maverick-spend, compliance, tail-spend, contract-coverage, p2p | medium |
| [`2026-06-05-should-cost-tco-teardown.md`](2026-06-05-should-cost-tco-teardown.md) | likely-general | should-cost, tco, unit-price, negotiation, leverage | medium |

## Promotion path

When ≥2 independent scenarios (different engagements / quarters) corroborate the same finding, an agent may propose promoting the lesson into [`../best-practices/`](../best-practices/) or a [`../knowledge/`](../knowledge/) decision tree. As of this bank's creation, promotion is manual — leave the scenario in place even after the rule is canonicalized (the narrative stays useful as context).

## How agents use this bank

Per [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md): surface a matching scenario only as a *secondary* source, always behind the unverified-scenario preamble, and never let a scenario override the cited knowledge bank or the Finance-agreed baseline (CLAUDE.md §2, §3 #3).
