# Finance scenarios bank

> Unverified, dated, scope-tagged narratives from real (or realistic) corporate-finance / FP&A engagements. Enabled as part of the value-add build-out (2026-06-05).

This directory holds **scenarios** — engagement war stories of "the team had problem X, here was the situation, these were the constraints, we tried A/B/C, D moved the number." Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with a mandatory unverified-scenario preamble (see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md))

Unlike a code-vertical scenarios bank (a 403, a token error), these are **finance-function engagements**: a budget-vs-actual variance investigation, a cash crunch, a forecast rebuild, a unit-economics teardown. The "Resolution" is an analytical move plus a measured outcome, not a code fix.

## The schema (mirrors the marketplace 9-field scenario schema)

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: finance
product: <fpa | modeling | controller | treasury | valuation | audit | board-reporting>
product_version: "n/a"          # non-code vertical — no product version
scope: company-specific | segment-specific | likely-general
tags: [list of 3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Context              (segment, size, constraints — the non-code analogue of "Permissions context")
## Attempts
## Resolution
```

> **Privacy (§3 #10 — confidentiality by default):** scenarios carry **no** company-identifying info, no customer/employee PII, no real company names or revenue figures attributable to a named entity. Numbers are illustrative ranges, marked `[ESTIMATE]`, or carry a public-benchmark source. This mirrors the marketplace `/wrap` scrub discipline.

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-budget-vs-actual-variance-investigation.md`](2026-06-05-budget-vs-actual-variance-investigation.md) | likely-general | variance, budget-vs-actual, reconcile-before-narrate, pvm, materiality | medium |
| [`2026-06-05-thirteen-week-cash-crunch.md`](2026-06-05-thirteen-week-cash-crunch.md) | likely-general | treasury, 13-week-cash, runway, covenant, working-capital | medium |
| [`2026-06-05-driver-based-forecast-rebuild.md`](2026-06-05-driver-based-forecast-rebuild.md) | likely-general | fpa, driver-based, forecast, hardcodes, scenarios | medium |
| [`2026-06-05-unit-economics-contribution-margin-teardown.md`](2026-06-05-unit-economics-contribution-margin-teardown.md) | segment-specific | saas, unit-economics, cac, ltv, contribution-margin, rule-of-40 | medium |

## Promotion path

When ≥2 independent scenarios (different engagements / quarters) corroborate the same finding, an agent may propose promoting the lesson into [`../best-practices/`](../best-practices/) or a [`../knowledge/`](../knowledge/) decision tree. As of this bank's creation, promotion is manual — leave the scenario in place even after the rule is canonicalized (the narrative stays useful as context).

## How agents use this bank

Per [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md): surface a matching scenario only as a *secondary* source, always behind the unverified-scenario preamble, and never let a scenario override the cited knowledge bank, a best-practice rule, or the applicable accounting standard (GAAP/IFRS). The most-likely-to-benefit specialists — `fpa-analyst`, `treasury-analyst`, `financial-modeler` — should check the bank when a situation matches.
