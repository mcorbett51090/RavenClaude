# Regulatory-compliance scenarios bank

> Unverified, dated, scope-tagged narratives from real (or realistic) financial-regulatory / compliance engagements. Enabled as part of the value-add build-out (2026-06-05) — resolves the §8b TODO in [`../CLAUDE.md`](../CLAUDE.md).

This directory holds **scenarios** — engagement war stories of "the firm had compliance problem X, here was the situation, these were the constraints, we tried A/B/C, D resolved it." Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with a mandatory unverified-scenario preamble (see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md))

Unlike a code-vertical scenarios bank (a 403, a token error), these are **compliance-program engagements**: an alert backlog and a no-file decision, a regulatory-change impact assessment, a control-testing gap, a vendor-risk re-tiering, an exam-readiness gap. The "Resolution" is a compliance / analytical move plus a documented outcome, not a code fix.

## The schema (mirrors the marketplace 9-field scenario schema)

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: regulatory-compliance
product: <aml-kyc | regulatory-change | control-testing | third-party-risk | examination-prep | reporting>
product_version: "n/a"          # non-code vertical — no product version
scope: firm-specific | jurisdiction-specific | likely-general
tags: [list of 3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Context              (sector, regime, constraints — the non-code analogue of "Permissions context")
## Attempts
## Resolution
```

> **Privacy & confidentiality:** scenarios carry **no** client-identifying info, no customer/UBO PII, no SAR/STR content, no wire details, no real firm names, and no figures attributable to a named institution (CLAUDE.md §3 #9, §4, and the `scrub-confidential-pre-write.sh` hook). Numbers are illustrative ranges or carry a public-source citation. This mirrors the marketplace `/wrap` scrub discipline. **Anything touching real PII / SAR content / wire instructions never goes in a scenario** — it routes to `ravenclaude-core` `security-reviewer` and stays out of the bank entirely.

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-aml-alert-backlog-no-file-decision.md`](2026-06-05-aml-alert-backlog-no-file-decision.md) | likely-general | aml, alert-backlog, sar, no-file, structuring, fincen | medium |
| [`2026-06-05-regulatory-change-impact-assessment.md`](2026-06-05-regulatory-change-impact-assessment.md) | likely-general | regulatory-change, horizon-scanning, gap-analysis, applicability, policy | medium |
| [`2026-06-05-control-testing-design-gap.md`](2026-06-05-control-testing-design-gap.md) | likely-general | control-testing, design-effectiveness, detective, remediation, three-lines | medium |
| [`2026-06-05-third-party-vendor-risk-retiering.md`](2026-06-05-third-party-vendor-risk-retiering.md) | likely-general | third-party-risk, vendor, due-diligence, ongoing-monitoring, concentration | medium |

## Promotion path

When ≥2 independent scenarios (different engagements / quarters) corroborate the same finding, an agent may propose promoting the lesson into [`../best-practices/`](../best-practices/) or a [`../knowledge/`](../knowledge/) decision tree. As of this bank's creation, promotion is manual — leave the scenario in place even after the rule is canonicalized (the narrative stays useful as context).

## How agents use this bank

Per [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md): surface a matching scenario only as a *secondary* source, always behind the unverified-scenario preamble, and never let a scenario override the cited knowledge bank, a primary-source regulatory citation, or the legal-advice gate (CLAUDE.md §3 #10). The most-likely-to-benefit agents — `aml-kyc-analyst`, `risk-and-controls-specialist`, `policy-and-procedure-writer`, `examination-prep-specialist` — carry an inline scenario-retrieval prior and should check the bank when a situation matches. **Every regulatory value in a scenario remains `[verify-at-use]` against the regulator's primary source and the firm's actual regime — a scenario is a narrative, never a citation.**
