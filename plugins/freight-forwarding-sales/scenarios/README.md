# Freight-forwarding sales scenarios bank

> Unverified, dated, scope-tagged narratives from real (or realistic) international freight-forwarding sales / business-development engagements. Enabled as part of the value-add build-out (2026-06-05).

This directory holds **scenarios** — sales war stories of "the seller faced situation X, here were the constraints, we tried A/B/C, D moved the number." Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with a mandatory unverified-scenario preamble (see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md))

Unlike a code-vertical scenarios bank (a 403, a token error), these are **commercial sales engagements**: a margin eroding under surcharge volatility, a tender to qualify-or-decline, a mode-shift call against a deadline, an account drifting toward churn. The "Resolution" is a commercial move plus a measured outcome, not a code fix.

## The schema (mirrors the marketplace 9-field scenario schema)

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: freight-forwarding-sales
product: <quoting | rfq-tender | account-management | mode-selection | pipeline | prospecting>
product_version: "n/a"          # non-code vertical — no product version
scope: lane-specific | segment-specific | likely-general
tags: [list of 3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Context              (segment, lane, constraints — the non-code analogue of "Permissions context")
## Attempts
## Resolution
```

> **Privacy:** scenarios carry **no** customer-identifying info, no real shipper names, no confidential commercial terms (a customer's actual buy rate, contract price, or volume commitment) attributable to a named account. Rates, surcharge amounts, and volumes are illustrative ranges, marked `[example — confirm against your live rates/tariff]`, or carry a public-benchmark source with a retrieval date. This mirrors the marketplace `/wrap` scrub discipline and CLAUDE.md §3 #8 (examples are examples) and the §"keep it generic" routing rule.

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-quote-margin-erosion-surcharge-volatility.md`](2026-06-05-quote-margin-erosion-surcharge-volatility.md) | likely-general | quoting, surcharge, baf, gri, margin, validity | medium |
| [`2026-06-05-rfq-tender-qualify-or-decline.md`](2026-06-05-rfq-tender-qualify-or-decline.md) | likely-general | rfq, tender, qualify, win-rate, bid-no-bid | medium |
| [`2026-06-05-mode-shift-air-vs-ocean-deadline.md`](2026-06-05-mode-shift-air-vs-ocean-deadline.md) | likely-general | mode-selection, air, ocean, sea-air, deadline, inventory-carrying-cost | medium |
| [`2026-06-05-key-account-qbr-retention.md`](2026-06-05-key-account-qbr-retention.md) | likely-general | qbr, account-management, retention, whitespace, multi-thread | medium |

## Promotion path

When ≥2 independent scenarios (different engagements / quarters) corroborate the same finding, an agent may propose promoting the lesson into [`../best-practices/`](../best-practices/) or a [`../knowledge/`](../knowledge/) decision tree. As of this bank's creation, promotion is manual — leave the scenario in place even after the rule is canonicalized (the narrative stays useful as context).

## How agents use this bank

Per [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md): surface a matching scenario only as a *secondary* source, always behind the unverified-scenario preamble, and never let a scenario override the cited knowledge bank ([`../knowledge/`](../knowledge/)), the best-practice rules ([`../best-practices/`](../best-practices/)), or a live tariff/carrier schedule. The most-likely-to-benefit specialists — `freight-rate-quoter`, `rfq-tender-strategist`, `key-account-manager`, `trade-lane-compliance-advisor` — should check the bank when a situation matches.
