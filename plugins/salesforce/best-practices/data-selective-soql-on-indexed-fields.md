# Filter SOQL on indexed, selective fields — defeat the non-selective-query error before it ships

**Status:** Absolute rule on high-volume objects — a non-selective query on an LDV object is a runtime error (`Non-selective query against large object type`), not a slow query.

**Domain:** Data / LDV

**Applies to:** `salesforce`

---

## Why this exists

The Salesforce **query optimizer** picks an index only when a filter is *selective* — when the filter resolves to fewer rows than a threshold (a row count and a percentage of total rows on the object). Below that threshold it uses the index; above it, the query does a full table scan. On a small object a scan is merely slow; on a **large object (LDV)** the platform refuses the query outright with a non-selective-query error to protect the multi-tenant pod. Three things defeat the index even on an indexed field: a **leading-`%` wildcard** (`LIKE '%acme'`), **negative operators** (`!=`, `NOT IN`, `NOT LIKE`), and filtering on a **non-indexed field**. House opinion #13 — design for LDV from day one — exists because the non-selective query that works in a 10k-row sandbox is the production fire at 10M rows.

## How to apply

Filter on a standard-indexed field (Id, Name, audit fields, lookups, external IDs, unique fields) or a custom index, and keep the predicate selective with a bounded date/status filter. Avoid leading wildcards and negative operators on LDV objects.

```apex
// DO — selective: indexed lookup + bounded, indexed date filter; binds its variable
List<Case> recent = [
    SELECT Id, Subject, Status
    FROM Case
    WHERE AccountId = :acctId                       // indexed lookup
      AND CreatedDate >= :startOfQuarter            // bounded, indexed audit field
    WITH SECURITY_ENFORCED
    LIMIT 5000
];
```

```apex
// DON'T — non-selective on an LDV object: leading wildcard + negative operator, no bound
List<Case> bad = [
    SELECT Id FROM Case
    WHERE Subject LIKE '%error%'                     // leading % -> index defeated
      AND Status != 'Closed'                         // negative operator -> index defeated
];  // throws Non-selective query against large object type at volume
```

**Do:**
- Filter on an indexed field; if the natural field isn't indexed, request a custom index (via Support) or add an external ID.
- Keep the predicate **selective** — add a bounded `CreatedDate`/status filter so it clears the optimizer threshold.
- Combine selective filters with `AND` so the optimizer can pick the most selective leading index.
- Bind variables and select only the fields you use (`knowledge/large-data-volume-design.md`).

**Don't:**
- Use a leading-`%` `LIKE` or a negative operator (`!=`, `NOT IN`) as the only filter on an LDV object.
- Filter on an un-indexed field and assume it'll be fine — it won't be at volume.
- Return unbounded result sets — page or move to Batch Apex `QueryLocator` (`./data-batch-apex-for-large-result-sets.md`).

## Edge cases / when the rule does NOT apply

On small objects (below the LDV threshold) a non-selective filter is allowed and merely slower — but writing the query selectively now avoids a refactor when the object grows. A two-column index can be created for compound filters via Support. Formula fields are generally not indexable unless deterministic and explicitly indexed; filtering on a formula often forces a scan. The optimizer's exact selectivity thresholds (absolute row count and percentage) are version-sensitive — verify against the current LDV guidance `[verify-at-build]`. Data skew (one parent owning a huge child share) can defeat selectivity even on an indexed lookup — see `./data-avoid-ownership-and-lookup-skew.md`.

## See also

- [`../skills/soql-authoring/SKILL.md`](../skills/soql-authoring/SKILL.md) — the selective, bind-safe, FLS-enforced query procedure
- [`../knowledge/large-data-volume-design.md`](../knowledge/large-data-volume-design.md) — what makes a query selective and the LDV levers
- [`./data-batch-apex-for-large-result-sets.md`](./data-batch-apex-for-large-result-sets.md) — streaming large sets instead of one SOQL
- [`./data-skinny-tables-and-custom-indexes.md`](./data-skinny-tables-and-custom-indexes.md) — Salesforce-managed levers for hot reporting queries
- [`../knowledge/integration-data-decision-trees.md`](../knowledge/integration-data-decision-trees.md) — the LDV-query and sharing-model trees

## Provenance

Codifies house opinion #13 and the selectivity rules from [`../knowledge/large-data-volume-design.md`](../knowledge/large-data-volume-design.md) (optimizer threshold; index-defeating filters) and the SOQL-authoring skill. Query-optimizer selectivity behavior is Salesforce platform internals; exact thresholds tagged `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
