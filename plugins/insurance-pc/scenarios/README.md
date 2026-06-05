# P&C insurance scenarios bank

> Unverified, dated, scope-tagged narratives from real (or realistic) property-&-casualty consulting / underwriting engagements. Added as part of the value-add build-out (2026-06-05).

This directory holds **scenarios** — engagement war stories of "the book had problem X, here was the situation, these were the constraints, we tried A/B/C, D moved the number." Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with a mandatory unverified-scenario preamble (see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md))

Unlike a code-vertical scenarios bank (a 403, a token error), these are **underwriting-and-claims engagements**: a combined-ratio deterioration, an underwriting-mix correction, a claims-cycle/LAE problem, a retention/renewal leak. The "Resolution" is an analytical move plus a measured outcome, not a code fix.

## The schema (mirrors the marketplace 9-field scenario schema)

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: insurance-pc
product: <underwriting | claims | actuarial-pricing | portfolio | agency-distribution>
product_version: "n/a"          # non-code vertical — no product version
scope: book-specific | segment-specific | likely-general
tags: [list of 3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Context              (segment, size, constraints — the non-code analogue of "Permissions context")
## Attempts
## Resolution
```

> **Privacy:** scenarios carry **no** client-identifying info, no policyholder/claimant PII, no real carrier/MGA/agency names or premium figures attributable to a named book. Numbers are illustrative ranges, marked `[ESTIMATE]`, or carry a public-benchmark source. This mirrors the marketplace `/wrap` scrub discipline and CLAUDE.md §2 (the team stores no policyholder records).

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-combined-ratio-deterioration-diagnosis.md`](2026-06-05-combined-ratio-deterioration-diagnosis.md) | likely-general | combined-ratio, loss-ratio, expense-ratio, catastrophe, attritional | medium |
| [`2026-06-05-underwriting-mix-correction.md`](2026-06-05-underwriting-mix-correction.md) | likely-general | line-of-business-mix, ncr, rate-adequacy, appetite, portfolio | medium |
| [`2026-06-05-claims-cycle-time-and-lae-reduction.md`](2026-06-05-claims-cycle-time-and-lae-reduction.md) | likely-general | claims, lae, cycle-time, leakage, severity | medium |
| [`2026-06-05-renewal-retention-leak.md`](2026-06-05-renewal-retention-leak.md) | likely-general | retention, renewal, persistency, agency, new-business-loss-ratio | medium |

## Promotion path

When ≥2 independent scenarios (different engagements / quarters) corroborate the same finding, an agent may propose promoting the lesson into [`../best-practices/`](../best-practices/) or a [`../knowledge/`](../knowledge/) decision tree. As of this bank's creation, promotion is manual — leave the scenario in place even after the rule is canonicalized (the narrative stays useful as context).

## How agents use this bank

Per [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md): surface a matching scenario only as a *secondary* source, always behind the unverified-scenario preamble, and never let a scenario override the cited knowledge bank or a credentialed actuary's judgment (CLAUDE.md §2). The most-likely-to-benefit specialists — `pc-underwriter`, `claims-specialist`, `actuarial-pricing-analyst` — should check the bank when a situation matches.
