# One trigger per object — the trigger dispatches, the handler thinks

**Status:** Absolute rule — a second trigger on the same object, or logic in a trigger body, is a defect.

**Domain:** Apex / trigger architecture

**Applies to:** `salesforce`

---

## Why this exists

Salesforce gives **no guaranteed execution order** when an SObject has more than one trigger for the same event. Two `before update` triggers on `Account` may run in either order across deploys, orgs, or releases — so behavior that depends on their sequence is non-deterministic and undebuggable. Logic in the trigger body compounds the problem: triggers can't be unit-tested in isolation, can't be reused, and can't carry recursion control cleanly. House opinions #2, #3, and #4 collapse this into one shape — **one logic-less trigger per object delegating to a handler class with mandatory recursion control**.

## How to apply

The trigger is a dispatch shell that routes by `Trigger.operationType`; all logic lives in the handler, which operates on collections and guards against recursion.

```apex
// DO — the trigger only dispatches; no queries, no DML, no business if/else
trigger AccountTrigger on Account (before insert, before update,
                                   after insert, after update) {
    new AccountTriggerHandler().run();   // one entry point, all contexts
}

public with sharing class AccountTriggerHandler {
    private static Boolean hasRun = false;          // recursion guard

    public void run() {
        if (hasRun) return;                          // re-entry from our own DML stops here
        hasRun = true;
        switch on Trigger.operationType {
            when BEFORE_UPDATE { onBeforeUpdate(Trigger.new, Trigger.oldMap); }
            when AFTER_INSERT  { onAfterInsert(Trigger.newMap); }
            // ...other contexts
        }
    }

    private void onBeforeUpdate(List<Account> records, Map<Id, Account> oldMap) {
        // bulk-safe logic on the collection — never one record at a time
    }
}
```

**Do:**
- Create exactly **one** trigger per SObject, covering every context it needs.
- Keep the trigger body to a single handler dispatch call — no `if`, no SOQL, no DML.
- Put a **static** recursion guard (`Boolean` or `Set<Id>` of processed IDs) in the handler.
- Operate on `Trigger.new` / `Trigger.newMap` collections so the handler is bulk-safe by construction.

**Don't:**
- Add a second trigger to an object that already has one — extend the existing handler instead.
- Write business logic, queries, or DML inside the trigger body.
- Omit recursion control — a handler that issues DML on its own object will re-fire itself.

## Edge cases / when the rule does NOT apply

A `Set<Id>`-based guard is preferable to a blunt `Boolean` when a *legitimate* second pass on **different** records must proceed (e.g. a roll-up that re-touches parents) — the boolean would wrongly suppress it. Trigger frameworks that centralize dispatch (a metadata-driven `TriggerHandler` base class) are an acceptable elaboration of this rule, not an exception to it: there is still one trigger per object. The "logic-less" constraint is absolute; the *shape* of the handler (virtual base + subclass, interface-driven, MDT-registered) is a free choice.

## See also

- [`../knowledge/trigger-handler-framework.md`](../knowledge/trigger-handler-framework.md) — the pattern and the structuring decision tree
- [`../knowledge/apex-decision-trees.md`](../knowledge/apex-decision-trees.md) — trigger-logic-placement decision tree
- [`../templates/trigger-handler.md`](../templates/trigger-handler.md) — the handler skeleton
- [`./bulkify-every-soql-and-dml.md`](./bulkify-every-soql-and-dml.md) — the bulk discipline the handler must follow
- [`../agents/apex-engineer.md`](../agents/apex-engineer.md) — owns this structure

## Provenance

Codifies house opinions #2, #3, and #4 from [`../CLAUDE.md`](../CLAUDE.md). Grounded in [`../knowledge/trigger-handler-framework.md`](../knowledge/trigger-handler-framework.md), sourced from the SalesforceBen trigger-handler-framework guide. The unguaranteed multi-trigger execution order is a documented Salesforce platform behavior.

---

_Last reviewed: 2026-05-30 by `claude`_
