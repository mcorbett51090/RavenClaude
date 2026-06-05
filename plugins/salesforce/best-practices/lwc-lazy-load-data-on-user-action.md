# Lazy-load expensive data on user action — do not load everything on component initialize

**Status:** Pattern
**Domain:** LWC performance
**Applies to:** `salesforce`

---

## Why this exists

An LWC component that loads all related data on `connectedCallback` or via a `@wire` that fires immediately creates a slow first paint for every user who opens the page, even when they never interact with the data. On record pages with multiple LWC components, N simultaneous Apex calls on load saturate the browser's concurrent-connection limit and produce a cascading slow-load effect. Lazy loading — loading data only when the user triggers an interaction (clicks a tab, opens an accordion, triggers a search) — isolates the latency to the user who needs the data and keeps initial page paint fast.

## How to apply

```javascript
// Eager (bad for large or secondary data)
connectedCallback() {
    this.loadAllRelatedCases(); // fires on every page load
}

// Lazy (correct for secondary panels)
handleTabActivate(event) {
    if (event.detail.value === 'cases' && !this.casesLoaded) {
        this.loadRelatedCases();
        this.casesLoaded = true;
    }
}
```

Pattern for accordion / tab panels:
```html
<template>
    <lightning-accordion>
        <lightning-accordion-section name="cases" label="Related Cases"
            onsectiontoggle={handleSectionToggle}>
            <template if:true={casesVisible}>
                <c-related-cases record-id={recordId}></c-related-cases>
            </template>
        </lightning-accordion-section>
    </lightning-accordion>
</template>
```

**Do:**
- Lazy-load data inside tabs, accordions, and modals — the user explicitly requested the content.
- Use a loaded guard (`if (!this.dataLoaded)`) to prevent re-fetching on every re-render when the panel stays open.
- Combine lazy load with a `lightning-spinner` to give visual feedback during the load.

**Don't:**
- Lazy-load primary key data the user needs immediately — the first visible state of the component (the record title, the primary status field) must load eagerly.
- Implement lazy loading with a polling loop — use event-driven triggers (tab activation, accordion open, button click) only.
- Apply lazy loading to a single-screen component where all the data is always visible — it adds complexity without benefit.

## Edge cases / when the rule does NOT apply

A component that is the single primary element on a standalone page (not embedded in a record page alongside other components) can load all its data eagerly — there is no competition for browser connections on load.

## See also

- [`../agents/apex-engineer.md`](../agents/apex-engineer.md) — owns the Apex controller behind the wire calls
- [`./lwc-wire-over-imperative-when-cacheable.md`](./lwc-wire-over-imperative-when-cacheable.md) — the wire vs imperative decision that determines how the lazy load is triggered

## Provenance

Codifies standard LWC performance best practice applied to the Salesforce record-page multi-component context; Lightning Web Components developer guide, performance section.

---

_Last reviewed: 2026-06-05 by `claude`_
