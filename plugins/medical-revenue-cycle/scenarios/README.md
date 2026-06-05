# Medical revenue-cycle scenarios bank

> Unverified, dated, scope-tagged narratives from real (or realistic) healthcare RCM consulting engagements. Enabled as part of the value-add build-out (2026-06-05).

This directory holds **scenarios** — engagement war stories of "the practice had problem X, here was the situation, these were the constraints, we tried A/B/C, D moved the number." Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with a mandatory unverified-scenario preamble (see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md))

Unlike a code-vertical scenarios bank (a 403, a token error), these are **revenue-cycle engagements**: a denial-rate root-cause, an A/R work-down, a clean-claim-rate lift, a payer underpayment recovery. The "Resolution" is an analytical move plus a measured outcome, not a code fix.

## The schema (mirrors the marketplace 9-field scenario schema)

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: medical-revenue-cycle
product: <denials | accounts-receivable | clean-claims | coding | payer-contract | front-end>
product_version: "n/a"          # non-code vertical — no product version
scope: practice-specific | segment-specific | likely-general
tags: [list of 3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Context              (segment, size, constraints — the non-code analogue of "Permissions context")
## Attempts
## Resolution
```

> **Privacy:** scenarios carry **no** client-identifying info, no PHI, no real provider names, no patient identifiers, and no revenue figures attributable to a named organization. Numbers are illustrative ranges, marked `[ESTIMATE]`, or carry a public-benchmark source. This mirrors the marketplace `/wrap` scrub discipline and CLAUDE.md §2 (the team stores no PHI). Any figure entering a client deliverable is validated against the client's actual data first (§3 #8).

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-denial-rate-root-cause-capa.md`](2026-06-05-denial-rate-root-cause-capa.md) | likely-general | denials, root-cause, capa, eligibility, authorization, carc | medium |
| [`2026-06-05-ar-days-reduction.md`](2026-06-05-ar-days-reduction.md) | likely-general | accounts-receivable, ar-days, aging, timely-filing, worklist | medium |
| [`2026-06-05-clean-claim-rate-improvement.md`](2026-06-05-clean-claim-rate-improvement.md) | likely-general | clean-claims, first-pass, scrubber, front-end, edits | medium |
| [`2026-06-05-payer-contract-underpayment.md`](2026-06-05-payer-contract-underpayment.md) | likely-general | payer-contract, underpayment, allowed-amount, variance, co-45 | medium |

## Promotion path

When ≥2 independent scenarios (different engagements / quarters) corroborate the same finding, an agent may propose promoting the lesson into [`../best-practices/`](../best-practices/) or a [`../knowledge/`](../knowledge/) decision tree. As of this bank's creation, promotion is manual — leave the scenario in place even after the rule is canonicalized (the narrative stays useful as context).

## How agents use this bank

Per [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md): surface a matching scenario only as a *secondary* source, always behind the unverified-scenario preamble, and never let a scenario override the cited knowledge bank or a credentialed coder's judgment (CLAUDE.md §2). The most-likely-to-benefit specialists — `denials-management-specialist`, `rcm-analytics-analyst`, `medical-coding-specialist` — should check the bank when a situation matches.
