# Stream large result sets with Batch Apex QueryLocator — not one 50k-row SOQL

**Status:** Absolute rule at volume — a single SOQL that exceeds the per-transaction row limit throws; a heap-busting in-memory list is a `LimitException`, not a slow path.

**Domain:** Data / LDV / Apex async

**Applies to:** `salesforce`

---

## Why this exists

A single synchronous transaction can only retrieve a bounded number of rows and hold a bounded heap. Try to `SELECT` and process millions of rows in one go and you hit the **total-rows-retrieved** governor limit or blow the heap — the job dies mid-way with nothing committed. **Batch Apex** exists precisely for this: its `start` method returns a `Database.QueryLocator` that can span far more rows than a synchronous query (into the millions), and the platform feeds them to `execute` in **chunks** (default 200, tunable down via the scope argument). Each chunk runs in its own transaction with a fresh governor budget, so a 5-million-row recalculation runs as thousands of small, independently-limited transactions instead of one impossible one. Using a single SOQL where Batch belonged is how a data-fix script works in a 10k-row sandbox and dies in production.

## How to apply

Return a `QueryLocator` (selective, indexed filter) from `start`; do the per-chunk work bulk-safely in `execute`; reconcile in `finish`. Tune the scope down if each row's processing is heavy.

```apex
// DO — Batch Apex streams a large, selective query in governor-bounded chunks
public class RecalcAccountTier implements Database.Batchable<SObject>, Database.Stateful {
    public Database.QueryLocator start(Database.BatchableContext bc) {
        // Selective, indexed filter — the locator can span millions of rows
        return Database.getQueryLocator([
            SELECT Id, AnnualRevenue, Tier__c
            FROM Account
            WHERE LastModifiedDate >= :cutoff          // bounded, indexed
        ]);
    }
    public void execute(Database.BatchableContext bc, List<Account> scope) {
        for (Account a : scope) a.Tier__c = tierFor(a.AnnualRevenue);  // bulk-safe, no SOQL/DML in loop
        update scope;                                                  // one DML per chunk
    }
    public void finish(Database.BatchableContext bc) { /* reconcile / chain / notify */ }
}
// Run with a tuned scope when per-row work is heavy:
Database.executeBatch(new RecalcAccountTier(), 100);
```

```apex
// DON'T — one synchronous query + in-memory loop over a huge object
List<Account> all = [SELECT Id, AnnualRevenue FROM Account];  // hits total-rows limit / heap at volume
for (Account a : all) { a.Tier__c = tierFor(a.AnnualRevenue); }
update all;  // and one giant DML
```

**Do:**
- Use Batch Apex (`Database.QueryLocator`) for any operation spanning more rows than a single transaction can hold.
- Keep the `start` query **selective and indexed** — the locator still runs through the optimizer.
- Tune the scope (chunk size) **down** when per-record processing is heavy, to stay inside per-chunk limits.
- Stay bulk-safe inside `execute` — no SOQL/DML in a loop within the chunk.

**Don't:**
- `SELECT` a high-volume object into a single in-memory list and loop it synchronously.
- Assume a non-selective `start` query is fine — a non-selective locator on an LDV object still errors.
- Forget that each chunk is its own transaction — don't carry un-`Stateful` state across them.

## Edge cases / when the rule does NOT apply

A query that returns well under the synchronous row/heap limits doesn't need Batch — the async overhead isn't worth it. For pure data movement out of (or into) the org, **Bulk API 2.0** is often the better tool than Batch Apex (`./integration-bulk-api-for-batch-not-row-by-row-rest.md`). Batch has its own limits (concurrent batch jobs, items in the flex queue, callouts-per-chunk if `Database.AllowsCallouts`) — for callout fan-out, prefer events. Exact per-transaction row caps, default/min scope, and batch-job concurrency are version-sensitive — verify against the current limits cheat sheet `[verify-at-build]`.

## See also

- [`./data-selective-soql-on-indexed-fields.md`](./data-selective-soql-on-indexed-fields.md) — the locator query must still be selective
- [`../knowledge/large-data-volume-design.md`](../knowledge/large-data-volume-design.md) — "Batch Apex with QueryLocator — stream large sets instead of one 50k-row SOQL"
- [`../knowledge/apex-async-patterns.md`](../knowledge/apex-async-patterns.md) — Future vs Queueable vs Batch selection
- [`./integration-bulk-api-for-batch-not-row-by-row-rest.md`](./integration-bulk-api-for-batch-not-row-by-row-rest.md) — when Bulk API beats Batch Apex
- [`../knowledge/integration-data-decision-trees.md`](../knowledge/integration-data-decision-trees.md) — the LDV-query decision tree

## Provenance

Codifies the levered guidance in [`../knowledge/large-data-volume-design.md`](../knowledge/large-data-volume-design.md) ("Use Batch Apex / QueryLocator, not a single SOQL") and the bulkification discipline from [`../knowledge/governor-limits-and-bulkification.md`](../knowledge/governor-limits-and-bulkification.md). Batch Apex semantics, QueryLocator row capacity, and scope behavior are Salesforce platform features; exact numbers tagged `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
