# developer-relations scenarios bank

> Unverified, dated, scope-tagged narratives from real (or realistic) DevRel engagements. Part of the
> initial build-out (2026-06-18). Section 8b of the plugin [`CLAUDE.md`](../CLAUDE.md) points here.

This directory holds **scenarios** — war stories of "the team had DevRel problem X, here was the
context and constraints, we tried A/B/C, and D was the defensible move." Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with a mandatory
  unverified-scenario preamble (see
  [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md))

Unlike a code-vertical scenarios bank (a 403, a token error), these are **program engagements**: a
board deck led by vanity metrics, an activation leak traced to time-to-first-success. The
"Resolution" is a *DevRel* move plus the defensible read it produced — not a code fix.

## The schema (mirrors the marketplace 9-field scenario schema)

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: developer-relations
product: <strategy-metrics | onboarding-funnel | sample-apps | cfp-talks | community>
product_version: "n/a"          # non-code vertical — no product version
scope: engagement-specific | domain-specific | likely-general
tags: [list of 3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Context              (audience, funnel stage, constraints — the non-code analogue of "Permissions context")
## Attempts
## Resolution
```

> **Privacy:** scenarios carry **no** client-identifying info, no real company names, no proprietary
> metric values attributable to a named client. Numbers are illustrative ranges, marked `[ESTIMATE]`,
> or carry a public-source citation. This mirrors the marketplace `/wrap` scrub discipline.

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-18-vanity-metric-board-deck.md`](2026-06-18-vanity-metric-board-deck.md) | likely-general | vanity-metrics, activation, funnel, board-reporting, stars | medium |
| [`2026-06-18-onboarding-drop-off-time-to-first-call.md`](2026-06-18-onboarding-drop-off-time-to-first-call.md) | likely-general | onboarding, time-to-first-success, activation, golden-path, drop-off | medium |

## Promotion path

When ≥2 independent scenarios (different engagements / quarters) corroborate the same finding, an
agent may propose promoting the lesson into [`../best-practices/`](../best-practices/) or a
[`../knowledge/`](../knowledge/) decision tree. Promotion is manual — leave the scenario in place even
after the rule is canonicalized (the narrative stays useful as context).

## How agents use this bank

Per [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md):
surface a matching scenario only as a *secondary* source, always behind the unverified-scenario
preamble, and never let a scenario override the cited knowledge bank ([`../knowledge/`](../knowledge/))
or the [`../best-practices/`](../best-practices/) rules. The canonical method always wins; the
scenario is the war story beside it.
