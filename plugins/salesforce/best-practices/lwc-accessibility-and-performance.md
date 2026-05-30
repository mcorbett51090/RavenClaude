# Build accessible, render-cheap LWCs — base components, keyed lists, and deferred work

**Status:** Pattern — strong default; accessibility requirements are non-negotiable for any user-facing component.

**Domain:** Lightning Web Components / accessibility + performance

**Applies to:** `salesforce`

---

## Why this exists

Two classes of defect ship invisibly in hand-built LWCs. **Accessibility:** raw `<div onclick>` "buttons", missing labels, and color-only error signalling lock out keyboard and screen-reader users — and on the Salesforce platform that is a compliance gap, not a nicety. **Performance:** LWC re-renders a component whenever a tracked field or `@api` prop changes; doing real work in `renderedCallback`, iterating un-`key`ed lists, or fetching on every render multiplies that cost. The base Lightning components (`lightning-button`, `lightning-input`, `lightning-datatable`) are accessible *and* performance-tuned out of the box — re-implementing them in raw HTML throws away both. Most of this is free if you start from base components and respect the render lifecycle.

## How to apply

```html
<!-- ACCESSIBLE — base component carries roles, focus, keyboard handling, label -->
<lightning-button label="Approve" onclick={handleApprove}></lightning-button>
<lightning-input
  label="Amount"
  type="number"
  value={amount}
  onchange={handleChange}
></lightning-input>

<!-- Keyed iteration — key:* lets the engine diff instead of re-creating rows -->
<template for:each={rows} for:item="row">
  <c-row key={row.id} record={row}></c-row>
</template>
```

```js
// PERFORMANCE — renderedCallback fires on EVERY render; guard one-time work.
renderedCallback() {
  if (this._initialized) return;
  this._initialized = true;
  // one-time DOM measurement / third-party init only
}
```

**Do:**

- Build from base Lightning components; they ship ARIA roles, focus management, and keyboard support.
- Give every `for:each` a stable `key` (the record Id, never the array index).
- Signal errors with text + icon, not color alone; associate every input with a `label`.
- Lazy-load heavy work: imperative fetch on demand, `loading` states, and avoid blocking the first paint.

**Don't:**

- Build clickable `<div>`s — they have no role, no tab stop, and no Enter/Space handling.
- Do DML/SOQL-triggering work or DOM mutation in `renderedCallback` without a guard — it re-runs every render and can loop.
- Use the array index as `key` — it defeats list diffing and causes wrong-row state on reorder.

## Edge cases / when the rule does NOT apply

A genuinely custom widget that no base component covers may need raw HTML — then you own the full ARIA contract (`role`, `aria-*`, `tabindex="0"`, key handlers) explicitly; that is a deliberate, reviewed cost, not a shortcut. `renderedCallback` is the correct place for third-party-library init and post-render DOM measurement — the guard pattern makes that safe. Static, never-reordered lists technically render correctly without `key`, but the platform still requires the attribute, so always supply it. Components rendered off-screen (in a closed tab/accordion) can defer their wires with conditional rendering to avoid paying for data the user hasn't asked to see.

## See also

- [`lwc-events-and-component-communication.md`](./lwc-events-and-component-communication.md) — listener lifecycle and unsubscribe
- [`lwc-wire-over-imperative-when-cacheable.md`](./lwc-wire-over-imperative-when-cacheable.md) — caching that cuts redundant fetches
- [`lwc-lds-before-apex.md`](./lwc-lds-before-apex.md) — base record-forms are accessible by default
- [`../skills/lwc-component-scaffold/SKILL.md`](../skills/lwc-component-scaffold/SKILL.md) — "Surface controller errors to the template; never swallow them"

## Provenance

Grounded in Salesforce LWC accessibility guidance (base-component ARIA, label requirements) and the render-lifecycle / `renderedCallback` performance documentation; extends the error-surfacing step of [`../skills/lwc-component-scaffold/SKILL.md`](../skills/lwc-component-scaffold/SKILL.md).

---

_Last reviewed: 2026-05-30 by `claude`_
