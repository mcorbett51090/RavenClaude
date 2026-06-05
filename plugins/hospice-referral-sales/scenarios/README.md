# Hospice referral-sales scenarios bank

> Unverified, dated, scope-tagged narratives from real (or realistic) hospice referral-development / community-liaison engagements. Part of the initial release (2026-06-05).

This directory holds **scenarios** — referral-development war stories of "the liaison faced situation X, here were the constraints, we tried A/B/C, D moved the number." Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a _secondary_ source — always surfaced with a mandatory unverified-scenario preamble (see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md))

These are **referral-development engagements**: a late-referral pattern shortening length of stay, a referral partner cooling after a poor admission experience, an eligibility-education gap at a cardiology practice, a gift/arrangement that crossed the anti-kickback line. The "Resolution" is a relationship/education move plus a measured outcome, not a code fix.

## The schema (mirrors the marketplace 9-field scenario schema)

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: hospice-referral-sales
product: <territory | eligibility-education | account-management | funnel | goals-of-care | compliance>
product_version: "n/a"          # non-code vertical — no product version
scope: lane-specific | segment-specific | likely-general
tags: [list of 3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Context              (segment, source type, constraints — the non-code analogue of "Permissions context")
## Attempts
## Resolution
```

> **Privacy & compliance:** scenarios carry **no** patient-identifying info, no real patient names, no real referral-source names, and no confidential commercial terms. They never assert a specific patient was "eligible" (the physician certifies) and never green-light a value exchange (the compliance officer rules). Eligibility thresholds, length-of-stay and conversion figures are illustrative ranges marked `[example — confirm]` or carry a public-source-type reference with a retrieval date and an `[unverified]` marker. This mirrors CLAUDE.md §3 (#1 educate-not-certify, #2 clear-anti-kickback-first, #7 protect-PHI, #8 examples-are-examples).

## What's in this bank

| File | Scope | Tags | Confidence |
| --- | --- | --- | --- |
| [`2026-06-05-late-referral-short-length-of-stay.md`](2026-06-05-late-referral-short-length-of-stay.md) | likely-general | late-referral, length-of-stay, education, timing | medium |
| [`2026-06-05-snf-referral-partner-relationship-recovery.md`](2026-06-05-snf-referral-partner-relationship-recovery.md) | likely-general | account-management, snf, recovery, service-failure | medium |
| [`2026-06-05-eligibility-education-end-stage-heart-failure.md`](2026-06-05-eligibility-education-end-stage-heart-failure.md) | likely-general | eligibility, cardiac, lcd, education, non-cancer | medium |
| [`2026-06-05-compliance-gift-inducement-line.md`](2026-06-05-compliance-gift-inducement-line.md) | likely-general | compliance, anti-kickback, gifts, inducement | medium |

## Promotion path

When ≥2 independent scenarios corroborate the same finding, an agent may propose promoting the lesson into [`../best-practices/`](../best-practices/) or a [`../knowledge/`](../knowledge/) decision tree. Promotion is manual; leave the scenario in place even after the rule is canonicalized.

## How agents use this bank

Per [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md): surface a matching scenario only as a _secondary_ source, always behind the unverified-scenario preamble, and never let a scenario override the cited knowledge bank, the best-practice rules, a current LCD/CMS rule, the physician's certification, or the compliance officer's ruling.
