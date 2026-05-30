# Default to least access — `with sharing` and enforce CRUD/FLS in user-context code

**Status:** Absolute rule — security defaults are not preferences; the verdict escalates to core.

**Domain:** Identity / record & field security

**Applies to:** `salesforce`

---

## Why this exists

Salesforce record access is layered: org-wide defaults (OWD) set the floor, the role hierarchy and sharing rules open it up. But OWD and sharing govern *records* — they say nothing about whether a given user may read a *field*. Apex that runs `without sharing`, or that queries a field the running user can't see, silently bypasses the security model the admin configured. The result is a field-level data leak that no sharing rule will catch. House opinions #6 and #7 make least-access the default; the actual security verdict is owned by `ravenclaude-core/security-reviewer`, not this plugin.

## How to apply

Start OWD at the most restrictive default that still works (usually Private) and open up deliberately. In code, declare `with sharing` and enforce CRUD/FLS for any user-context access.

```apex
// DO — class respects sharing; SOQL enforces field-level security
public with sharing class AccountService {
    public List<Account> getVisible(Set<Id> ids) {
        return [
            SELECT Id, Name, AnnualRevenue
            FROM Account
            WHERE Id IN :ids
            WITH SECURITY_ENFORCED          // strips/throws on fields the user can't read
        ];
    }

    // For DML in user context, strip inaccessible fields before writing
    public void save(List<Account> records) {
        SObjectAccessDecision d =
            Security.stripInaccessible(AccessType.UPDATABLE, records);
        update d.getRecords();
    }
}
```

**Do:**
- Make `with sharing` the default; **write a justification comment for every `without sharing`**.
- Enforce CRUD/FLS in user-context access — `WITH SECURITY_ENFORCED` in SOQL or `Security.stripInaccessible` on DML.
- Choose master-detail vs lookup deliberately — master-detail **inherits** the parent's sharing, lookup does not.
- Escalate the *verdict* ("is this design actually secure?") to `ravenclaude-core/security-reviewer`.

**Don't:**
- Use `without sharing` to "make the query work" without stating why.
- Assume OWD/sharing protects fields — it protects records; CRUD/FLS protects fields.

## Edge cases / when the rule does NOT apply

`without sharing` is legitimate for genuine system operations that must see all records (a roll-up batch, a system integration user's service class) — but the choice is *documented*, scoped as narrowly as possible, and never the default. Code running in a defined system context (some `@future`/Batch jobs) may intentionally run in system mode; that, too, is a written decision, not an accident. The CRUD/FLS enforcement is non-negotiable for any class that acts on behalf of a user.

## See also

- [`../knowledge/sharing-and-security-model.md`](../knowledge/sharing-and-security-model.md) — the OWD → hierarchy → sharing-rule layering and the access decision tree
- [`./bulkify-every-soql-and-dml.md`](./bulkify-every-soql-and-dml.md) — the queries that must also be FLS-enforced
- [`../agents/salesforce-platform-architect.md`](../agents/salesforce-platform-architect.md) — owns the sharing-model design
- [`../agents/apex-engineer.md`](../agents/apex-engineer.md) — owns CRUD/FLS enforcement in code

## Provenance

Codifies house opinions #6 and #7 from [`../CLAUDE.md`](../CLAUDE.md). Grounded in [`../knowledge/sharing-and-security-model.md`](../knowledge/sharing-and-security-model.md), sourced from the Salesforce sharing-model guide and the PMD Apex security rules (CRUD/FLS). The security *verdict* is escalated to `ravenclaude-core/security-reviewer` per the plugin constitution.

---

_Last reviewed: 2026-05-30 by `claude`_
