---
scenario_id: 2026-06-05-trigger-recursion-runaway-update
contributed_at: 2026-06-05
plugin: salesforce
product: apex
product_version: "unknown"
scope: likely-general
tags: [trigger, recursion, recursion-guard, handler-framework, maximum-trigger-depth, dml]
confidence: high
reviewed: false
---

## Problem

An Opportunity after-update trigger recomputed a field and called `update` on the same Opportunity records. That `update` re-fired the trigger, which updated again, and the transaction died with `System.DmlException: Maximum trigger depth exceeded` (Salesforce caps re-entrant trigger recursion at 16 levels). When it didn't hit the hard cap it still ran the same work 16 times — burning SOQL/DML/CPU budget and, on one bad day, sending 16 duplicate platform-event notifications to a downstream system before the transaction rolled back. The author's mental model was "after-update only runs once," which is true for the *original* save but false the moment the handler issues DML on its own object.

## Constraints context

- The org had **two** triggers on Opportunity (a legacy one plus the new handler) — so even "I only update once" wasn't safe; the other trigger's DML also re-entered.
- A record-triggered Flow on Opportunity *also* updated a field, adding a third re-entry path the Apex author couldn't see from their code.
- `[verify-at-build]` the re-entrant trigger-depth ceiling is 16 — confirm against the current Apex limits reference; the point stands regardless of the exact number.

## Attempts

- Tried: a `Boolean` instance variable on the handler as a "already ran" flag. Failed — a new handler instance is constructed on each trigger invocation, so the instance flag reset every re-entry and guarded nothing. The guard **must** be `static` to survive across invocations within the same transaction.
- Tried: only updating records "that changed" by diffing old vs new. Reduced the blast radius but didn't stop recursion — the diff still flagged a change on the first re-entry, so it recursed at least twice and the downstream double-fired.
- Tried: moving the recompute to a before-update context so no DML was needed (the platform persists `Trigger.new` edits as part of the original save). This was the *right* fix for *this* field — but it doesn't generalize to cross-object roll-ups that genuinely need after-context DML.
- Tried (the general fix): a **static recursion guard** in the handler — a `static Set<Id> processedIds` (or a static `Boolean` per context) checked-and-set at the top of the DML-issuing method, so a re-entrant call sees the Ids already processed and returns immediately.

## Resolution

**Any handler that issues DML on its own object will re-fire itself — a `static` recursion guard is mandatory, and "set the field in before-context" is the cheaper fix when the work is same-record.** Two layered rules:

1. **Same-record field changes belong in before-context, with no DML.** If the recompute only touches the saving record, do it in a before-update handler — the platform saves your `Trigger.new` edits as part of the original transaction, so there's no `update`, hence no recursion. This dissolves the problem instead of guarding it.
2. **When after-context DML is genuinely needed** (cross-object roll-up, related-record write), add a **static** guard: `static Set<Id> processed = new Set<Id>();` checked-and-set per record before the DML. Static survives re-entry within the transaction; an instance field does not.
3. **One trigger per object, logic in a handler.** Two triggers on one object multiply every recursion path and make the guard impossible to reason about. Consolidate to a single logic-less trigger that dispatches to one handler (house opinion #2).
4. **Account for declarative re-entry too.** A record-triggered Flow that updates the same object re-enters your Apex trigger. The guard protects against *all* re-entry sources, which is exactly why it's mandatory even when "my Apex only updates once."

The trap: the recursion is invisible until another automation (a second trigger, a Flow) shares the object, and an *instance* flag looks like a guard but resets every invocation.

**Action for the next engineer:** on `Maximum trigger depth exceeded` (or duplicated downstream side effects from a save), check first whether the handler DMLs its own object; if it does, confirm the recursion guard is `static`, not an instance field, and ask whether the work could move to before-context and avoid the DML entirely. Audit the object for a second trigger or a record-triggered Flow that re-enters.

Cross-reference: canonical guidance in [`../knowledge/trigger-handler-framework.md`](../knowledge/trigger-handler-framework.md) and the **Trigger Logic** decision tree in [`../knowledge/apex-decision-trees.md`](../knowledge/apex-decision-trees.md); rules [`../best-practices/apex-recursion-control-on-handlers.md`](../best-practices/apex-recursion-control-on-handlers.md), [`../best-practices/apex-one-trigger-per-object-handler.md`](../best-practices/apex-one-trigger-per-object-handler.md), and [`../best-practices/flow-before-save-for-same-record-field-updates.md`](../best-practices/flow-before-save-for-same-record-field-updates.md). House opinions #2–#4 and #12.
