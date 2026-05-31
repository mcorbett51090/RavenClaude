---
description: Design a Dataverse table/column schema correctly — choice vs lookup vs customer column, alternate keys for upsert, where to enforce logic (business rule vs rollup vs plug-in), avoiding cascade-on-high-volume-child, least-privilege security roles, and field-level security used sparingly.
argument-hint: "[the entity/relationship, e.g. 'Project with many Tasks']"
---

# Design a Dataverse schema

You are running `/power-platform:design-dataverse-schema`. Model the Dataverse tables, columns, and relationships for what the user described (`$ARGUMENTS`), following this plugin's `dataverse-architect` discipline — choices that won't become migration-and-performance debt at volume.

## When to use this

A new table or relationship is being added, or an existing model is being reviewed before it scales.

## Steps

1. **Column type by intent** (`dataverse-choice-vs-lookup-vs-customer-column`): bounded fixed set → Choice; reference to one other table → Lookup; polymorphic (Account *or* Contact) → Customer column — picking wrong forces a costly remodel.
2. **Alternate keys for upsert + integration** (`dataverse-alternate-keys-and-upsert`): define alternate keys so external systems upsert by business key, not GUID.
3. **Where to enforce logic** (`dataverse-where-to-enforce-logic`, `dataverse-rollup-vs-calculated-vs-plugin`): same-record/simple → business rule or calculated; aggregate of children → rollup (mind its limits); complex/cross-entity/transactional → plug-in at the right **pipeline stage** (`dataverse-plugin-pipeline-stage-selection`).
4. **Relationship cascade behavior** (`dataverse-avoid-cascade-on-high-volume-child`): never cascade-delete/assign/share onto a high-volume child — it's a row-lock + recalculation storm. Use Referential where appropriate.
5. **Security**: least-privilege roles (`dataverse-security-least-privilege-roles`); field-level security only where genuinely needed (`dataverse-field-level-security-sparingly` — it's expensive and complicates everything).
6. **Bulk + throttling awareness** (`dataverse-bulk-operations-and-throttling`) for any load path.

## Guardrails

- An *access* error (privilege) is not a *schema* error (`dataverse-access-error-is-not-a-schema-error`) — diagnose which before "fixing" the model.
- Don't cascade onto high-volume children; don't sprinkle field-level security.
- Pin the publisher prefix (`alm-pin-one-publisher-prefix-per-repo`) and keep the table in a solution, not the default environment.
