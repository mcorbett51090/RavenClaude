# Lineage tracking must cover derived PII — every downstream copy is in scope

**Status:** Absolute rule
**Domain:** Data lineage / PII propagation
**Applies to:** `data-governance-privacy`

---

## Why this exists

A DSR erasure that deletes the PII from the source table but not from the mart, the backup, the ML training set, or the exported CSV is incomplete. The lineage graph is the only way to know where a PII column has flowed. A lineage system that tracks only source-to-staging hops (e.g., Airbyte lineage) but not the dbt transformation layer (where `customer_email` from `stg_stripe__customers` becomes `contact_email` in `dim_customer`) will silently miss derived copies. Every derived or copied PII field must be tracked, tagged, and included in DSR scope.

## How to apply

Configure lineage capture at every transformation layer:

| Layer | Lineage tool | Coverage |
|---|---|---|
| ELT (Airbyte/Fivetran) | Airbyte/Fivetran lineage API or OpenLineage | Source → raw table |
| dbt transform | dbt `--emit-artifacts` + OpenLineage dbt adapter | raw → staging → marts |
| Cube / semantic layer | Cube lineage API or manual catalog entry | mart → Cube cube |
| BI tool | Metabase / Superset metadata API | Cube/mart → dashboard |
| Exports / ML training sets | Manual registration or data-platform catalog hooks | mart → S3 / ML store |

**OpenLineage integration with dbt:**

```yaml
# profiles.yml — add OpenLineage emitter
analytics:
  target: prod
  outputs:
    prod:
      ...
      openlineage:
        transport:
          type: http
          url: "http://marquez:5000"
```

**In the catalog, for every PII column, annotate which downstream assets contain it:**

```markdown
## PII column: fct_customers.email
- Classification: Confidential + PII
- Downstream copies:
  - stg_stripe__customers.email (source)
  - dim_customer.contact_email (mart alias)
  - ml_training_set_2025.customer_email (S3 export — registered manually)
- DSR erasure target: ALL of the above
```

**Do:**
- Run a lineage coverage audit on every PII-classified column to verify all downstream copies are tracked.
- Include manual registration steps for untracked copies (CSV exports, ML training sets, BI extracts).
- Update lineage when a new mart or export is added that consumes a PII column.

**Don't:**
- Assume the catalog's auto-discovered lineage covers everything — manual export and ML training sets are often invisible to automated lineage tools.
- Treat lineage as a nice-to-have feature — it is the prerequisite for a complete DSR pipeline.

## Edge cases / when the rule does NOT apply

- Truly anonymized data (as defined by the anonymization decision tree — k-anonymity or differential-privacy verified) is out of PII scope and doesn't need PII lineage tracking. But most "de-identified" data remains pseudonymized and still in scope.

## See also

- [`../agents/data-catalog-lineage-engineer.md`](../agents/data-catalog-lineage-engineer.md) — owns the lineage graph and its PII annotations
- [`./lineage-enables-impact-analysis.md`](./lineage-enables-impact-analysis.md) — the broader lineage rule this specializes for PII

## Provenance

Codifies data-governance-privacy CLAUDE.md §2 house opinion #4 ("Access, erasure, and portability must be executable across every system that holds the person's data — which requires the catalog/lineage to even find it"). GDPR Article 17 (right to erasure) requires completeness across all copies.

---

_Last reviewed: 2026-06-05 by `claude`_
