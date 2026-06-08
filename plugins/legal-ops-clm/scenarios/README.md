# Legal Ops & CLM scenarios bank

> Unverified, dated, scope-tagged narratives from real legal-ops / CLM engagements. War stories of "we hit X
> problem, here was the situation, these were our constraints, we tried A/B/C, D worked." **Not legal advice.**

This directory holds **scenarios** — field notes from real legal-ops and contract-lifecycle work. Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with the mandatory unverified-scenario preamble

For the full architecture and the retrieval pattern, see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md). Canonical knowledge lives in [`../knowledge/`](../knowledge/) and `best-practices/`; scenarios never replace it, and none of it is legal advice.

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: legal-ops-clm
product: <ironclad | docusign | evisort | generic | etc.>
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
| [`2026-06-08-nda-self-serve-without-a-playbook.md`](2026-06-08-nda-self-serve-without-a-playbook.md) | intake, playbook, escalation-trigger, self-serve | `structured-intake-not-a-dm`, `the-playbook-needs-a-bright-line-escalation-trigger` |
| [`2026-06-08-missed-auto-renew-notice-window.md`](2026-06-08-missed-auto-renew-notice-window.md) | renewals, auto-renew, notice-window, alerts | `track-the-notice-window-not-just-expiry`, `signature-is-the-start-not-the-end` |
