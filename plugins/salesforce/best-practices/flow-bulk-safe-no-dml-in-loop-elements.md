# Keep Flows bulk-safe — no Get/Create/Update/Delete inside a Loop element

**Status:** Absolute rule. A DML or query element inside a Flow Loop is a bug, not a preference.

**Domain:** Declarative automation / governor limits

**Applies to:** `salesforce`

---

## Why this exists

Flow consumes the **same per-transaction governor limits as Apex** — 100 SOQL queries and 150 DML statements synchronous, and the same row caps. A Get Records or any Create/Update/Delete element placed *inside* a Loop runs once per iteration: loop over 200 records and you have issued 200 queries or 200 DML statements, blowing the limit and rolling back the whole transaction. House opinion #1 ("no SOQL or DML in a loop, ever") is written for Apex but is **identical** in Flow — the canvas just hides the loop body, so the anti-pattern is easier to draw without noticing.

## How to apply

Build the bulk-safe shape: query/collect **before** the loop, mutate records into a **collection variable** *inside* the loop, and do **one** DML element **after** the loop.

```
GOOD (one DML, bulk-safe):
  Get Records (Children)  ->  query all related children ONCE, store in collection
  Loop over {!Children} as {!loopItem}
      Assignment: {!loopItem.Status__c} = "Reviewed"
      Assignment: add {!loopItem} to collection {!toUpdate}     (Add to collection)
  (End Loop)
  Update Records: {!toUpdate}                                    (ONE DML, after the loop)

BAD (DML in loop — 200 children = 200 DML statements):
  Loop over {!Children} as {!loopItem}
      Update Records: {!loopItem}        <-- DML inside the loop. Never.
```

The same applies to **Get Records**: never query inside a loop. Use a single Get with an `IN`-style filter (collection of Ids) before the loop, then look up matches in memory.

**Do:**
- Collect into a record collection variable inside the loop; run one Create/Update/Delete after.
- Move every Get Records outside the loop and filter by a collection of Ids.

**Don't:**
- Place any Create/Update/Delete/Get element on a path that is inside a Loop.
- Assume "this only runs on one record at a time" — record-triggered Flows are invoked in **batches of up to 200**, and data loads / bulk API drive them at scale.

## Edge cases / when the rule does NOT apply

Pure in-memory work inside a loop (Assignment, Decision, building a collection) is fine and expected — only **DML and SOQL** elements are forbidden in the loop. A loop that genuinely must call an external system per item is past the declarative ceiling: move it to Apex (queueable/batch) — see [`../knowledge/flow-vs-apex-decision.md`](../knowledge/flow-vs-apex-decision.md). Scheduled-path and async-after-commit Flows still consume limits per transaction; the rule holds there too.

## See also

- [`bulkify-every-soql-and-dml.md`](./bulkify-every-soql-and-dml.md) — the Apex statement of the same rule
- [`flow-entry-conditions-and-fault-paths.md`](./flow-entry-conditions-and-fault-paths.md) — entry filters reduce how often the loop runs
- [`flow-vs-apex-one-entry-point.md`](./flow-vs-apex-one-entry-point.md) — when loop work belongs in Apex instead
- [`../knowledge/governor-limits-and-bulkification.md`](../knowledge/governor-limits-and-bulkification.md) — the shared limit budget

## Provenance

Codifies house opinion #1 from [`../CLAUDE.md`](../CLAUDE.md) applied to Flow, and the limits note in [`../agents/flow-automation-architect.md`](../agents/flow-automation-architect.md) ("a Flow in a loop over a large collection hits the same limits as Apex").

---

_Last reviewed: 2026-05-30 by `claude`_
