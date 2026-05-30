# Match the notification mechanism to who owns the schema — Platform Events vs Change Data Capture vs callout

**Status:** Pattern — strong default; deviate only with a written reason naming who owns the event shape and who consumes it.

**Domain:** Integration

**Applies to:** `salesforce`

---

## Why this exists

"Notify another system when something happens in Salesforce" has three structurally different answers, and picking the wrong one bakes in either a maintenance tax or a missed-event gap. **Platform Events** are a custom, publish-subscribe contract you design (`__e` object, defined fields) — best when *you* own the event shape and want to decouple producer from consumer. **Change Data Capture (CDC)** emits Salesforce-managed change events for record create/update/delete/undelete on standard or custom objects — best when the consumer wants the *record's field-level deltas* and you don't want to hand-author a publish for every DML path. A **synchronous callout** is neither — it's request-reply, couples the transaction to the remote system's availability, and consumes a long-running request slot. Choosing a callout where a Platform Event belonged turns a remote outage into a Salesforce transaction failure; choosing a Platform Event where CDC belonged means hand-publishing change events that CDC would have emitted for free.

## How to apply

When you own the event contract and want decoupling, publish a Platform Event with `EventBus.publish`. The publish is transactional (or immediate, per the event's publish behavior) and the producer never waits on the consumer.

```apex
// DO — fire-and-forget notification on a contract YOU own; producer doesn't block on the consumer
public with sharing class OrderShippedNotifier {
    public void notify(List<Order> shipped) {
        List<Order_Shipped__e> events = new List<Order_Shipped__e>();
        for (Order o : shipped) {
            events.add(new Order_Shipped__e(
                Order_Id__c = o.Id,
                Shipped_At__c = o.Shipped_Date__c
            ));
        }
        // One bulk publish — never publish inside a loop (shares the DML/event limit budget)
        List<Database.SaveResult> results = EventBus.publish(events);
        // Inspect results for partial failures; events can be replayed via Replay Id
    }
}
```

```apex
// DON'T — synchronous callout in the trigger path to "notify" — couples the save to a remote system
// A remote 500 now rolls back the user's order save.
HttpResponse res = new Http().send(req);   // wrong mechanism for fire-and-forget notification
```

**Do:**
- Use **Platform Events** when you own the event shape and want producer/consumer decoupling and replay.
- Use **CDC** when the consumer wants record-level change deltas and you don't want to author a publish per DML path — subscribe a channel rather than instrument every trigger.
- Publish events **in bulk** (`EventBus.publish(List)`), never one per loop iteration.
- Keep callouts for genuine **request-reply** where you need the response in-transaction.

**Don't:**
- Put a synchronous callout in a trigger/save path to "send a notification" — that couples the save to a remote outage.
- Hand-roll Platform Event publishes to mirror every field change when CDC already emits those deltas.
- Assume delivery is guaranteed-instant — both Platform Events and CDC are eventually-delivered with replay, not synchronous RPC.

## Edge cases / when the rule does NOT apply

If the consumer genuinely needs a value back *before the transaction commits* (a credit check that gates the save), that is request-reply — a callout (often async-orchestrated) is correct, not an event. CDC has per-object enablement and a daily delivery allocation; very high-churn objects can exhaust it, in which case a curated Platform Event carrying only the fields the consumer needs is leaner. Platform Events have their own daily publish allocation and a 24-hour (standard) / 72-hour (high-volume) replay window — a consumer offline longer than the window misses events, so durable downstream queuing (often via `azure-cloud/*` middleware) is the backstop. Verify current event allocations and replay windows `[verify-at-build]`.

## See also

- [`../knowledge/integration-patterns.md`](../knowledge/integration-patterns.md) — Fire-and-Forget and UI-Update-from-Data-Changes patterns
- [`../knowledge/integration-data-decision-trees.md`](../knowledge/integration-data-decision-trees.md) — the request-reply vs fire-forget vs pub-sub decision tree
- [`./integration-callout-governor-and-async.md`](./integration-callout-governor-and-async.md) — why a callout doesn't belong in the save path
- [`../agents/salesforce-platform-architect.md`](../agents/salesforce-platform-architect.md) — owns the pattern pick; coordinates Azure eventing with `azure-cloud/*`

## Provenance

Codifies the Fire-and-Forget vs UI-Update vs Request-Reply distinction from [`../knowledge/integration-patterns.md`](../knowledge/integration-patterns.md) (six canonical patterns) and the limit-budget note there. Platform Events / CDC mechanics and allocations are Salesforce platform features; exact allocations and replay windows are version-sensitive and tagged `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
