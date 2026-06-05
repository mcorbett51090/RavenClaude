# Enforce object-level CRUD before checking field-level security — the permission layers are ordered

**Status:** Primary diagnostic
**Domain:** Apex security
**Applies to:** `salesforce`

---

## Why this exists

Salesforce security is layered: Object-level CRUD (Create/Read/Update/Delete) is evaluated **before** field-level security (FLS). An Apex class that calls `Security.stripInaccessible()` or `WITH SECURITY_ENFORCED` to strip inaccessible fields will still silently return records the user is not allowed to see if the object CRUD check is omitted. The reverse is also a common bug: code that checks `Schema.sObjectType.Account.isAccessible()` before querying (correct) but then writes to a field without checking `Schema.sObjectType.Account.fields.Annual_Revenue__c.isUpdateable()` (incomplete). The ordering matters: fail fast at the CRUD level so you never execute a FLS check on an object the user cannot see at all.

## How to apply

Correct layered security check pattern:

```apex
public static List<Account> getAccountsForUser() {
    // 1. Object-level CRUD check FIRST
    if (!Schema.sObjectType.Account.isAccessible()) {
        throw new AuraHandledException('You do not have access to Account records.');
    }

    // 2. Field-level security via WITH SECURITY_ENFORCED (throws QueryException if inaccessible)
    return [
        SELECT Id, Name, Annual_Revenue__c
        FROM Account
        WITH SECURITY_ENFORCED
        LIMIT 200
    ];
}

public static void updateRevenue(Account acc, Decimal newRevenue) {
    // 1. Object update permission
    if (!Schema.sObjectType.Account.isUpdateable()) {
        throw new AuraHandledException('You cannot update Account records.');
    }
    // 2. Field update permission
    if (!Schema.sObjectType.Account.fields.Annual_Revenue__c.isUpdateable()) {
        throw new AuraHandledException('You cannot update Annual Revenue.');
    }
    acc.Annual_Revenue__c = newRevenue;
    update acc;
}
```

Alternatively, use `Security.stripInaccessible()` with `AccessType.READABLE` / `UPDATABLE` — it handles both object and field levels in one call:

```apex
SObjectAccessDecision decision = Security.stripInaccessible(
    AccessType.READABLE,
    [SELECT Id, Name, Annual_Revenue__c FROM Account]
);
List<Account> accounts = (List<Account>) decision.getRecords();
```

**Do:**
- Check object-level permission before executing any DML or SOQL.
- Prefer `Security.stripInaccessible()` or `WITH SECURITY_ENFORCED` over manual field-by-field FLS loops for new code.
- Route any FLS-as-a-security-control design through `ravenclaude-core/security-reviewer` per the cross-plugin seam.

**Don't:**
- Check field-level security without first confirming object-level access — the object check is the prerequisite.
- Use `WITH SECURITY_ENFORCED` on a write path — it only applies to SELECT; use `Security.stripInaccessible(AccessType.UPDATABLE, ...)` for write operations.
- Skip security checks in `@future` or `Queueable` methods — they run in the user context by default (unless `without sharing` is declared); the CRUD/FLS obligation applies.

## Edge cases / when the rule does NOT apply

System-context Apex methods (e.g., integration handlers that run as a service account via `without sharing`) operate with elevated permission and are exempt from per-user CRUD/FLS checks — but the exemption must be documented and reviewed as a security decision by `ravenclaude-core/security-reviewer`.

## See also

- [`../agents/apex-engineer.md`](../agents/apex-engineer.md) — owns Apex security enforcement
- [`./enforce-sharing-and-crud-fls.md`](./enforce-sharing-and-crud-fls.md) — the broader sharing + CRUD/FLS rule; this rule adds the ordering discipline

## Provenance

Codifies house opinion #7 ("enforce CRUD/FLS for user-context access") with the ordering discipline from the Salesforce platform security model; Salesforce Apex security best practices guide.

---

_Last reviewed: 2026-06-05 by `claude`_
