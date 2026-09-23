# Keep INP under 200 ms by breaking up long tasks

**Status:** Primary diagnostic — when the page "feels laggy" on tap/type/click, INP is the metric, and long main-thread tasks are the first suspect.

**Domain:** Performance / Core Web Vitals

**Applies to:** `web-design`

---

## Why this exists

INP (Interaction to Next Paint) replaced FID and measures the **full** interaction lifecycle — input delay + processing + presentation — not just the first input. Per the HTTP Archive Web Almanac 2025, INP's mobile "good" rate is **77%**, ahead of LCP (62%, the most-failed CWV on mobile overall); INP is still the weakest metric on JS-heavy or high-traffic sites (top-1,000 mobile sites: only 63% good), which is why it stays a primary diagnostic here. The "good" bar is **< 200 ms** at field p75. The dominant cause is long JavaScript tasks blocking the main thread: heavy event handlers, synchronous hydration, and third-party scripts that monopolize the CPU when the user is trying to act.

## How to apply

Find the long tasks (DevTools Performance panel, the "long animation frames" API, or web-vitals.js attribution), then yield, defer, or remove them. Hand control back to the browser between chunks of work.

```js
// Don't: one long synchronous task blocks paint until everything finishes
function onClick() {
  doExpensiveWork();      // 350 ms of synchronous work
  updateDom();            // user sees nothing until this completes — INP spikes
}

// Don't: call scheduler.yield() unguarded — it throws a ReferenceError in Safari,
// which ships neither `scheduler` nor `requestIdleCallback`.
async function onClickUnsafe() {
  showPendingState();
  await scheduler.yield();  // ReferenceError in Safari — ships in Chrome 129+/Firefox 142+ only
  await processInChunks(items, { chunkSize: 50 });
}

// Do: update the UI immediately, then yield with a cross-browser fallback
async function yieldToMain() {
  if (typeof scheduler !== 'undefined' && scheduler.yield) {
    return scheduler.yield();      // Chrome/Edge 129+, Firefox 142+
  }
  return new Promise((resolve) => setTimeout(resolve, 0)); // Safari fallback
}

async function onClick() {
  showPendingState();              // immediate visual feedback (the "next paint")
  await yieldToMain();             // hand control back so the paint can happen, cross-browser
  await processInChunks(items, { chunkSize: 50 }); // break the long task up
}
```

**Do:**
- Break long tasks with a guarded yield (`scheduler.yield()` when present — Chrome/Edge 129+, Firefox 142+ — falling back to `setTimeout(fn, 0)` for Safari, which ships neither `scheduler` nor `requestIdleCallback`); paint a pending state *before* the heavy work.
- Defer / `async` non-critical JS, code-split, and lazy-load below-the-fold interactivity (and the third-party scripts that cause most INP failures).
- Measure INP in the **field** (CrUX / RUM at p75), since lab tools don't fire real interactions.

**Don't:**
- Run expensive work synchronously inside a click/input handler.
- Hydrate the whole page eagerly when only a few islands are interactive (static-first, house opinion #9).
- Treat a Lighthouse "Total Blocking Time" pass as proof INP is fine — TBT is lab, INP is field.

## Edge cases / when the rule does NOT apply

- **Genuinely static content sites** with no interactions may have no measurable INP — don't manufacture interactivity to "test" it; the win is shipping little JS in the first place.
- **One unavoidable heavy computation** (e.g. client-side search index) — move it to a Web Worker so the main thread stays free for paint.

## See also

- [`./budget-core-web-vitals-before-build.md`](./budget-core-web-vitals-before-build.md) — INP sits in the budget
- [`./frontend-progressive-enhancement.md`](./frontend-progressive-enhancement.md) — less JS shipped is less main-thread work
- [`../knowledge/web-design-decision-trees.md`](../knowledge/web-design-decision-trees.md) — "Which CWV is failing → which fix" tree
- [`../knowledge/web-platform-capabilities-2026.md`](../knowledge/web-platform-capabilities-2026.md) — INP CWV data, `scheduler.yield()`, third-party debt
- [`../agents/performance-engineer.md`](../agents/performance-engineer.md) — INP fix-by-symptom map

## Provenance

Distilled from the `performance-engineer` agent's INP fix-by-symptom map (long JS task on input, debounce, hydration cost, third-party blocking) and the CWV table in `web-platform-capabilities-2026.md` (INP replaced FID; `scheduler.yield()`). INP mobile "good" rate (77%), the LCP-is-most-failed-on-mobile correction, and the Safari `scheduler.yield()` gap corrected against the HTTP Archive Web Almanac 2025 Performance chapter and the `web-features` npm package (3.39.0), retrieved 2026-09-23.

---

_Last reviewed: 2026-09-23 by `claude`_
