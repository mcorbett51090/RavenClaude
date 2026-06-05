# Renewable energy scenarios bank

> Unverified, dated, scope-tagged narratives from real (or realistic) renewable-energy development/finance/ops engagements. Enabled as part of the value-add build-out (2026-06-05).

This directory holds **scenarios** — engagement war stories of "the project had problem X, here was the situation, these were the constraints, we tried A/B/C, D moved the number." Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with a mandatory unverified-scenario preamble (see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md))

Unlike a code-vertical scenarios bank (a 403, a token error), these are **project-development/finance/ops engagements**: an interconnection-queue delay, an offtake-structure choice, a tax-credit election, a storage-add decision, a production-underperformance diagnosis. The "Resolution" is an analytical move plus a measured outcome, not a code fix.

## The schema (mirrors the marketplace 9-field scenario schema)

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: renewable-energy
product: <development | interconnection | finance | offtake | operations | storage>
product_version: "n/a"          # non-code vertical — no product version
scope: project-specific | segment-specific | likely-general
tags: [list of 3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Context              (segment, size, constraints — the non-code analogue of "Permissions context")
## Attempts
## Resolution
```

> **Privacy:** scenarios carry **no** client-identifying info, no counterparty PII, no real project names, no named-utility queue positions, and no revenue figures attributable to a named developer or offtaker. Numbers are illustrative ranges, marked `[ESTIMATE]`, or carry a public-benchmark source with a retrieval date. This mirrors the marketplace `/wrap` scrub discipline and CLAUDE.md §2 (the team stores no customer PII).

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-interconnection-queue-upgrade-shock.md`](2026-06-05-interconnection-queue-upgrade-shock.md) | likely-general | interconnection, queue, network-upgrade, resize, irr | medium |
| [`2026-06-05-ppa-vs-merchant-offtake.md`](2026-06-05-ppa-vs-merchant-offtake.md) | likely-general | ppa, merchant, offtake, financing, basis-risk | medium |
| [`2026-06-05-itc-vs-ptc-election.md`](2026-06-05-itc-vs-ptc-election.md) | likely-general | itc, ptc, tax-credit, capacity-factor, election | medium |
| [`2026-06-05-storage-add-to-capture-curtailment.md`](2026-06-05-storage-add-to-capture-curtailment.md) | likely-general | storage, bess, curtailment, dispatch, hybrid | medium |
| [`2026-06-05-capacity-factor-underperformance.md`](2026-06-05-capacity-factor-underperformance.md) | likely-general | capacity-factor, degradation, availability, p90, underperformance | medium |

## Promotion path

When ≥2 independent scenarios (different engagements / quarters) corroborate the same finding, an agent may propose promoting the lesson into [`../best-practices/`](../best-practices/) or a [`../knowledge/`](../knowledge/) decision tree. As of this bank's creation, promotion is manual — leave the scenario in place even after the rule is canonicalized (the narrative stays useful as context).

## How agents use this bank

Per [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md): surface a matching scenario only as a *secondary* source, always behind the unverified-scenario preamble, and never let a scenario override the cited knowledge bank, a current tax/legal opinion, or a PE-stamped engineering judgment (CLAUDE.md §2). Tax-credit, interconnection-tariff, and policy facts are **jurisdiction- and year-specific** and moved materially in 2025 (the OBBBA / 25D-sunset cautionary tale) — re-verify every such figure at point of use.
