# Experimentation & growth-engineering scenarios bank

> Unverified, dated, scope-tagged narratives from real (or realistic) experimentation engagements. War stories of "the test looked like X, here was the situation, these were the constraints, we tried A/B/C, D was the move that worked."

This directory holds **scenarios** — field notes from experimentation / feature-flag / instrumentation work. Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with the **mandatory unverified-scenario preamble** (see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md))

These are **apparatus + trustworthiness** engagements — a peeking false-positive, an underpowered test, a sample-ratio mismatch, a guardrail regression — not pure code fixes. The "Resolution" is usually a process/plumbing move plus a measured outcome. Canonical guidance lives in [`../knowledge/`](../knowledge/) and [`../best-practices/`](../best-practices/); scenarios never replace it. **Statistical-validity verdicts (significance, the "is the lift real" call) belong to `applied-statistics`** — these scenarios stop at the apparatus boundary (CLAUDE.md §2 #1, §3).

## The 9-field schema (mirrors the marketplace scenario schema)

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: experimentation-growth-engineering
product: <experimentation | feature-flags | instrumentation | generic | etc.>
product_version: <"2026.04" | "n/a" | "unknown">
scope: tenant-specific | version-specific | likely-general
tags: [3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Context              (segment, scale, constraints — the analogue of "Permissions context")
## Attempts
## Resolution
```

> **Privacy:** scenarios carry **no** client-identifying info, no real company names, no PII, and no revenue figures attributable to a named org. Numbers are illustrative ranges or marked `[ESTIMATE]`. This mirrors the marketplace `/wrap` scrub discipline.

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-peeking-early-stop-false-positive.md`](2026-06-05-peeking-early-stop-false-positive.md) | likely-general | peeking, early-stopping, false-positive, fixed-horizon, sequential | high |
| [`2026-06-05-underpowered-test-mde-miss.md`](2026-06-05-underpowered-test-mde-miss.md) | likely-general | underpowered, mde, sample-size, power, null-result | high |
| [`2026-06-05-srm-from-redirect-bot-filter.md`](2026-06-05-srm-from-redirect-bot-filter.md) | likely-general | srm, sample-ratio-mismatch, assignment, exposure-logging, chi-square | high |
| [`2026-06-05-guardrail-regression-latency-vs-conversion.md`](2026-06-05-guardrail-regression-latency-vs-conversion.md) | likely-general | guardrail, latency, conversion, regression, ship-decision | medium |

## Promotion path

When ≥2 independent scenarios (different `contributed_at` quarters, different engagements) corroborate the same finding, an agent proposes promoting the lesson into [`../best-practices/`](../best-practices/) or a [`../knowledge/`](../knowledge/) decision tree. Promotion is manual; leave the scenario in place even after the rule is canonicalized — the narrative stays useful context.

## How agents use this bank

Per [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md): surface a matching scenario only as a *secondary* source, always behind the unverified-scenario preamble, and never let a scenario override the cited knowledge bank or a significance verdict that belongs to `applied-statistics`. The most-likely-to-benefit agents — `experimentation-architect`, `feature-flag-engineer`, `product-analytics-instrumentation-engineer` — should check the bank when a situation matches.
