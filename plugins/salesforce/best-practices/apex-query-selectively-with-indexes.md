# Query selectively — filter on indexed fields so the optimizer can use them

**Status:** Absolute rule on high-volume objects — a non-selective query is a `QueryException` waiting for the row count to grow.

**Domain:** Apex / SOQL selectivity & LDV

**Applies to:** `salesforce`

---

## Why this exists

The Salesforce **query optimizer** picks an index only when a filter is *selective* — when it estimates the predicate returns fewer rows than a threshold (a row count and a percentage of the object's total). A query that filters on a non-indexed field, uses a leading-`%` wildcard, or uses a negative operator forces a full table scan; on a small object that's invisible, but past roughly a million rows it produces `System.QueryException: Non-selective query against large object type`. The failure is **invisible until the data grows**, which is why house opinion #13 says design for LDV from day one — the query you write against 10k rows in a sandbox must still be selective at 50M in production.

## How to apply

Filter on a standard-indexed field (`Id`, `Name`, audit fields, lookups, external IDs, unique fields) or a custom index, keep the predicate selective (bounded date/status windows), and avoid the constructs that defeat the index.

```apex
// DON'T — non-indexed field + leading wildcard + negative operator = full scan
List<Case> stuck = [
    SELECT Id FROM Case
    WHERE Description LIKE '%escalat%'     // leading % can't use an index
      AND Status != 'Closed'              // negative operator defeats the index
];

// DO — indexed, selective, bounded
List<Case> recentOpen = [
    SELECT Id, Subject FROM Case
    WHERE Status IN ('New', 'Working')    // positive set on an indexed picklist
      AND CreatedDate >= :Date.today().addDays(-30)   // bounded window on indexed audit field
      AND AccountId IN :accountIds        // indexed lookup, bound collection
    LIMIT 10000
];
```

**Do:**
- Filter on **indexed** fields: `Id`, `Name`, audit fields (`CreatedDate`, `SystemModstamp`), lookups/master-detail, external IDs, unique fields, or a custom index (request via Support / `__c` external-ID flag).
- Use **positive, bounded** predicates — an explicit status set and a date window, not "everything that isn't closed forever."
- For genuinely large result sets, stream with **Batch Apex `QueryLocator`** instead of one 50k-row SOQL.
- Use the **Query Plan tool** (Developer Console) to confirm the optimizer chose an index (cost < 1.0). `[verify-at-build]`

**Don't:**
- Filter with a **leading `%`** wildcard (`LIKE '%foo'`) — the index can't be used.
- Use `!=`, `NOT`, `NOT IN`, or `!= null` as the **only** filter on a large object — negative operators are non-selective.
- Rely on `LIMIT` to rescue a non-selective query — `LIMIT` caps the result, the optimizer still scans to find them.

## Edge cases / when the rule does NOT apply

Selectivity only matters at **volume** — on a low-row object the optimizer may table-scan and never warn, so a non-indexed filter there is a latent risk, not a current bug. A **two-column custom index** can make a compound filter selective even when neither column is alone. Skinny tables (Salesforce-managed, request via Support) sidestep base-table joins for frequent reporting queries. The selectivity threshold itself is a moving platform value — confirm against the current LDV documentation rather than memorizing a number `[verify-at-build]`.

## See also

- [`../knowledge/large-data-volume-design.md`](../knowledge/large-data-volume-design.md) — the LDV-safe-query decision tree, skinny tables, archival
- [`../knowledge/apex-decision-trees.md`](../knowledge/apex-decision-trees.md) — the SOQL-selectivity / indexing decision tree
- [`../skills/soql-authoring/SKILL.md`](../skills/soql-authoring/SKILL.md) — the step-by-step selective-query authoring skill
- [`./apex-bind-variables-in-dynamic-soql.md`](./apex-bind-variables-in-dynamic-soql.md) — bind the collections you filter on
- [`../agents/apex-engineer.md`](../agents/apex-engineer.md) — owns query selectivity

## Provenance

Codifies house opinion #13 from [`../CLAUDE.md`](../CLAUDE.md). Grounded in [`../knowledge/large-data-volume-design.md`](../knowledge/large-data-volume-design.md), sourced from the ApexHours query-optimizer-for-LDV reference. The standard-index list, the leading-wildcard / negative-operator index defeats, and the non-selective-query exception are documented Salesforce platform behaviors; exact thresholds tagged `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
