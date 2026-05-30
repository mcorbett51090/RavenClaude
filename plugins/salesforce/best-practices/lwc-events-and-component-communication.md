# Communicate by the smallest mechanism that reaches — props down, events up, LMS only across the DOM

**Status:** Pattern — strong default; escalate to a heavier channel only when the lighter one cannot reach.

**Domain:** Lightning Web Components / component communication

**Applies to:** `salesforce`

---

## Why this exists

LWC has a deliberate communication hierarchy, and reaching for the heaviest channel by habit creates components that are impossible to reason about. Data flows **down** through `@api` public properties; notifications flow **up** through `CustomEvent`. A child that fires an event stays reusable because it knows nothing about its parent. Skip the hierarchy — broadcast everything over Lightning Message Service (LMS) or a `pubsub` singleton — and you get hidden coupling: any component can mutate any other, the data-flow graph is invisible, and a refactor in one corner breaks something three components away. LMS exists for the one case the parent/child tree genuinely cannot handle: communication **between components that aren't in the same DOM hierarchy** (e.g. two components in different regions of a Lightning page).

## How to apply

Pick the channel by the relationship between the two components.

```
Parent -> child:                 @api property (reactive; child re-renders on change)
Child  -> parent:                this.dispatchEvent(new CustomEvent('x', { detail }))
Parent <-> child two-way:        @api property down + CustomEvent up (no two-way binding)
Method call on a child:          @api method on the child, parent calls via this.refs / querySelector
Across the DOM (no ancestor):    Lightning Message Service (publish/subscribe on a message channel)
Same record context on a page:   often no message needed — wire to getRecord and share the LDS cache
```

```js
// Child fires up — composed:false (default) keeps it from leaking past the parent.
this.dispatchEvent(
  new CustomEvent("rowselect", { detail: { id: this.recordId } })
);
```

```html
<!-- Parent listens; passes data back down via @api -->
<c-row onrowselect={handleSelect} record-id={selectedId}></c-row>
```

**Do:**

- Default to props-down / events-up; keep `composed`/`bubbles` at their defaults (`false`) unless you specifically need the event to cross shadow boundaries.
- Use LMS (a `messageChannel` metadata file) only for cross-DOM communication, and unsubscribe in `disconnectedCallback`.

**Don't:**

- Build a custom `pubsub` singleton — LMS is the supported cross-DOM channel and survives navigation correctly.
- Mutate an object/array passed in via `@api` — inputs are effectively read-only; emit an event and let the owner change its own state.

## Edge cases / when the rule does NOT apply

Two components that merely need the **same record's data** usually don't need *any* message — both wire `getRecord` and share the LDS cache, so an edit in one refreshes the other automatically (see [`lwc-lds-before-apex.md`](./lwc-lds-before-apex.md)). `bubbles: true, composed: true` is legitimate for a genuinely page-level notification, but it crosses shadow DOM and couples you to ancestors — use it consciously, not as a default. Aura-interop and `pageReference` navigation use their own platform events (`NavigationMixin`), not custom events. State shared across an entire app feature may justify a wire-adapter-backed store, but that is past the point where simple events suffice.

## See also

- [`lwc-lds-before-apex.md`](./lwc-lds-before-apex.md) — the shared LDS cache that removes many "messages"
- [`lwc-accessibility-and-performance.md`](./lwc-accessibility-and-performance.md) — event listeners and render cost
- [`../knowledge/flow-lwc-decision-trees.md`](../knowledge/flow-lwc-decision-trees.md) — the "component communication: events vs LMS vs public API" tree
- [`../skills/lwc-component-scaffold/SKILL.md`](../skills/lwc-component-scaffold/SKILL.md) — the bundle these components live in

## Provenance

Grounded in the LWC communication model (public properties, `CustomEvent`, Lightning Message Service) from Salesforce LWC documentation; extends [`../skills/lwc-component-scaffold/SKILL.md`](../skills/lwc-component-scaffold/SKILL.md) into the multi-component case.

---

_Last reviewed: 2026-05-30 by `claude`_
