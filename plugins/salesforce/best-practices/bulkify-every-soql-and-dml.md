# Bulkify every SOQL and DML — no query or DML inside a loop

**Status:** Absolute rule — a violation is a production bug, not a style preference.

**Domain:** Apex / governor-limit safety

**Applies to:** `salesforce`

---

## Why this exists

Salesforce runs Apex in a multi-tenant context, so every transaction is capped by **governor limits**. The single highest-frequency Salesforce failure mode is code that works on one record in a sandbox and throws `System.LimitException: Too many SOQL queries: 101` the moment a data load, a Bulk API job, or a 200-record trigger batch arrives. A SOQL query or DML statement inside a loop multiplies one operation by the batch size — 200 records means 200 queries against a 100-query synchronous ceiling. This is house opinion #1 and the reason `apex-engineer` exists.

## How to apply

Collect keys in one pass, query once with `WHERE Id IN :ids`, build a map for O(1) lookup, then issue one DML on a collection.

```apex
// DON'T — query + DML inside the loop (101 SOQL at 101 records)
for (Account a : Trigger.new) {
    List<Contact> cs = [SELECT Id FROM Contact WHERE AccountId = :a.Id];
    a.Number_Of_Contacts__c = cs.size();
    update a;                       // 200 DML statements too
}

// DO — one aggregate query, one DML on the whole list
Map<Id, Integer> counts = new Map<Id, Integer>();
for (AggregateResult ar : [
        SELECT AccountId, COUNT(Id) c FROM Contact
        WHERE AccountId IN :Trigger.newMap.keySet()
        GROUP BY AccountId]) {
    counts.put((Id) ar.get('AccountId'), (Integer) ar.get('c'));
}
for (Account a : Trigger.new) {
    a.Number_Of_Contacts__c = counts.containsKey(a.Id) ? counts.get(a.Id) : 0;
}
// no update here — let the before-trigger save the change, or one update outside any loop
```

**Do:**
- Hoist every query and every DML statement out of every loop, including nested ones.
- Bind collections into the `WHERE` clause (`IN :ids`) — never query per record.
- Accumulate records into a `List`, then `insert`/`update`/`delete` the list once.

**Don't:**
- Put a SOQL, SOSL, or DML statement inside a `for`/`while` body.
- Assume "it'll only ever be one record" — the Bulk API and data loaders defeat that assumption.

## Edge cases / when the rule does NOT apply

The rule admits no exception for the *loop placement* of SOQL/DML — that is always wrong. What legitimately varies is the *limit budget*: asynchronous contexts get 200 SOQL queries instead of 100, but the bulkification pattern is identical and you should never lean on the async headroom to excuse an unbulkified loop. A genuinely unavoidable per-record callout belongs in `@future`/Queueable, not a synchronous loop. The same per-transaction limits are shared by Flow — a Flow looping over a large collection hits them too.

## See also

- [`../knowledge/governor-limits-and-bulkification.md`](../knowledge/governor-limits-and-bulkification.md) — the limits table + the bulk-safe decision tree
- [`../knowledge/trigger-handler-framework.md`](../knowledge/trigger-handler-framework.md) — where the bulk-safe logic lives
- [`../templates/apex-test-class.md`](../templates/apex-test-class.md) — the 200-record bulk test that proves the safety
- [`../agents/apex-engineer.md`](../agents/apex-engineer.md) — the agent that owns this discipline

## Provenance

Codifies house opinion #1 from [`../CLAUDE.md`](../CLAUDE.md) and the `apex-engineer` prime directive. Grounded in [`../knowledge/governor-limits-and-bulkification.md`](../knowledge/governor-limits-and-bulkification.md), itself sourced from Salesforce's Apex governor-limit and mixed-DML documentation.

---

_Last reviewed: 2026-05-30 by `claude`_
