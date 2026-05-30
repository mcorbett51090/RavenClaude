# An LWC's Apex controller is cacheable for reads, FLS-aware, with sharing, and bulk-safe

**Status:** Absolute rule for the controller's security posture; pattern for the cacheable/bulk shape.

**Domain:** Lightning Web Components / Apex controller

**Applies to:** `salesforce`

---

## Why this exists

The Apex controller behind an LWC runs in **user context from the browser** — it is a public entry point a user (or a crafted request) can call directly. If it isn't `with sharing`, it leaks records the running user can't see; if it doesn't enforce CRUD/FLS, it returns or writes fields the user has no permission to; if it isn't bulk-safe, a list-shaped UI blows governor limits on the first large account. And the read methods must be `@AuraEnabled(cacheable=true)` or `@wire` can't bind to them at all — which is also the contract that makes them cache and reactive. This is house opinions #1, #6, and #7 applied at the LWC boundary: the controller is the security and limits frontier of the component.

## How to apply

```apex
public with sharing class ContactController {        // #6: with sharing by default

    @AuraEnabled(cacheable=true)                      // wirable + cached; reads only
    public static List<Contact> getContacts(Id accountId) {
        return [
            SELECT Id, Name, Email
            FROM Contact
            WHERE AccountId = :accountId               // #8: bound variable, no concat
            WITH SECURITY_ENFORCED                      // #7: CRUD/FLS enforced
            ORDER BY Name
            LIMIT 200
        ];
    }

    @AuraEnabled                                       // NOT cacheable — it writes
    public static void rate(List<Contact> toUpdate) {  // #1/#9: accepts a collection
        Security.stripInaccessible(AccessType.UPDATABLE, toUpdate);
        update toUpdate;                               // one bulk DML, no loop
    }
}
```

**Do:**

- Mark read methods `@AuraEnabled(cacheable=true)`; keep them side-effect-free.
- Enforce FLS with `WITH SECURITY_ENFORCED` (queries) or `Security.stripInaccessible` (DML payloads).
- Accept and return **collections** where the UI is list-shaped; one DML/SOQL, never in a loop.
- Throw `AuraHandledException` with a user-safe message so the component can surface it.

**Don't:**

- Put `cacheable=true` on a method that does DML — `cacheable` methods must be pure; the platform caches the result.
- Use `without sharing` to "make the component work" — that is a security hole, not a fix. Justify any `without sharing` in writing and escalate to `ravenclaude-core/security-reviewer`.
- Loop a SOQL/DML per row to serve a list UI.

## Edge cases / when the rule does NOT apply

A method that *must* read data the running user can't see (a legitimate elevated-context need) may use `without sharing` — but that is a security verdict owned by `ravenclaude-core/security-reviewer`, documented, never a default. Methods that only ever return org-wide metadata (not record data) still benefit from `cacheable=true` for the cache, even though sharing is moot. If the read genuinely can't be cacheable (it has real per-call side effects a wire shouldn't trigger), it isn't a read — model it as an imperative action (see [`lwc-wire-over-imperative-when-cacheable.md`](./lwc-wire-over-imperative-when-cacheable.md)).

## See also

- [`enforce-sharing-and-crud-fls.md`](./enforce-sharing-and-crud-fls.md) — the org-wide statement of #6–#7
- [`bulkify-every-soql-and-dml.md`](./bulkify-every-soql-and-dml.md) — the controller's bulk obligation
- [`lwc-wire-over-imperative-when-cacheable.md`](./lwc-wire-over-imperative-when-cacheable.md) — cacheable enables `@wire`
- [`../skills/lwc-component-scaffold/SKILL.md`](../skills/lwc-component-scaffold/SKILL.md) — the FLS-aware-controller step this codifies

## Provenance

Codifies the "FLS-aware controller" + "bulk-safe controller" steps of [`../skills/lwc-component-scaffold/SKILL.md`](../skills/lwc-component-scaffold/SKILL.md) and house opinions #1/#6/#7/#8 from [`../CLAUDE.md`](../CLAUDE.md), grounded in Salesforce `@AuraEnabled(cacheable=true)`, `WITH SECURITY_ENFORCED`, and `Security.stripInaccessible` documentation.

---

_Last reviewed: 2026-05-30 by `claude`_
