# Reach for skinny tables and custom indexes when hot queries strain at LDV — but treat them as Support-managed levers

**Status:** Pattern — a tuning lever for proven hot paths, not a day-one default; deviate only after the selective-query and data-model levers are exhausted.

**Domain:** Data / LDV

**Applies to:** `salesforce`

---

## Why this exists

When a high-volume object is queried frequently for reporting or list views and the query still strains after you've made it selective, two Salesforce-managed levers exist. A **custom index** lets the optimizer choose an index on a field that isn't standard-indexed, restoring selectivity to a filter that would otherwise scan. A **skinny table** is a Salesforce-managed copy of a frequently-queried subset of fields from the base object (and a small number of fields from its standard companion table), kept in sync automatically — it avoids the base-table/companion-table join the platform normally does, which is the dominant cost on wide LDV objects. Both are requested through **Salesforce Support**, not self-served, and both have constraints (skinny tables don't include soft-deleted rows or all field types, and they must be re-requested when copied to a new sandbox). They are precision tools: applied to a proven hot path they remove a production fire; applied speculatively they add maintenance surface for no gain.

## How to apply

Exhaust the free levers first (selective indexed filters, narrowing the field list, archival), confirm the query is genuinely hot and still strained, then request the Support-managed lever for that specific query shape.

```text
Order of operations for a strained LDV query:
1. Make it selective  -> indexed field + bounded filter   (./data-selective-soql-on-indexed-fields.md)
2. Narrow the SELECT  -> only the fields actually used
3. Archive cold rows  -> Big Objects / external storage    (./data-archive-cold-rows-to-keep-hot-object-small.md)
4. STILL strained + frequent?  -> request via Support:
   - Custom index  on the filter field (restores optimizer selectivity)
   - Skinny table  on the frequently-read field subset (removes the base/companion join)
```

```apex
// The query is unchanged — the skinny table / custom index is transparent to SOQL.
// You request it for THIS shape, then the optimizer/skinny copy serves it faster:
List<Account> hot = [
    SELECT Id, Name, Industry, AnnualRevenue, Custom_Tier__c   // the skinny-table field subset
    FROM Account
    WHERE Custom_Tier__c = :tier                                // the custom-indexed filter
    WITH SECURITY_ENFORCED
    LIMIT 5000
];
```

**Do:**
- Confirm selectivity and field-narrowing first — skinny tables/indexes are step 4, not step 1.
- Request a **custom index** when a frequently-filtered field isn't standard-indexed and defeats selectivity.
- Request a **skinny table** for a hot, wide-field read on an LDV object to skip the base/companion join.
- Re-request skinny tables after a sandbox refresh — they don't always carry over.

**Don't:**
- Treat skinny tables/custom indexes as a day-one default — they are tuning levers for proven hot paths.
- Assume a skinny table includes every field type or soft-deleted rows — it doesn't.
- Forget that both are **Support-managed** — you can't self-serve them, so plan lead time.

## Edge cases / when the rule does NOT apply

If the query isn't actually hot (run rarely), the maintenance cost outweighs the gain — leave it as a plain selective query. Skinny tables exclude certain field types and don't reflect rows in the recycle bin; a query that needs those can't be served by one. For truly massive cold data, **archival** to Big Objects or external storage (`./data-archive-cold-rows-to-keep-hot-object-small.md`) beats indexing the hot object further. Skinny-table field limits, supported field types, and sandbox-copy behavior are version-sensitive — verify against current LDV guidance `[verify-at-build]`.

## See also

- [`./data-selective-soql-on-indexed-fields.md`](./data-selective-soql-on-indexed-fields.md) — the free selectivity lever to exhaust first
- [`./data-archive-cold-rows-to-keep-hot-object-small.md`](./data-archive-cold-rows-to-keep-hot-object-small.md) — shrinking the hot object instead
- [`../knowledge/large-data-volume-design.md`](../knowledge/large-data-volume-design.md) — skinny tables and custom indexes in the LDV levers list
- [`../skills/soql-authoring/SKILL.md`](../skills/soql-authoring/SKILL.md) — authoring the selective query the index serves
- [`../knowledge/integration-data-decision-trees.md`](../knowledge/integration-data-decision-trees.md) — the LDV-query decision tree

## Provenance

Codifies the skinny-table and custom-index levers from [`../knowledge/large-data-volume-design.md`](../knowledge/large-data-volume-design.md) ("Skinny tables — Salesforce-managed copies of frequently queried fields … request via Support"). Skinny-table and custom-index mechanics, field-type limits, and Support-request requirement are Salesforce platform features; exact limits tagged `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
