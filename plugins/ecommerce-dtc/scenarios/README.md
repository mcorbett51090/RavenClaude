# E-commerce & DTC scenarios bank

> Unverified, dated, scope-tagged narratives from real (or realistic) DTC growth-and-unit-economics engagements. Enabled as part of the value-add build-out (2026-06-05).

This directory holds **scenarios** — engagement war stories of "the brand had problem X, here was the situation, these were the constraints, we tried A/B/C, D moved the number." Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with a mandatory unverified-scenario preamble (see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md))

Unlike a code-vertical scenarios bank (a 403, a token error), these are **growth-and-unit-economics engagements**: a CAC spike, a contribution-margin leak, a checkout drop, a subscription-churn problem. The "Resolution" is an analytical move plus a measured outcome, not a code fix.

## The schema (mirrors the marketplace 9-field scenario schema)

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: ecommerce-dtc
product: <acquisition | merchandising-conversion | retention | unit-economics | returns>
product_version: "n/a"          # non-code vertical — no product version
scope: brand-specific | segment-specific | likely-general
tags: [list of 3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Context              (segment, size, constraints — the non-code analogue of "Permissions context")
## Attempts
## Resolution
```

> **Privacy:** scenarios carry **no** customer PII, no order-level data, no real brand names or revenue figures attributable to a named store. Numbers are illustrative ranges, marked `[ESTIMATE]`, or carry a public-benchmark source. This mirrors the marketplace `/wrap` scrub discipline and CLAUDE.md §2 (the team stores no customer PII).

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-cac-rising-blended-vs-incremental.md`](2026-06-05-cac-rising-blended-vs-incremental.md) | likely-general | cac, blended, incrementality, attribution, channel-mix, mer | medium |
| [`2026-06-05-contribution-margin-negative-after-returns.md`](2026-06-05-contribution-margin-negative-after-returns.md) | likely-general | contribution-margin, returns, apparel, bracketing, reverse-logistics | medium |
| [`2026-06-05-checkout-conversion-drop.md`](2026-06-05-checkout-conversion-drop.md) | likely-general | conversion, checkout, cart-abandonment, funnel, mobile | medium |
| [`2026-06-05-subscription-churn-vs-acquisition.md`](2026-06-05-subscription-churn-vs-acquisition.md) | likely-general | subscription, churn, retention, ltv, discount-only | medium |

## Promotion path

When ≥2 independent scenarios (different engagements / quarters) corroborate the same finding, an agent may propose promoting the lesson into [`../best-practices/`](../best-practices/) or a [`../knowledge/`](../knowledge/) decision tree. As of this bank's creation, promotion is manual — leave the scenario in place even after the rule is canonicalized (the narrative stays useful as context).

## How agents use this bank

Per [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md): surface a matching scenario only as a *secondary* source, always behind the unverified-scenario preamble, and never let a scenario override the cited knowledge bank or a brand's own data (CLAUDE.md §2). The most-likely-to-benefit specialists — `performance-marketing-strategist`, `merchandising-specialist`, `retention-analytics-analyst` — should check the bank when a situation matches.
