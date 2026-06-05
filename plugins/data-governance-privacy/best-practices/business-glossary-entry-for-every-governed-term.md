# Create a business glossary entry for every governed business term

**Status:** Pattern
**Domain:** Data catalog / business glossary
**Applies to:** `data-governance-privacy`

---

## Why this exists

"Revenue," "active user," and "customer" have precise technical definitions in the mart layer. They also have business definitions that non-technical stakeholders use, and the two definitions often don't match exactly. Without a governed business glossary that links the business definition to the technical asset (the dbt model, the Cube measure), a stakeholder who reads "active user" in a quarterly review has no way to verify which SQL definition produced that number. The business glossary is the bridge between the business language and the technical catalog — and it is the governance artifact that makes an analytics program auditable.

## How to apply

For every KPI or business term that appears in a dashboard, a report, or a stakeholder communication, create a glossary entry with these fields:

```yaml
# OpenMetadata / DataHub glossary entry shape
term: Active User
description: >
  A registered account that has performed at least one qualifying interaction
  within a rolling 30-day window. Qualifying interactions: login, feature use,
  API call. Excludes: staff accounts, test accounts, accounts marked churned.
owner: analytics-team
domain: Product
status: Approved
technical_assets:
  - type: dbt_metric
    path: metrics/active_user.yml
  - type: cube_measure
    path: cubes/users.yml#active_users
synonyms:
  - MAU (Monthly Active User)
  - 30DAU
related_terms:
  - Churned User
  - Engaged User
last_reviewed: 2026-06-05
```

**Do:**
- Create the glossary entry at the same time the metric is first defined in the semantic layer.
- Link the glossary term to the technical asset (dbt metric, Cube measure, mart model) so the lineage is searchable.
- Mark terms as `Approved` or `Draft` — stakeholders should only cite `Approved` terms in formal reports.
- Review glossary terms when the underlying technical definition changes.

**Don't:**
- Create a glossary entry that is a copy of the column description — the glossary entry is the business definition, not the technical implementation.
- Let synonyms diverge ("MAU" and "Monthly Active User" should be one term with a synonym, not two separate entries with slightly different definitions).

## Edge cases / when the rule does NOT apply

- Internal engineering metrics (e.g., `pipeline_run_duration_ms`) that are never cited in business communications are exempt from the governed glossary requirement.

## See also

- [`../agents/data-catalog-lineage-engineer.md`](../agents/data-catalog-lineage-engineer.md) — manages the catalog and glossary
- [`./you-cant-govern-what-you-cant-find.md`](./you-cant-govern-what-you-cant-find.md) — the discovery-first rule that the glossary builds on

## Provenance

Standard data governance practice — the business glossary is a core capability in enterprise catalog tools (DataHub, OpenMetadata, Alation, Atlan). Codifies data-governance-privacy CLAUDE.md §2 house opinion #1 ("You can't govern what you can't find") at the business-language layer.

---

_Last reviewed: 2026-06-05 by `claude`_
