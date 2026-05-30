# Keep INP under 200 ms by breaking up long tasks

**Status:** Primary diagnostic — when the page "feels laggy" on tap/type/click, INP is the metric, and long main-thread tasks are the first suspect.

**Domain:** Performance / Core Web Vitals

**Applies to:** `web-design`

---

## Why this exists

INP (Interaction to Next Paint) replaced FID and measures the **full** interaction lifecycle — input delay + processing + presentation — not just the first input. It is the **most-failed 2026 CWV (~43% of sites fail)** because it surfaces real responsiveness, not a single early moment [verify-at-build — INP threshold + failure rate]. The "good" bar is **< 200 ms** at field p75. The dominant cause is long JavaScript tasks blocking the main thread: heavy event handlers, synchronous hydration, and third-party scripts that monopolize the CPU when the user is trying to act.

## How to apply

Find the long tasks (DevTools Performance panel, the "long animation frames" API, or web-vitals.js attribution), then yield, defer, or remove them. Hand control back to the browser between chunks of work.

```js
// Don't: one long synchronous task blocks paint until everything finishes
function onClick() {
  doExpensiveWork();      // 350 ms of synchronous work
  updateDom();            // user sees nothing until this completes — INP spikes
}

// Do: update the UI immediately, then yield before the heavy part
async function onClick() {
  showPendingState();              // immediate visual feedback (the "next paint")
  await scheduler.yield();         // hand control back so the paint can happen
  await processInChunks(items, { chunkSize: 50 }); // break the long task up
}
```

**Do:**
- Break long tasks with `scheduler.yield()` (or `postTask` / `setTimeout(0)` fallback); paint a pending state *before* the heavy work.
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
- [`../knowledge/web-platform-capabilities-2026.md`](../knowledge/web-platform-capabilities-2026.md) — INP as most-failed, `scheduler.yield()`, third-party debt
- [`../agents/performance-engineer.md`](../agents/performance-engineer.md) — INP fix-by-symptom map

## Provenance

Distilled from the `performance-engineer` agent's INP fix-by-symptom map (long JS task on input, debounce, hydration cost, third-party blocking) and the CWV table in `web-platform-capabilities-2026.md` (INP replaced FID; most-failed in 2026; `scheduler.yield()`; retrieved 2026-05-28).

---

_Last reviewed: 2026-05-30 by `claude`_
