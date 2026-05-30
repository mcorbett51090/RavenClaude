# Treat model-driven form `OnLoad` as a performance budget — async with returned Promises, ≤3 web API calls, batched

**Status:** Pattern — strong default; exceed the budget only with a measured justification.

**Domain:** Model-driven apps / Web resources

**Applies to:** `power-platform`

---

## Why this exists

Form load is the user's first impression and a performance-critical path. JS web resources written in 2012-era patterns wreck it two ways. First, a synchronous `Xrm.WebApi` call blocks the form thread — the form freezes until the round-trip returns. Second, an `OnLoad` handler that fires four independent async calls *without* awaiting them together doubles (or worse) perceived load, and a fire-and-forget chain swallows its own errors so failures are invisible. The platform also needs to know when async load work is done: if your handler doesn't **return its Promise**, the form considers itself loaded before your data arrives, producing flicker and races. Each of these is a recurring `model-driven-engineer` anti-pattern.

## How to apply

Make `OnLoad` async, batch independent reads, run them in parallel with `Promise.all`, and **return** the Promise so the form respects completion.

```typescript
// DON'T — synchronous, blocks the thread; or fire-and-forget that swallows errors.
//   var r = Xrm.WebApi.online.retrieveMultipleRecords(...);   // sync = frozen form
//   loadA(); loadB(); loadC();                                 // no await, no error path

// DO — async, parallel, returns the Promise; errors are caught.
async function onLoad(executionContext) {
  const formContext = executionContext.getFormContext();   // not the deprecated Xrm.Page
  try {
    const [accounts, contacts, prefs] = await Promise.all([
      Xrm.WebApi.retrieveMultipleRecords("account",  "?$top=5"),
      Xrm.WebApi.retrieveMultipleRecords("contact",  "?$top=5"),
      Xrm.WebApi.retrieveRecord("systemuser", userId, "?$select=preferences"),
    ]);
    // ...populate form...
  } catch (e) {
    console.error("OnLoad failed", e);   // surface, don't swallow
  }
}
// Register so the framework awaits it: pass "executionContext as first parameter" = true,
// and have the handler RETURN the promise (return onLoad(executionContext)) for load completion.
```

**Do:**

- Keep `OnLoad` to ≤3 web API calls; batch more with `Xrm.WebApi.online.executeMultiple`, and parallelize independent ones with `Promise.all`.
- Defer non-critical work to `OnReadyStateComplete` or a button instead of front-loading it.
- Use `executionContext.getFormContext()`; null-check `formContext.getAttribute("x")` — the column may not be on this form.
- Keep web resources as source-controlled TypeScript, transpiled and packed into the solution — never authored in the portal.

**Don't:**

- Call any synchronous `Xrm.WebApi.*` variant on the form thread.
- Fire multiple async calls sequentially when they're independent — that stacks latencies.
- Reference deprecated `Xrm.Page`, or manipulate the model-driven DOM directly (`document.querySelector(...)`) — UCI releases break it.

## Edge cases / when the rule does NOT apply

- **A single fast read** — one small `retrieveRecord` doesn't need `Promise.all`; just await and return it.
- **Genuinely sequential dependencies** — when call B needs call A's result, sequence them, but still return the final Promise and consider deferring B off the critical path.
- **Transactional logic** — work that must be atomic with the server write belongs in a plug-in, not `OnSave` JS that races server-side writes.

## See also

- [`../skills/dataverse-web-resources/resources/js-form-scripts.md`](../skills/dataverse-web-resources/resources/js-form-scripts.md) — form-event scripting + async patterns
- [`../skills/dataverse-web-resources/resources/ux-decision-guide.md`](../skills/dataverse-web-resources/resources/ux-decision-guide.md)
- [`./apps-business-rules-before-javascript.md`](./apps-business-rules-before-javascript.md) — keep JS for genuine logic, not show/hide
- [`./apps-canvas-performance-budget.md`](./apps-canvas-performance-budget.md) — the canvas analogue of a load budget
- [`../agents/model-driven-engineer.md`](../agents/model-driven-engineer.md) — "Form load is a performance budget", async-OnLoad opinions

## Provenance

From `model-driven-engineer.md` opinions ("≤3 web API calls in OnLoad", `executeMultiple` batching, async `OnLoad` returning the Promise, `executionContext.getFormContext()` over `Xrm.Page`) and its flagged anti-patterns (synchronous `retrieveMultipleRecords`, four async calls without `Promise.all`, portal-authored web resources, DOM manipulation).

---

_Last reviewed: 2026-05-30 by `claude`_
