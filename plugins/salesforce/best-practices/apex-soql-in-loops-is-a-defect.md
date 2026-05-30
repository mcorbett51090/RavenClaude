# `Too many SOQL queries: 101` means a query is inside a loop — find it first

**Status:** Primary diagnostic — when this LimitException appears, the SOQL-in-a-loop is the first thing to check.

**Domain:** Apex / governor-limit diagnostics

**Applies to:** `salesforce`

---

## Why this exists

`System.LimitException: Too many SOQL queries: 101` is the single most common runtime governor-limit failure, and it has one dominant cause: a `SELECT` executing once per record inside a `for`/`while` body. The trap is that the code *passes every test and demo* — one record means one query, comfortably under the 100-synchronous ceiling — and only fails when a data load, a record-triggered batch of 200, or a Bulk API job arrives in production. This doc is the **diagnostic companion** to the bulkify rule: that rule says "don't write it," this one says "when you see the exception, here is where to look and how to confirm it." The fix is always structural (hoist + map), never "raise the limit."

## How to apply

When the exception fires, grep the offending class for a `SELECT` (or `[...]` query) whose enclosing braces are a loop. The count in the message ÷ your batch size usually equals the number of loop iterations — a strong tell. Then convert to the collect-once / query-once / map-lookup shape.

```apex
// SYMPTOM — "Too many SOQL queries: 101" at 101+ records.
// The query is inside the loop: 1 query per Account.
for (Account a : Trigger.new) {
    List<Opportunity> opps =
        [SELECT Id, Amount FROM Opportunity WHERE AccountId = :a.Id];   // <-- the defect
    a.Open_Pipeline__c = sum(opps);
}

// FIX — one query keyed by the whole batch, map for O(1) in-loop lookup.
Map<Id, Decimal> pipelineByAccount = new Map<Id, Decimal>();
for (AggregateResult ar : [
        SELECT AccountId, SUM(Amount) total
        FROM Opportunity
        WHERE AccountId IN :Trigger.newMap.keySet()
        GROUP BY AccountId]) {
    pipelineByAccount.put((Id) ar.get('AccountId'), (Decimal) ar.get('total'));
}
for (Account a : Trigger.new) {
    a.Open_Pipeline__c = pipelineByAccount.get(a.Id);   // no query in the loop
}
```

**Do:**
- Treat the `101` exception as "a query is in a loop" until proven otherwise — check that first.
- Look inside **helper methods called from the loop**, not just the loop body — a query one call deep still counts per iteration.
- Confirm the fix with a 200-record test that would have thrown before the change.

**Don't:**
- "Fix" it by moving the work to `@future`/Batch for the 200-query async budget — that only doubles the headroom and still breaks at 201.
- Add `LIMIT 1` to the in-loop query — it still counts as one query per iteration.

## Edge cases / when the rule does NOT apply

The same exception with a *low* count after a single record points elsewhere — a recursive trigger re-entering and re-querying (see the recursion-control rule), or a class that legitimately runs many distinct queries in one transaction approaching the cap by accumulation rather than by loop multiplication. Aggregate queries (`COUNT`, `SUM`, `GROUP BY`) still count as **one** SOQL query regardless of rows scanned, so they're a valid in-transaction tool — just never *inside* the loop. SOSL and `Database.countQuery` have their own separate limits but the same loop-placement diagnostic applies.

## See also

- [`./bulkify-every-soql-and-dml.md`](./bulkify-every-soql-and-dml.md) — the don't-write-it rule this diagnoses
- [`./apex-collections-and-maps-for-o1-lookups.md`](./apex-collections-and-maps-for-o1-lookups.md) — the map pattern that replaces the in-loop query
- [`./apex-recursion-control-on-handlers.md`](./apex-recursion-control-on-handlers.md) — the other cause of unexpected query counts
- [`../knowledge/governor-limits-and-bulkification.md`](../knowledge/governor-limits-and-bulkification.md) — the limits table and bulk-safe decision tree
- [`../knowledge/apex-decision-trees.md`](../knowledge/apex-decision-trees.md) — the SOQL-selectivity tree
- [`../agents/apex-engineer.md`](../agents/apex-engineer.md) — owns governor-limit discipline

## Provenance

Codifies the diagnostic side of house opinion #1 from [`../CLAUDE.md`](../CLAUDE.md). Grounded in [`../knowledge/governor-limits-and-bulkification.md`](../knowledge/governor-limits-and-bulkification.md), whose limit numbers are sourced from Salesforce Apex governor-limit documentation and tagged `[verify-at-build]`. The synchronous 100-query / asynchronous 200-query ceiling is a documented platform limit.

---

_Last reviewed: 2026-05-30 by `claude`_
