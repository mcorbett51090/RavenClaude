---
scenario_id: 2026-06-05-soql-in-loop-101-on-trigger
contributed_at: 2026-06-05
plugin: salesforce
product: apex
product_version: "unknown"
scope: likely-general
tags: [governor-limits, soql-101, soql-in-loop, bulkification, trigger, data-load]
confidence: high
reviewed: false
---

## Problem

An Account trigger worked fine in the UI (one record at a time) but blew up with `System.LimitException: Too many SOQL queries: 101` the moment a 250-row Data Loader import touched the object. The handler looped over `Trigger.new` and, for each Account, ran a `SELECT` for its related Contacts to recompute a roll-up field. One record → 1 query; 250 records → 251 queries, tripping the 100-SOQL synchronous ceiling at the 100th Account. The defect was invisible in every manual test and every single-record unit test the team had.

## Constraints context

- The query lived inside a `for (Account a : Trigger.new)` loop — sometimes one method call deep, so it wasn't obvious at the trigger body.
- The org had multiple automations on Account (the trigger plus a record-triggered Flow), so the 100-query budget was *shared* across the whole transaction — the trigger didn't get all 100 to itself.
- The team's only test inserted a single Account, so coverage was green and the bulk path was never exercised.
- `[verify-at-build]` the synchronous SOQL limit is 100 per transaction (200 async) — confirm against the current Apex governor-limits cheat sheet before quoting a number to a stakeholder.

## Attempts

- Tried: raising the worry to "maybe split the import into smaller batches." This is treating the symptom — it makes the failure *less frequent*, not *gone*; a 95-row batch still fails the day a second automation on the object adds two queries. Rejected.
- Tried: wrapping the per-record query in a `try/catch` to swallow the `LimitException`. Worse — it silently dropped the roll-up for every record past the 100th, corrupting data quietly instead of failing loudly. Rejected.
- Tried (the fix): **hoist the query out of the loop.** Collect every Account Id into a `Set<Id>` in one pass, run one `SELECT Contact ... WHERE AccountId IN :accountIds`, bucket the results into a `Map<Id, List<Contact>>`, then loop the in-memory map to compute the roll-up. 251 queries collapsed to 1. Then added a **200-record bulk test** asserting the roll-up values, so the regression can't silently return.

## Resolution

**A SOQL (or DML) statement inside a loop is a defect, not a style nit — the only correct count is one query for the whole batch.** The reliable shape:

1. **First pass — collect keys.** Loop `Trigger.new` once, gather the foreign keys (`AccountId`s) into a `Set<Id>`. No query in this loop.
2. **One bulk query, bound by `IN`.** `[SELECT Id, AccountId, ... FROM Contact WHERE AccountId IN :accountIds]` — a single query regardless of batch size.
3. **Bucket into a Map for O(1) lookup.** Build `Map<Id, List<Contact>>` keyed on `AccountId` so the compute loop never touches the database.
4. **Second pass — compute from memory.** Loop the records, read children from the map, set the field. Accumulate any DML into one `update`.
5. **Prove it with a 200-record bulk test that asserts outcomes**, not just coverage. A single-record test cannot catch this class of bug — the limit is only reached at volume.

The trap is that the per-record query is *correct in isolation* and the failure scales with data, so it survives every interactive test and ships. The budget is also **shared** across all automations in the transaction, so "it's only 1 query per record" is never the real arithmetic.

**Action for the next engineer:** when you see `Too many SOQL queries: 101` (or `Too many DML statements: 151`), don't reach for batch-size or `try/catch` — find the query/DML inside a loop (it may be a method call deep), hoist it, bind with `IN :ids`, and add a 200-record bulk test before you call it fixed.

Cross-reference: the canonical guidance is [`../knowledge/governor-limits-and-bulkification.md`](../knowledge/governor-limits-and-bulkification.md) and the **Bulk Safety** decision tree in [`../knowledge/apex-decision-trees.md`](../knowledge/apex-decision-trees.md); the rules are [`../best-practices/apex-soql-in-loops-is-a-defect.md`](../best-practices/apex-soql-in-loops-is-a-defect.md) and [`../best-practices/bulkify-every-soql-and-dml.md`](../best-practices/bulkify-every-soql-and-dml.md). House opinions #1 (bulkify everything) and #9 (test for bulk, assert outcomes).
