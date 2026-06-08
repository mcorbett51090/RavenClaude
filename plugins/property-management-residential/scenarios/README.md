# Property-management-residential scenarios bank

> Unverified, dated, scope-tagged narratives from real residential property-management engagements. War stories of
> "we hit X problem, here was the situation, these were our constraints, we tried A/B/C, D worked." None of these
> are legal advice — fair-housing and habitability narratives are flag-and-route stories, not legal rulings.

This directory holds **scenarios** — field notes from real property work. Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with the mandatory unverified-scenario preamble

For the full architecture and the retrieval pattern, see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md). Canonical knowledge lives in [`../knowledge/`](../knowledge/) and `best-practices/`; scenarios never replace it.

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: property-management-residential
product: <appfolio | yardi | buildium | rentmanager | generic | etc.>
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
| [`2026-06-08-inconsistent-screening-fair-housing-risk.md`](2026-06-08-inconsistent-screening-fair-housing-risk.md) | screening, fair-housing, documentation, consistency | `screen-by-a-consistent-documented-standard`, `fair-housing-is-a-flag-not-an-opinion` |
| [`2026-06-08-no-heat-call-parked-as-routine.md`](2026-06-08-no-heat-call-parked-as-routine.md) | habitability, triage, emergency, work-order | `habitability-is-non-negotiable-and-time-sensitive`, `triage-by-safety-and-habitability-first` |
| [`2026-06-08-turn-clock-started-at-empty-not-notice.md`](2026-06-08-turn-clock-started-at-empty-not-notice.md) | vacancy, turn, make-ready, days-vacant, leasing | `vacancy-is-the-most-expensive-thing`, `pm_calc.py rentroll` |
| [`2026-06-08-noi-reported-with-debt-service-mixed-in.md`](2026-06-08-noi-reported-with-debt-service-mixed-in.md) | noi, owner-statement, debt-service, capex, reporting | `noi-is-operating-only-not-cash-flow`, `pm_calc.py noi` |
| [`2026-06-08-drifted-rent-roll-hid-the-real-delinquency.md`](2026-06-08-drifted-rent-roll-hid-the-real-delinquency.md) | rent-roll, delinquency, reconciliation, data-integrity, collections | `rent-roll-is-the-source-of-truth`, `delinquency-runs-on-a-consistent-collections-ladder`, `pm_calc.py delinquency` |
