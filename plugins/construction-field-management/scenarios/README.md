# Construction Field Management scenarios bank

> Unverified, dated, scope-tagged narratives from real construction field engagements. War stories of "we hit X
> problem, here was the situation, these were our constraints, we tried A/B/C, D worked."

This directory holds **scenarios** — field notes from real jobsite work. Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with the mandatory unverified-scenario preamble

For the full architecture and the retrieval pattern, see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md). Canonical knowledge lives in [`../knowledge/`](../knowledge/) and `docs/best-practices/`; scenarios never replace it.

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: construction-field-management
product: <aia-g702-g703 | procore | osha-1926 | generic | etc.>
product_version: "<version or unknown>"
scope: <likely-general | product-specific>
tags: [<tag>, ...]
confidence: <high | medium | low>
reviewed: false
---
```

## Current bank

| File | Tags | Corroborates |
|---|---|---|
| [`2026-06-08-rfi-answer-built-before-it-was-priced.md`](2026-06-08-rfi-answer-built-before-it-was-priced.md) | rfi, change-order, unpriced-work, claim | `nothing-gets-built-unpriced-or-uninspected`, `ball-in-court-is-the-unit-of-progress` |
| [`2026-06-08-submittal-surfaced-the-week-of-install.md`](2026-06-08-submittal-surfaced-the-week-of-install.md) | submittals, lead-time, schedule, document-control | `schedule-submittals-backward-from-the-install`, `field-builds-off-one-current-set` |
| [`2026-06-08-under-budget-until-the-ctc-landed.md`](2026-06-08-under-budget-until-the-ctc-landed.md) | cost-report, cost-to-complete, commitments, change-order | `cost-report-needs-a-cost-to-complete`, `an-sov-is-the-billing-contract-not-a-front-load` |
| [`2026-06-08-generic-toolbox-talk-on-a-confined-space-day.md`](2026-06-08-generic-toolbox-talk-on-a-confined-space-day.md) | safety, jha, toolbox-talk, confined-space, osha | `safety-is-planned-per-task-osha-is-the-floor`, `contemporaneous-records-win-disputes` |
| [`2026-06-08-substantial-completion-held-the-retainage.md`](2026-06-08-substantial-completion-held-the-retainage.md) | closeout, retainage, punch-list, substantial-completion | `closeout-is-a-package-that-releases-retainage`, `a-punch-list-goes-to-zero` |
