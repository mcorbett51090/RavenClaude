# Commercial real estate scenarios bank

> Unverified, dated, scope-tagged narratives from real (or realistic) CRE acquisitions / asset-management / leasing engagements. Enabled as part of the value-add build-out (2026-06-05).

This directory holds **scenarios** — engagement war stories of "the deal/asset had problem X, here was the situation, these were the constraints, we tried A/B/C, D moved the number." Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with a mandatory unverified-scenario preamble (see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md))

Unlike a code-vertical scenarios bank (a 403, a token error), these are **investment / asset-management engagements**: a refinance covenant breach, an NOI miss, a hold-vs-sell call, a lease renewal-vs-re-tenant trade. The "Resolution" is an analytical move plus a measured outcome, not a code fix.

## The schema (mirrors the marketplace 9-field scenario schema)

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: commercial-real-estate
product: <underwriting | asset-management | leasing | debt-finance | disposition>
product_version: "n/a"          # non-code vertical — no product version
scope: deal-specific | segment-specific | likely-general
tags: [list of 3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Context              (segment, size, constraints — the non-code analogue of "Permissions context")
## Attempts
## Resolution
```

> **Privacy:** scenarios carry **no** client-identifying info, no tenant PII, no real property addresses or ownership figures attributable to a named owner/fund. Numbers are illustrative ranges, marked `[ESTIMATE]`, or carry a public-benchmark source. This mirrors the marketplace `/wrap` scrub discipline and CLAUDE.md §2 (the team stores no tenant records).

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-dscr-breach-on-refi-rate-reset.md`](2026-06-05-dscr-breach-on-refi-rate-reset.md) | likely-general | dscr, refinance, rate-reset, debt-yield, cash-in | medium |
| [`2026-06-05-noi-erosion-opex-and-vacancy.md`](2026-06-05-noi-erosion-opex-and-vacancy.md) | likely-general | noi, opex, recovery-ratio, vacancy, variance | medium |
| [`2026-06-05-hold-vs-sell-at-cap-rate-shift.md`](2026-06-05-hold-vs-sell-at-cap-rate-shift.md) | likely-general | hold-vs-sell, exit-cap, irr, refinance, disposition | medium |
| [`2026-06-05-lease-renewal-vs-retenant-ti-downtime.md`](2026-06-05-lease-renewal-vs-retenant-ti-downtime.md) | likely-general | lease, renewal, net-effective-rent, ti, downtime | medium |

## Promotion path

When ≥2 independent scenarios (different engagements / quarters) corroborate the same finding, an agent may propose promoting the lesson into [`../best-practices/`](../best-practices/) or a [`../knowledge/`](../knowledge/) decision tree. As of this bank's creation, promotion is manual — leave the scenario in place even after the rule is canonicalized (the narrative stays useful as context).

## How agents use this bank

Per [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md): surface a matching scenario only as a *secondary* source, always behind the unverified-scenario preamble, and never let a scenario override the cited knowledge bank or the house opinions (CLAUDE.md §3). The most-likely-to-benefit specialists — `acquisitions-underwriter`, `asset-property-manager`, `cre-market-analyst` — should check the bank when a situation matches.
