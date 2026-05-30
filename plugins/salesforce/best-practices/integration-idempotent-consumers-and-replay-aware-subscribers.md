# Make event consumers idempotent and replay-aware — delivery is at-least-once, not exactly-once

**Status:** Absolute rule — a non-idempotent consumer that double-processes a redelivered event is a data-corruption bug, not a tuning issue.

**Domain:** Integration / Eventing

**Applies to:** `salesforce`

---

## Why this exists

Platform Events and Change Data Capture (CDC) are **eventually delivered with replay**, not synchronous RPC. A subscriber can receive the same event more than once (redelivery after a disconnect, an Apex trigger that retries, a consumer that resumes from a stored Replay Id), and it can also *miss* events if it is offline longer than the replay window. Two consequences fall out. First: every consumer must be **idempotent** — processing the same event twice must produce the same end state as processing it once, or you get duplicate orders, double-charged invoices, doubled roll-ups. Second: a durable consumer must **track its Replay Id** and resume from it, and must have a backstop for the case where its last-seen Replay Id has aged out of the window. Assuming exactly-once delivery is the single most common eventing defect.

## How to apply

Carry a stable business key (or the event's Replay Id) and guard the side effect against re-processing. An Apex Platform Event trigger should dedupe on a key and use the `EventBus.TriggerContext` Replay Id to resume cleanly after a partial failure.

```apex
// DO — idempotent Platform Event subscriber: dedupe on a business key before acting
trigger OrderShippedSub on Order_Shipped__e (after insert) {
    Set<String> keys = new Set<String>();
    for (Order_Shipped__e e : Trigger.new) keys.add(e.Order_Id__c);

    // Already-processed keys -> skip; the marker makes re-delivery a no-op
    Set<String> done = new Set<String>();
    for (Processed_Event__c p : [SELECT Key__c FROM Processed_Event__c WHERE Key__c IN :keys]) {
        done.add(p.Key__c);
    }
    List<Processed_Event__c> markers = new List<Processed_Event__c>();
    for (Order_Shipped__e e : Trigger.new) {
        if (done.contains(e.Order_Id__c)) continue;   // redelivery -> no-op
        // ... perform the side effect once ...
        markers.add(new Processed_Event__c(Key__c = e.Order_Id__c));
    }
    insert markers;
    // On uncaught failure, set Replay Id to resume from the last good event:
    // EventBus.TriggerContext.currentContext().setResumeCheckpoint(lastReplayId);
}
```

```apex
// DON'T — act on every delivery with no dedupe; a redelivered event double-applies
trigger OrderShippedSub on Order_Shipped__e (after insert) {
    for (Order_Shipped__e e : Trigger.new) chargeInvoice(e.Order_Id__c);  // double-charge on replay
}
```

**Do:**
- Dedupe each event on a stable business key (or Replay Id) before performing the side effect.
- Track and persist the Replay Id for durable external subscribers; resume from it after a disconnect.
- Have a backstop (reconciliation query / Bulk re-sync) for when the consumer falls outside the replay window.
- Treat the publish as bulk and the consume as idempotent — both ends matter.

**Don't:**
- Assume exactly-once delivery — both Platform Events and CDC are at-least-once with a finite replay window.
- Perform a non-idempotent side effect (charge, create, increment) directly off raw delivery.
- Let a consumer stay offline past the replay window without a re-sync plan.

## Edge cases / when the rule does NOT apply

A genuinely idempotent side effect (a set-to-absolute-value field update, an upsert keyed on the event's business key) is naturally replay-safe and needs no extra marker table. High-volume Platform Events have a longer replay window than standard events but still finite — verify the current standard vs high-volume retention windows `[verify-at-build]`. For cross-cloud durability beyond the replay window, queue events into Azure middleware (`azure-cloud/*`) where the broker provides its own retention. CDC field-level deltas may arrive coalesced or out of order under load — design the consumer to apply latest-wins, not append.

## See also

- [`./integration-platform-events-vs-cdc-vs-callout.md`](./integration-platform-events-vs-cdc-vs-callout.md) — choosing the notification mechanism in the first place
- [`../knowledge/integration-patterns.md`](../knowledge/integration-patterns.md) — Fire-and-Forget and UI-Update-from-Data-Changes patterns
- [`../knowledge/integration-data-decision-trees.md`](../knowledge/integration-data-decision-trees.md) — the integration-pattern and pub-sub trees
- [`../agents/salesforce-platform-architect.md`](../agents/salesforce-platform-architect.md) — owns the eventing design and Azure-durability coordination

## Provenance

Codifies the eventual-delivery-with-replay and bulk-publish guidance from [`../knowledge/integration-patterns.md`](../knowledge/integration-patterns.md) and the replay-window caveat in [`./integration-platform-events-vs-cdc-vs-callout.md`](./integration-platform-events-vs-cdc-vs-callout.md). At-least-once delivery, Replay Id resume, and replay-window retention are Salesforce platform behaviors; exact retention windows tagged `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
