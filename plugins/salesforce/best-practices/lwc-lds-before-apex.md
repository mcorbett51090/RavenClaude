# Reach for Lightning Data Service / UI API before writing any Apex

**Status:** Pattern — strong default; write Apex only when LDS cannot express the need.

**Domain:** Lightning Web Components / data access

**Applies to:** `salesforce`

---

## Why this exists

Lightning Data Service (LDS) — the `lightning-record-*-form` components and the UI-API wire adapters (`getRecord`, `getRecords`, `getRelatedListRecords`, `createRecord`, `updateRecord`, `deleteRecord`) — reads and writes single records **without any Apex**. It enforces CRUD and FLS automatically, shares one client-side cache across every component on the page (so a record edited in one component refreshes everywhere), and requires **zero server-side test coverage** because you wrote no Apex. Every Apex controller you *don't* write is a class you don't have to make `with sharing`, FLS-enforce, bulk-test, and maintain. The anti-pattern is reflexively scaffolding an `@AuraEnabled` controller for what `getRecord` + `lightning-record-edit-form` already do securely and for free.

## How to apply

Walk the escalation ladder in order; stop at the first rung that satisfies the requirement.

```
1. Single-record display/edit on a record page
     -> lightning-record-form / -view-form / -edit-form   (no JS, no Apex)
2. Read specific fields reactively
     -> @wire(getRecord, { recordId, fields })             (UI API, no Apex)
3. Read a related list
     -> @wire(getRelatedListRecords, {...})                (UI API, no Apex)
4. Create / update / delete one record imperatively
     -> createRecord / updateRecord / deleteRecord (lightning/uiRecordApi)
5. Multi-object joins, aggregates, complex filters, bulk DML
     -> @AuraEnabled Apex (cacheable for reads) — now you need Apex
```

```html
<!-- GOOD — secure create/edit with no controller, no test class -->
<lightning-record-edit-form
  object-api-name="Contact"
  onsuccess={handleSaved}
>
  <lightning-input-field field-name="FirstName"></lightning-input-field>
  <lightning-input-field field-name="LastName"></lightning-input-field>
  <lightning-button type="submit" label="Save"></lightning-button>
</lightning-record-edit-form>
```

**Do:**

- Use `lightning-record-*-form` for single-record CRUD on a record page.
- Use `getRecord`/`getRelatedListRecords` wires for reads; import field references from `@salesforce/schema/...` so deletes break the build, not runtime.

**Don't:**

- Write an Apex controller to fetch one record by Id — `getRecord` does it with FLS enforced and cached.
- Re-implement single-record save in Apex when `updateRecord` already enforces FLS and refreshes the shared cache.

## Edge cases / when the rule does NOT apply

LDS / UI API is **single-record-oriented** and does not do: cross-object joins, SOQL aggregates, `WHERE` filters beyond a related list, SOSL, or bulk DML across many records. Those need Apex — at which point all the controller rules apply (`with sharing`, `WITH SECURITY_ENFORCED`, bulk-safe, tested). The `lightning-record-form` "view/edit" modes also can't do custom layouts with conditional sections; drop to `lightning-record-edit-form` with explicit `lightning-input-field`s, still no Apex. Large related lists past the UI-API page size also justify an Apex pagination method.

## See also

- [`lwc-wire-over-imperative-when-cacheable.md`](./lwc-wire-over-imperative-when-cacheable.md) — when Apex *is* needed, wire it cacheably
- [`enforce-sharing-and-crud-fls.md`](./enforce-sharing-and-crud-fls.md) — the FLS contract LDS gives you for free
- [`../knowledge/flow-lwc-decision-trees.md`](../knowledge/flow-lwc-decision-trees.md) — the "LWC data access: wire vs imperative vs LDS" tree
- [`../skills/lwc-component-scaffold/SKILL.md`](../skills/lwc-component-scaffold/SKILL.md) — "Prefer `@wire` to … `getRecord`/UI API over imperative calls"

## Provenance

Codifies the LDS-first guidance in [`../skills/lwc-component-scaffold/SKILL.md`](../skills/lwc-component-scaffold/SKILL.md) and house opinions #6–#7 (sharing + FLS) by removing the Apex surface entirely where LDS suffices, grounded in Salesforce Lightning Data Service / UI-API wire-adapter documentation.

---

_Last reviewed: 2026-05-30 by `claude`_
