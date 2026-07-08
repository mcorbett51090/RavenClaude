# Template — Batch Apex Class (bulk-safe Database.Batchable)

For large-data-volume processing. See `knowledge/apex-async-patterns.md` for when Batch beats Queueable/Future/Schedulable.

```apex
public with sharing class AccountArchiveBatch
    implements Database.Batchable<SObject>, Database.Stateful {

    private Integer recordsProcessed = 0;

    // start: return a selective, LDV-safe QueryLocator (filter on indexed field)
    public Database.QueryLocator start(Database.BatchableContext bc) {
        return Database.getQueryLocator([
            SELECT Id, Name, LastActivityDate
            FROM Account
            WHERE LastActivityDate < LAST_N_YEARS:3
            WITH USER_MODE              // v67.0+ (pre-v67: WITH SECURITY_ENFORCED, removed at v67.0+)
        ]);
    }

    // execute: operates on a scope (default 200, up to 2000). Bulk-safe.
    public void execute(Database.BatchableContext bc, List<Account> scope) {
        List<Account> toUpdate = new List<Account>();
        for (Account a : scope) {
            a.Archived__c = true;
            toUpdate.add(a);
        }
        if (!toUpdate.isEmpty()) {
            update toUpdate;            // one DML on the collection
            recordsProcessed += toUpdate.size();
        }
    }

    // finish: chain the next job here if needed
    public void finish(Database.BatchableContext bc) {
        // e.g. System.enqueueJob(new NextQueueable());
        // log recordsProcessed; send completion notice
    }
}
```

Run: `Database.executeBatch(new AccountArchiveBatch(), 200);`

Notes: `Database.Stateful` only when you must carry state across scopes; keep scope size within CPU/heap budget; selective `start` query; one DML per `execute`; verify async-Apex limits `[verify-at-build]`.
