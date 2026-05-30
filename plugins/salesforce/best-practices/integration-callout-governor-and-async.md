# Budget the callout limits and never call out from a trigger synchronously

**Status:** Absolute rule — a callout inside an open DML transaction is a runtime error; the cumulative limits are a design constraint, not a runtime surprise.

**Domain:** Integration / Apex async

**Applies to:** `salesforce`

---

## Why this exists

Apex callouts run inside the multi-tenant governor envelope, and two rules catch teams repeatedly. First: **you cannot make a callout after uncommitted DML in the same transaction** — so a trigger that updates records and then calls out throws `You have uncommitted work pending`. The fix is to move the callout async (`@future(callout=true)`, Queueable implementing `Database.AllowsCallouts`, or Batch), which also decouples the user's save from the remote system's latency. Second: callouts are **capped per transaction** — a bounded number of callouts and a cumulative timeout budget across all of them — so a loop that calls out per record blows the limit at volume exactly like SOQL-in-a-loop does. A synchronous callout also holds a long-running concurrent-request slot, of which the org has very few. Designing the callout placement (async, bulk, timeout-bounded) is as load-bearing as bulkifying SOQL.

## How to apply

Trigger collects the work; an async Queueable (callout-enabled) does the callout after the DML commits. The callout is made once for the batch, with an explicit timeout.

```apex
// DO — trigger enqueues; Queueable calls out AFTER the transaction commits
public with sharing class SyncAccountsToErp implements Queueable, Database.AllowsCallouts {
    private final Set<Id> accountIds;
    public SyncAccountsToErp(Set<Id> ids) { this.accountIds = ids; }

    public void execute(QueueableContext ctx) {
        // One callout for the batch — not one per record
        HttpRequest req = new HttpRequest();
        req.setEndpoint('callout:My_ERP/accounts/sync');
        req.setMethod('POST');
        req.setTimeout(120000);                         // explicit, under the per-transaction cap
        req.setBody(JSON.serialize([SELECT Id, Name FROM Account WHERE Id IN :accountIds]));
        HttpResponse res = new Http().send(req);
        // handle res.getStatusCode(); persist failures for retry
    }
}
// In the trigger handler (after the DML is queued, not in a loop):
System.enqueueJob(new SyncAccountsToErp(accountIdSet));
```

```apex
// DON'T — synchronous callout in the trigger, inside a loop, after DML
for (Account a : Trigger.new) {
    update a;                       // uncommitted DML...
    new Http().send(buildReq(a));   // ...then a callout -> "uncommitted work pending"; and N callouts in a loop
}
```

**Do:**
- Move any trigger-path callout **async** (`@future(callout=true)`, `Queueable implements Database.AllowsCallouts`, or Batch).
- Make **one callout for the batch**, not one per record — aggregate into a single request or a bulk endpoint.
- Set an explicit `setTimeout` and budget it against the cumulative per-transaction callout time cap.
- Persist failures so the async job can be retried/replayed rather than silently lost.

**Don't:**
- Call out synchronously from a trigger or from any context with pending uncommitted DML.
- Put `Http().send()` inside a loop over records.
- Leave the timeout at the default and assume the remote system is fast.

## Edge cases / when the rule does NOT apply

A genuinely synchronous **request-reply** from a controller/LWC action (user clicks, waits for the answer) is correctly synchronous — there is no trigger DML to conflict with, and the user is waiting on purpose. `Database.setSavepoint`/rollback does not let you call out mid-transaction — the uncommitted-DML rule still bites. For high fan-out, prefer publishing a Platform Event (the producer never blocks) over orchestrating many async callouts. Exact per-transaction callout count, cumulative timeout, and concurrent-long-running-request caps shift across releases — verify against the current limits cheat sheet `[verify-at-build]`.

## See also

- [`../knowledge/apex-async-patterns.md`](../knowledge/apex-async-patterns.md) — Future vs Queueable vs Batch for the async callout
- [`../knowledge/governor-limits-and-bulkification.md`](../knowledge/governor-limits-and-bulkification.md) — the per-transaction limit envelope the callout shares
- [`./integration-platform-events-vs-cdc-vs-callout.md`](./integration-platform-events-vs-cdc-vs-callout.md) — when an event beats a callout entirely
- [`../knowledge/integration-data-decision-trees.md`](../knowledge/integration-data-decision-trees.md) — sync-vs-async callout tree
- [`./bulkify-every-soql-and-dml.md`](./bulkify-every-soql-and-dml.md) — the same no-IO-in-a-loop discipline

## Provenance

Codifies the callout/limit discipline from [`../knowledge/integration-patterns.md`](../knowledge/integration-patterns.md) ("synchronous callouts hold a long-running concurrent request slot and have a per-transaction time cap") and the async-primitive guidance in [`../knowledge/apex-async-patterns.md`](../knowledge/apex-async-patterns.md). The uncommitted-work-pending rule and per-transaction callout caps are Salesforce platform behavior; exact numbers tagged `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
