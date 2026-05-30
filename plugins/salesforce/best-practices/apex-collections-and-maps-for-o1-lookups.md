# Use `Map` for O(1) lookups — never a nested loop to correlate records

**Status:** Pattern — strong default; a nested loop where a map keyed lookup would do is a CPU-time and readability defect.

**Domain:** Apex / collections & bulkification

**Applies to:** `salesforce`

---

## Why this exists

Once SOQL and DML are hoisted out of loops (the bulkify rule), the next bulk-safety failure is **CPU time**, not query count. Correlating two collections with a nested loop is O(n×m): 200 parents against 5,000 children is a million iterations, and at production scale it trips `System.LimitException: Apex CPU time limit exceeded` (10,000 ms synchronous). A `Map<Id, …>` keyed on the join field turns each correlation into an O(1) lookup, collapsing O(n×m) to O(n+m). Maps are also how you build the query-once / lookup-in-loop shape the bulkify and SOQL-in-loops rules depend on — the map *is* the mechanism that lets the in-loop query disappear. This is foundational bulkification craft, adjacent to house opinion #1.

## How to apply

Query the related records once, index them into a `Map` (or `Map<Id, List<…>>` for one-to-many) keyed on the correlation field, then look them up by key inside the loop.

```apex
// DON'T — nested loop, O(parents × contacts), CPU-bound at scale
for (Account a : accounts) {
    for (Contact c : allContacts) {                 // re-scans every contact per account
        if (c.AccountId == a.Id) { a.Contact_Count__c++; }
    }
}

// DO — one map keyed by the join field; O(1) lookup per parent
Map<Id, List<Contact>> contactsByAccount = new Map<Id, List<Contact>>();
for (Contact c : [SELECT Id, AccountId FROM Contact
                  WHERE AccountId IN :accountIds]) {     // one query, bound collection
    if (!contactsByAccount.containsKey(c.AccountId)) {
        contactsByAccount.put(c.AccountId, new List<Contact>());
    }
    contactsByAccount.get(c.AccountId).add(c);
}
for (Account a : accounts) {
    List<Contact> kids = contactsByAccount.get(a.Id);    // O(1)
    a.Contact_Count__c = (kids == null) ? 0 : kids.size();
}
```

**Do:**
- Build a `Map<Id, SObject>` (or `Map<Id, List<SObject>>` for one-to-many) keyed on the correlation field.
- Use the **`Map(List<SObject>)` constructor** to index query results by Id in one line: `new Map<Id, Account>([SELECT ...])`.
- Use a `Set` for membership/dedup checks instead of scanning a `List` with `contains` in a loop.
- Null-check `map.get(key)` — a missing key returns `null`, not an empty collection.

**Don't:**
- Nest two loops to correlate collections when a map lookup is O(1).
- Call `List.contains()` inside a loop on a large list — that's an O(n) scan per iteration; use a `Set`.
- Forget `containsKey` before appending to a `Map<Id, List<…>>` — you'll NPE on the first child of each key.

## Edge cases / when the rule does NOT apply

For tiny, bounded collections (a handful of records, never growing with data volume) a nested loop is harmless and a map adds ceremony — but the moment either side scales with record count, the map is mandatory. A composite correlation key (two fields) can be modeled as `Map<String, …>` with a concatenated key, or a nested `Map<Id, Map<Id, …>>`. `Map` key equality for sObjects and user-defined types depends on `equals`/`hashCode` semantics — keying on the **Id** (or a primitive) is the safe, predictable choice; keying on a whole sObject is not. CPU-time limits, like all governor limits, double in async but the algorithmic fix is identical.

## See also

- [`./bulkify-every-soql-and-dml.md`](./bulkify-every-soql-and-dml.md) — the rule whose query-once shape this map enables
- [`./apex-soql-in-loops-is-a-defect.md`](./apex-soql-in-loops-is-a-defect.md) — the map is what replaces the in-loop query
- [`../knowledge/governor-limits-and-bulkification.md`](../knowledge/governor-limits-and-bulkification.md) — the CPU-time limit and the collect/query/map/DML pattern
- [`../knowledge/apex-decision-trees.md`](../knowledge/apex-decision-trees.md) — the bulk-safety decision tree
- [`../agents/apex-engineer.md`](../agents/apex-engineer.md) — owns bulkification craft

## Provenance

Grounded in [`../knowledge/governor-limits-and-bulkification.md`](../knowledge/governor-limits-and-bulkification.md) (step 3: "build a `Map<Id, SObject>` for O(1) lookup"), itself sourced from Salesforce Apex governor-limit documentation. Reflects house opinion #1 and the `apex-engineer` bulkification discipline in [`../CLAUDE.md`](../CLAUDE.md). The `Map(List<SObject>)` constructor and the 10,000 ms synchronous CPU-time limit are documented Apex platform behaviors; the exact limit is tagged `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
