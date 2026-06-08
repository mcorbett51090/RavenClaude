# Behavioral-Health Practice scenarios bank

> Unverified, dated, scope-tagged narratives from real behavioral-health practice-operations engagements. War stories
> of "we hit X problem, here was the situation, these were our constraints, we tried A/B/C, D worked." **Operational and
> documentation support only — never clinical, medical, or legal advice. PHI-placeholdered throughout.**

This directory holds **scenarios** — field notes from real practice-operations work. Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with the mandatory unverified-scenario preamble

For the full architecture and the retrieval pattern, see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md). Canonical knowledge lives in [`../knowledge/`](../knowledge/) and `best-practices/`; scenarios never replace it.

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: behavioral-health-practice
product: <ehr | clearinghouse | payer-portal | generic | etc.>
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
| [`2026-06-08-no-show-rate-that-was-reminders-only.md`](2026-06-08-no-show-rate-that-was-reminders-only.md) | no-shows, scheduling, telehealth, operations | `operations-exist-to-protect-the-clinical-hour` |
| [`2026-06-08-part-2-record-disclosed-on-a-general-roi.md`](2026-06-08-part-2-record-disclosed-on-a-general-roi.md) | 42-cfr-part-2, roi, consent, disclosure | `part-2-stricter-than-hipaa-assume-it-applies`, `consent-precedes-disclosure` |
| [`2026-06-08-auth-ran-out-mid-treatment-and-claims-denied.md`](2026-06-08-auth-ran-out-mid-treatment-and-claims-denied.md) | prior-authorization, reauth, claims, denial, units | `code-reflects-the-service-rendered`, `verify-eligibility-before-the-first-session` |
| [`2026-06-08-telehealth-couldnt-connect-no-shows.md`](2026-06-08-telehealth-couldnt-connect-no-shows.md) | telehealth, no-shows, readiness, place-of-service | `telehealth-readiness-is-part-of-the-appointment` |
| [`2026-06-08-whole-chart-sent-on-a-benefits-request.md`](2026-06-08-whole-chart-sent-on-a-benefits-request.md) | minimum-necessary, disclosure, roi, consent | `minimum-necessary-is-the-disclosure-default`, `consent-precedes-disclosure` |
