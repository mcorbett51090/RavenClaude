# Cybersecurity-GRC scenarios bank

> Unverified, dated, scope-tagged narratives from real GRC engagements. War stories of "we hit X
> problem, here was the situation, these were our constraints, we tried A/B/C, D worked."

This directory holds **scenarios** — field notes from real compliance work. Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with the mandatory unverified-scenario preamble

For the full architecture and the retrieval pattern, see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md). Canonical knowledge lives in [`../knowledge/`](../knowledge/) and `best-practices/`; scenarios never replace it.

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: cybersecurity-grc
product: <soc2 | iso-27001 | nist-csf | nist-800-53 | tprm | generic | etc.>
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
| [`2026-06-08-evidence-screenshot-fire-drill.md`](2026-06-08-evidence-screenshot-fire-drill.md) | evidence, ccm, type-ii, operating-effectiveness | `evidence-is-a-system-not-a-fire-drill`, `a-control-has-three-states` |
| [`2026-06-08-vendor-soc2-taken-at-face-value.md`](2026-06-08-vendor-soc2-taken-at-face-value.md) | tprm, vendor-risk, shared-responsibility, soc2-exceptions | `third-party-risk-is-your-risk` |
