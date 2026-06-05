# Data Governance & Privacy scenarios bank

> Unverified, dated, scope-tagged narratives from real data-governance / privacy engagements. War stories of "we hit X problem, here was the situation, these were our constraints, we tried A/B/C, D worked." Governance engineering, not legal advice — privacy law varies by jurisdiction; every regulatory fact is dated and `[verify-at-use]`.

This directory holds **scenarios** — field notes from real governance/privacy work. Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with the mandatory unverified-scenario preamble

For the full architecture and the retrieval pattern, see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md). Canonical knowledge lives in [`../knowledge/`](../knowledge/) and `docs/best-practices/`; scenarios never replace it.

**Privacy boundary (this plugin's §2):** scenarios carry **no real personal data, no client identifiers, no regulated records** — they describe the *engineering pattern* (the pipeline, the classification, the transfer mechanism), never the data. A scenario that would require an actual PII sample to be useful does not belong here.

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: data-governance-privacy
product: <gdpr | ccpa-cpra | dpdp | data-catalog | warehouse | generic | etc.>
product_version: <"2026.04" | "unknown">
scope: tenant-specific | version-specific | likely-general
tags: [3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Constraints context
## Attempts
## Resolution
```

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-dsar-erasure-at-scale.md`](2026-06-05-dsar-erasure-at-scale.md) | likely-general | dsar, erasure, lineage, fan-out, retention-carve-out | high |
| [`2026-06-05-pii-discovery-in-the-warehouse.md`](2026-06-05-pii-discovery-in-the-warehouse.md) | likely-general | pii-discovery, classification, warehouse, column-tagging, derived-pii | high |
| [`2026-06-05-cross-border-transfer-gap.md`](2026-06-05-cross-border-transfer-gap.md) | likely-general | cross-border, scc, adequacy, dpf, transfer-mechanism, sub-processor | medium |
| [`2026-06-05-consent-purpose-limitation-drift.md`](2026-06-05-consent-purpose-limitation-drift.md) | likely-general | consent, purpose-limitation, lawful-basis, ml-training, revocation | medium |

## Promotion path

When ≥2 independent scenarios (different `contributed_at` quarters, different engagements) corroborate the same finding, an agent proposes promotion to a `knowledge/` decision tree or `docs/best-practices/`. As of this bank's first version, promotion is manual and the scenarios stay in place after a rule is canonicalized — the narrative remains useful context.
