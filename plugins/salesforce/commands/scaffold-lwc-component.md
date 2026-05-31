---
description: Scaffold a Lightning Web Component the right way — LDS/wire before imperative Apex, a cacheable + FLS-aware + bulk-safe Apex controller only when needed, accessibility and performance baked in, and proper event-based component communication.
argument-hint: "[component name and purpose, e.g. 'accountSummary card']"
---

# Scaffold an LWC

You are running `/salesforce:scaffold-lwc-component`. Scaffold a Lightning Web Component for what the user described (`$ARGUMENTS`), following this plugin's LWC best-practices (the `salesforce-platform-architect`'s front-end discipline). The `lwc-component-scaffold` skill carries the mechanics; this command makes the right *architecture* choices.

## When to use this

A new UI component is needed on a record page, app page, or community. Prefer base Lightning components and Lightning Data Service before reaching for custom Apex.

## Steps

1. **Data layer — LDS/wire before Apex** (`lwc-lds-before-apex`): if the component reads/writes a single record's fields, use `lightning-record-form` / `getRecord` / `updateRecord` — no Apex controller at all.
2. **Only if Apex is genuinely needed** (complex query, multi-object, aggregation): scaffold a controller that is **`@AuraEnabled(cacheable=true)`** for reads, **FLS-aware** (`WITH SECURITY_ENFORCED` or `Security.stripInaccessible`), and **bulk-safe** (`lwc-controller-is-cacheable-fls-aware-and-bulk-safe`). Prefer **`@wire` over imperative** when the data is cacheable (`lwc-wire-over-imperative-when-cacheable`).
3. **Component communication** (`lwc-events-and-component-communication`): child→parent via `CustomEvent`, parent→child via public `@api` props / methods, cross-tree via Lightning Message Service — never reach into another component's DOM.
4. **Accessibility + performance** (`lwc-accessibility-and-performance`): semantic markup, ARIA where base components don't cover it, keyboard reachable, no heavy work in `renderedCallback`, lazy-load where possible.
5. Scaffold `.js`, `.html`, `.js-meta.xml` (with the right targets), and a Jest test. Show the diff.

## Guardrails

- Don't write an Apex controller for what LDS already does — it's slower, less secure by default, and more to maintain.
- A `cacheable=true` method must be side-effect-free (no DML). Imperative calls for writes.
- Tee up the deploy (`sf project deploy`) and the page-assignment step with exact commands.
