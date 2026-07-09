---
name: lwc-component-scaffold
description: Scaffold a Lightning Web Component bundle (.html / .js / .js-meta.xml) with an FLS-aware Apex controller. Use when creating a new LWC.
---

# LWC Component Scaffold

Generate a complete LWC bundle wired to a secure, cacheable Apex controller.

## When to use

Creating a new Lightning Web Component that reads or writes Salesforce data.

## Steps

1. **Bundle trio.** Produce `<name>.html`, `<name>.js`, and `<name>.js-meta.xml` with the right `apiVersion`, targets, and exposure. See `templates/lwc-bundle.md`.
2. **Wire data the lightning way.** Prefer `@wire` to a cacheable Apex method or to `getRecord`/UI API over imperative calls; reach for imperative Apex only for user-triggered actions.
3. **FLS-aware controller.** The Apex controller method is `@AuraEnabled(cacheable=true)` for reads, uses `WITH USER_MODE` (or `Security.stripInaccessible`), and is `with sharing`. **At API v67.0+ `WITH SECURITY_ENFORCED` no longer compiles** — use `WITH USER_MODE`. (House opinions #6-#7.) `[verify-at-build]`
4. **Bulk-safe controller.** No SOQL/DML in loops; accept and return collections where the UI is list-shaped.
5. **Error handling.** Surface controller errors to the template; never swallow them.

## Output

The three bundle files, the Apex controller, and a note on which FLS enforcement and sharing mode were applied. Escalate any security concern to `ravenclaude-core/security-reviewer`.
