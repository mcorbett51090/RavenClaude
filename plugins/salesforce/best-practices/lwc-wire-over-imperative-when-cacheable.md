# Prefer @wire to a cacheable method over imperative Apex for reads

**Status:** Pattern — strong default for read paths; use imperative Apex only for user-triggered actions or writes.

**Domain:** Lightning Web Components / data access

**Applies to:** `salesforce`

---

## Why this exists

`@wire` to a `@AuraEnabled(cacheable=true)` Apex method (or to a UI-API adapter like `getRecord`) is **reactive and cached**. The framework re-invokes the wire automatically when a reactive parameter changes, and it serves results from the Lightning Data Service client cache when the same query has already run — so a second component asking for the same record costs zero server round-trips. Imperative Apex (`import method; method({...})`) is **none of that**: no cache, no reactivity, you own the call lifecycle, and two components calling the same imperative method hit the server twice. Reaching for imperative by default throws away the platform's free caching and reactivity, and `cacheable=true` is *required* for a method to be wirable at all — so the choice of wire-vs-imperative is also a choice about whether the method may mutate data.

## How to apply

Default to `@wire` for reads; switch to imperative only when the call is triggered by a user gesture, must run exactly once on demand, or writes data.

```js
// GOOD — reactive, cached read. Re-runs when recordId changes; shared cache.
import { LightningElement, api, wire } from "lwc";
import getContacts from "@salesforce/apex/ContactController.getContacts";

export default class ContactList extends LightningElement {
  @api recordId;
  // recordId is reactive: the wire re-invokes whenever it changes
  @wire(getContacts, { accountId: "$recordId" }) contacts;
}
```

```js
// Imperative — correct only because this is a user-triggered WRITE on click.
import saveRating from "@salesforce/apex/ContactController.saveRating";
async handleSave() {
  try {
    await saveRating({ contactId: this.recordId, rating: this.rating });
  } catch (e) {
    this.error = e; // surface, never swallow
  }
}
```

**Do:**

- Use `@wire` for every read that can be cacheable; pass reactive params with the `"$prop"` syntax.
- Keep the wired Apex method `@AuraEnabled(cacheable=true)`, `with sharing`, and FLS-enforced.

**Don't:**

- Call imperative Apex on `connectedCallback` just to fetch initial data — that is a wire in disguise, minus the cache.
- Mark a method `cacheable=true` if it performs DML — `cacheable` methods must not mutate; the platform assumes purity.

## Edge cases / when the rule does NOT apply

Imperative is the **right** tool when: the call writes data (DML cannot be `cacheable`), it must run on a precise user action (button click, form submit), it needs imperative error/loading control, or it must run again with the *same* parameters (a wire won't re-fire if its inputs are unchanged — call `refreshApex` on the wired provisioned value, or use imperative). Pagination and infinite-scroll often go imperative for that reason. Prefer UI-API adapters (`getRecord`, `getRelatedListRecords`) over even a cacheable Apex method when they cover the need — see [`lwc-lds-before-apex.md`](./lwc-lds-before-apex.md).

## See also

- [`lwc-lds-before-apex.md`](./lwc-lds-before-apex.md) — prefer LDS/UI-API adapters before any Apex
- [`../skills/lwc-component-scaffold/SKILL.md`](../skills/lwc-component-scaffold/SKILL.md) — "prefer @wire … reach for imperative only for user-triggered actions"
- [`../knowledge/flow-lwc-decision-trees.md`](../knowledge/flow-lwc-decision-trees.md) — the "LWC data access" decision tree
- [`enforce-sharing-and-crud-fls.md`](./enforce-sharing-and-crud-fls.md) — the controller's sharing + FLS contract

## Provenance

Codifies the data-wiring step of [`../skills/lwc-component-scaffold/SKILL.md`](../skills/lwc-component-scaffold/SKILL.md) ("Prefer `@wire` to a cacheable Apex method or to `getRecord`/UI API over imperative calls; reach for imperative Apex only for user-triggered actions"), grounded in Salesforce LWC `@wire` / cacheable-Apex documentation.

---

_Last reviewed: 2026-05-30 by `claude`_
