# Product-management scenarios bank

> Unverified, dated, scope-tagged narratives from real (or realistic) product-management engagements. Enabled as part of the value-add build-out (2026-06-05).

This directory holds **scenarios** — engagement war stories of "the team had product problem X, here was the situation, these were the constraints, we tried A/B/C, D moved the outcome." Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with a mandatory unverified-scenario preamble (see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md))

Unlike a code-vertical scenarios bank (a 403, a token error), these are **product-craft engagements**: a roadmap with no prioritization rigor, a feature shipped with no success metric, discovery skipped into low adoption, a build-vs-buy-vs-partner call. The "Resolution" is an analytical/process move plus a measured outcome, not a code fix.

## The schema (mirrors the marketplace 9-field scenario schema)

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: product-management
product: <strategy | discovery | prioritization | metrics | roadmap>
product_version: "n/a"          # non-code vertical — no product version
scope: practice-specific | segment-specific | likely-general
tags: [list of 3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Context              (segment, stage, constraints — the non-code analogue of "Permissions context")
## Attempts
## Resolution
```

> **Privacy:** scenarios carry **no** client-identifying info, no customer PII, no real company names, and no revenue figures attributable to a named org. Numbers are illustrative ranges, marked `[ESTIMATE]`, or carry a public-benchmark source. This mirrors the marketplace `/wrap` scrub discipline.

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-roadmap-thrash-no-prioritization-rigor.md`](2026-06-05-roadmap-thrash-no-prioritization-rigor.md) | likely-general | prioritization, rice, wsjf, roadmap-thrash, hippo | medium |
| [`2026-06-05-feature-shipped-without-success-metric.md`](2026-06-05-feature-shipped-without-success-metric.md) | likely-general | success-metric, outcomes, north-star, ship-to-learn, guardrail | medium |
| [`2026-06-05-discovery-skipped-low-adoption.md`](2026-06-05-discovery-skipped-low-adoption.md) | likely-general | discovery, jtbd, assumption-testing, adoption, opportunity-solution-tree | medium |
| [`2026-06-05-build-vs-buy-vs-partner-capability.md`](2026-06-05-build-vs-buy-vs-partner-capability.md) | likely-general | build-buy-partner, strategy, differentiation, opportunity-cost, capability | medium |

## Promotion path

When ≥2 independent scenarios (different engagements / quarters) corroborate the same finding, an agent may propose promoting the lesson into [`../best-practices/`](../best-practices/) or a [`../knowledge/`](../knowledge/) decision tree. As of this bank's creation, promotion is manual — leave the scenario in place even after the rule is canonicalized (the narrative stays useful as context).

## How agents use this bank

Per [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md): surface a matching scenario only as a *secondary* source, always behind the unverified-scenario preamble, and never let a scenario override the cited knowledge bank or the canonical best-practices (CLAUDE.md §2). The most-likely-to-benefit specialists — `product-strategist`, `product-discovery-lead`, `product-metrics-analyst` — should check the bank when a situation matches.
