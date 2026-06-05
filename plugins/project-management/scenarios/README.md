# Project-management scenarios bank

> Unverified, dated, scope-tagged narratives from real (or realistic) project/delivery-management engagements. Enabled as part of the value-add build-out (2026-06-05); this replaces the `## 7a. Scenarios bank — TODO (planned)` placeholder that previously sat in [`../CLAUDE.md`](../CLAUDE.md).

This directory holds **scenarios** — delivery war stories of "the project had problem X, here was the situation, these were the constraints, we tried A/B/C, D moved the outcome." Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with a mandatory unverified-scenario preamble (see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md))

Unlike a code-vertical scenarios bank (a 403, a token error), these are **delivery-management engagements**: a watermelon status, scope creep with no change control, an earned-value recovery decision, a predictive-vs-agile method mismatch. The "Resolution" is a delivery move plus a measured or qualitative outcome, not a code fix.

## The schema (mirrors the marketplace 9-field scenario schema)

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: project-management
product: <delivery-predictive | delivery-agile | delivery-hybrid | raid-risk | stakeholder-governance>
product_version: "n/a"          # non-code vertical — no product version
scope: project-specific | segment-specific | likely-general
tags: [list of 3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Context              (track, size, constraints — the non-code analogue of "Permissions context")
## Attempts
## Resolution
```

> **Privacy:** scenarios carry **no** client-identifying info, no named programs, no real organisation names, and no real budget/revenue figures attributable to a named engagement. Numbers are illustrative ranges, marked `[ESTIMATE]`, or carry a public-source reference. This mirrors the marketplace `/wrap` scrub discipline.

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-watermelon-status-green-on-red.md`](2026-06-05-watermelon-status-green-on-red.md) | likely-general | status, watermelon, rag, earned-value, spi, governance | medium |
| [`2026-06-05-scope-creep-no-change-control.md`](2026-06-05-scope-creep-no-change-control.md) | likely-general | scope-creep, change-control, baseline, requirements, predictive | medium |
| [`2026-06-05-evm-cpi-recovery-decision.md`](2026-06-05-evm-cpi-recovery-decision.md) | likely-general | earned-value, cpi, eac, tcpi, recovery, contingency | medium |
| [`2026-06-05-predictive-agile-method-mismatch.md`](2026-06-05-predictive-agile-method-mismatch.md) | likely-general | delivery-approach, hybrid, agile, predictive, requirements-stability, tailoring | medium |

## Promotion path

When ≥2 independent scenarios (different engagements / quarters) corroborate the same finding, an agent may propose promoting the lesson into [`../best-practices/`](../best-practices/) or a [`../knowledge/`](../knowledge/) decision tree. As of this bank's creation, promotion is manual — leave the scenario in place even after the rule is canonicalised (the narrative stays useful as context). Several of these scenarios already corroborate existing rules (e.g. `scope-absorption-is-a-defect`, `status-leads-with-narrative-and-matches-the-numbers`) — they are kept as the lived case behind the rule.

## How agents use this bank

Per [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md): surface a matching scenario only as a *secondary* source, always behind the unverified-scenario preamble ("Based on N unverified scenarios from YYYY-MM tagged [scope] — verify in your environment"), and never let a scenario override the cited knowledge bank (the decision trees + best-practices) or the engagement's actual governance. The specialists most likely to benefit — `delivery-lead`, `scrum-master`, `risk-and-raid-analyst`, `stakeholder-comms-lead` — should check the bank when a situation matches.
