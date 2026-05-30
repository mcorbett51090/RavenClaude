# Template — Trigger Handler (one trigger per object + handler class)

One logic-less trigger that dispatches to a virtual handler class with recursion control (house opinions #2-#4). See `knowledge/trigger-handler-framework.md`.

## Trigger (dispatch shell only — no logic)

```apex
trigger AccountTrigger on Account (
    before insert, before update, before delete,
    after insert, after update, after delete, after undelete
) {
    new AccountTriggerHandler().run();
}
```

## Virtual base handler

```apex
public virtual class TriggerHandler {
    @TestVisible private static Set<Id> processedIds = new Set<Id>();

    public void run() {
        switch on Trigger.operationType {
            when BEFORE_INSERT { beforeInsert(Trigger.new); }
            when BEFORE_UPDATE { beforeUpdate(Trigger.new, Trigger.oldMap); }
            when AFTER_INSERT  { afterInsert(Trigger.new); }
            when AFTER_UPDATE  { afterUpdate(Trigger.new, Trigger.oldMap); }
            // ... remaining contexts
        }
    }

    // Override only what you need. Default no-ops keep subclasses lean.
    protected virtual void beforeInsert(List<SObject> newList) {}
    protected virtual void beforeUpdate(List<SObject> newList, Map<Id, SObject> oldMap) {}
    protected virtual void afterInsert(List<SObject> newList) {}
    protected virtual void afterUpdate(List<SObject> newList, Map<Id, SObject> oldMap) {}
}
```

## Concrete handler (bulk-safe, recursion-guarded)

```apex
public with sharing class AccountTriggerHandler extends TriggerHandler {
    protected override void afterUpdate(List<SObject> newList, Map<Id, SObject> oldMap) {
        // Recursion guard
        List<Account> toProcess = new List<Account>();
        for (Account a : (List<Account>) newList) {
            if (!processedIds.contains(a.Id)) {
                toProcess.add(a);
                processedIds.add(a.Id);
            }
        }
        if (toProcess.isEmpty()) return;

        // Bulk-safe: collect IDs, query once, DML once
        // ... build a Map keyed by Id, update a List in one DML
    }
}
```

Notes: `with sharing` by default; no SOQL/DML in loops; recursion guard is mandatory.
