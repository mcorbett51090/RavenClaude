# Choose the async channel deliberately — Batch, Queueable, Future, or Scheduled

**Status:** Pattern — strong default; the choice must be justified against the workload, not picked by habit.

**Domain:** Apex / asynchronous processing

**Applies to:** `salesforce`

---

## Why this exists

Async Apex moves work off the synchronous transaction for larger data volume, higher limits, and the ability to make callouts. But the four channels are **not interchangeable**: `@future` can't take object parameters or chain; `Queueable` chains and carries complex state; `Batch` streams millions of rows in scoped chunks; `Schedulable` only handles cron timing. Picking the wrong primitive produces stuck jobs, blown chaining depth, or a `@future` that can't pass the data it needs. `@future` is effectively legacy — `Queueable` supersedes it for nearly every new use. This is the design decision behind house-opinion-adjacent async discipline.

## How to apply

Match the channel to the workload's dominant constraint: data volume → Batch; chaining/state → Queueable; simple fire-and-forget callout → Future (or Queueable); cron → Schedulable kicking off the real work.

```apex
// DON'T — @future can't take an sObject; you lose the data and can't chain
@future
public static void recalc(List<Account> accts) { /* won't compile — no sObject params */ }

// DO — Queueable carries object state and can chain the next job
public class AccountRollupQueueable implements Queueable {
    private final List<Account> accounts;             // complex state travels with the job
    public AccountRollupQueueable(List<Account> accounts) { this.accounts = accounts; }

    public void execute(QueueableContext ctx) {
        // ...bulk-safe work on this.accounts...
        if (moreWorkRemains) {
            System.enqueueJob(new AccountRollupQueueable(nextChunk));  // chain
        }
    }
}

// DO — Batch for large data volume; QueryLocator streams, doesn't load 50k at once
public class AccountArchiveBatch implements Database.Batchable<SObject> {
    public Database.QueryLocator start(Database.BatchableContext bc) {
        return Database.getQueryLocator([SELECT Id FROM Account WHERE Last_Activity__c < :cutoff]);
    }
    public void execute(Database.BatchableContext bc, List<Account> scope) { /* per-chunk */ }
    public void finish(Database.BatchableContext bc) { /* chain / notify */ }
}
```

**Do:**
- Use **Batch** when processing exceeds tens of thousands of rows or needs `QueryLocator` streaming.
- Use **Queueable** when you must pass object state or chain jobs sequentially.
- Use **Schedulable** only for cron timing — let it enqueue a Batch/Queueable for the real work.
- Reserve **`@future`** for the narrow legacy case of a simple, primitive-param, fire-and-forget callout — and prefer Queueable even there.

**Don't:**
- Reach for `@future` when you need to pass an sObject or chain — it can do neither.
- Run a high-volume job synchronously to "avoid the async complexity" — it will hit limits at scale.
- Lean on the higher async limit budget to excuse an unbulkified loop (see the bulkify rule).

## Edge cases / when the rule does NOT apply

Chaining depth is constrained — `Queueable` chaining from a synchronous context is limited, and you can't enqueue from within a Batch `execute` without care. Mixed-DML restrictions (setup vs non-setup objects) often *force* an async hop regardless of channel choice. A callout that must happen inside a trigger context must be deferred to `@future(callout=true)` or Queueable because triggers can't call out synchronously. Exact daily async-execution and concurrency caps are volatile — verify against the current limits cheat sheet `[verify-at-build]`.

## See also

- [`../knowledge/apex-async-patterns.md`](../knowledge/apex-async-patterns.md) — the channel comparison table and limits
- [`../knowledge/apex-decision-trees.md`](../knowledge/apex-decision-trees.md) — the async-channel-selection decision tree
- [`../templates/batch-apex-class.md`](../templates/batch-apex-class.md) — the Batchable skeleton
- [`./bulkify-every-soql-and-dml.md`](./bulkify-every-soql-and-dml.md) — async headroom is not a license to skip bulkification
- [`../agents/apex-engineer.md`](../agents/apex-engineer.md) — owns the async choice

## Provenance

Grounded in [`../knowledge/apex-async-patterns.md`](../knowledge/apex-async-patterns.md), sourced from the async-Apex complete-guide reference. Reflects the `apex-engineer` discipline #3 ("choose async deliberately") in [`../CLAUDE.md`](../CLAUDE.md). Limit numbers tagged `[verify-at-build]` per house convention.

---

_Last reviewed: 2026-05-30 by `claude`_
