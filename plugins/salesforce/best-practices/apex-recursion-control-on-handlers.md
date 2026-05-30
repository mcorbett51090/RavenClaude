# Guard every trigger handler against recursion — a static guard is mandatory

**Status:** Absolute rule — a handler that issues DML on its own object with no guard is a defect.

**Domain:** Apex / trigger architecture

**Applies to:** `salesforce`

---

## Why this exists

When a trigger handler updates the same object that fired it, the update **re-fires the trigger**, which runs the handler again, which updates again — an infinite loop the platform stops only by throwing `System.LimitException: Maximum trigger depth exceeded` (16 levels) or `Too many SOQL queries` as the re-entrant passes accumulate queries and DML. Even when it doesn't hit the ceiling, uncontrolled recursion does redundant work, double-counts roll-ups, and makes behavior impossible to reason about. House opinion #4 makes recursion control **mandatory on every handler** — it is not optional hardening, it is part of the handler's correctness contract.

## How to apply

Add a static guard in the handler. A `Boolean` is the simplest form; a `Set<Id>` of already-processed records is the correct form when a legitimate second pass on *different* records must still proceed.

```apex
public with sharing class AccountTriggerHandler {

    // Set<Id> guard — suppresses re-entry on records WE already processed,
    // while still allowing a first pass on records we haven't seen.
    private static Set<Id> processedIds = new Set<Id>();

    public void onAfterUpdate(List<Account> records) {
        List<Account> toProcess = new List<Account>();
        for (Account a : records) {
            if (!processedIds.contains(a.Id)) {
                toProcess.add(a);
                processedIds.add(a.Id);     // mark before the DML that re-fires us
            }
        }
        if (toProcess.isEmpty()) return;    // pure re-entry — nothing new, stop

        // ...bulk-safe roll-up that issues an update on Account, re-firing this trigger...
        // on re-entry, processedIds already holds these — the loop adds nothing — we return.
    }
}
```

**Do:**
- Put a **static** guard in the handler — its lifetime is the transaction, exactly the recursion scope.
- Prefer a **`Set<Id>`** guard when a roll-up may legitimately re-touch *different* records in the same transaction.
- Mark a record processed **before** the DML that will re-fire the trigger, so the re-entrant pass sees it.
- Reset the guard only if a genuine, intended second full pass is required (and document why).

**Don't:**
- Omit the guard on any handler whose logic issues DML on its own object — it will recurse.
- Use a blunt `Boolean` when partial re-processing of new records in the same transaction is valid — it wrongly suppresses them.
- Put the guard on an **instance** field — a new handler instance per trigger invocation resets it, defeating the purpose.

## Edge cases / when the rule does NOT apply

A handler whose contexts never DML their own object (a `before insert` that only sets fields in-memory on `Trigger.new`, which the platform saves *without* a second DML) has no recursion path and a guard is harmless but inert. Cross-object updates can still recurse indirectly if object A's trigger updates B and B's trigger updates A — each handler needs its own guard. The `Boolean` form is acceptable when the handler's entire job is genuinely once-per-transaction; the `Set<Id>` form is the safer default when in doubt. A metadata-driven trigger framework may centralize the guard, but the guard must still exist.

## See also

- [`./apex-one-trigger-per-object-handler.md`](./apex-one-trigger-per-object-handler.md) — the one-trigger / logic-less-trigger structure this completes
- [`./apex-soql-in-loops-is-a-defect.md`](./apex-soql-in-loops-is-a-defect.md) — unguarded recursion is a hidden cause of surprise query counts
- [`../knowledge/trigger-handler-framework.md`](../knowledge/trigger-handler-framework.md) — the handler pattern and structuring decision tree
- [`../knowledge/apex-decision-trees.md`](../knowledge/apex-decision-trees.md) — the trigger-logic-placement decision tree
- [`../templates/trigger-handler.md`](../templates/trigger-handler.md) — the handler skeleton with the guard
- [`../agents/apex-engineer.md`](../agents/apex-engineer.md) — owns recursion control

## Provenance

Codifies house opinion #4 from [`../CLAUDE.md`](../CLAUDE.md), the fourth `apex-engineer` discipline. Grounded in [`../knowledge/trigger-handler-framework.md`](../knowledge/trigger-handler-framework.md), sourced from the SalesforceBen trigger-handler-framework guide. The 16-level maximum trigger depth and trigger-re-fire-on-DML behavior are documented Salesforce platform behaviors.

---

_Last reviewed: 2026-05-30 by `claude`_
