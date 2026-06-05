# Keep long tasks off the main thread

**Status:** Absolute rule
**Domain:** INP / Core Web Vitals
**Applies to:** `frontend-engineering`

---

## Why this exists

INP (Interaction to Next Paint) measures the delay between a user input and the browser painting a visual response. Any JavaScript task running longer than 50 ms on the main thread is a "long task" and directly delays all input handling during that window. A 500 ms long task means a 500 ms unresponsive UI — the user feels the app is frozen. INP replaced FID as a Core Web Vital in 2024; it is now a ranking signal and a direct measure of perceived interactivity.

## How to apply

Break up long synchronous work. Defer non-urgent work to after the current frame.

```typescript
// Bad: blocking the main thread with synchronous processing
function processLargeList(items: Item[]) {
  return items.map(expensiveTransform);  // blocks for 600ms on 10k items
}

// Good: yield to the browser between chunks
async function processLargeListAsync(items: Item[]): Promise<TransformedItem[]> {
  const CHUNK_SIZE = 100;
  const result: TransformedItem[] = [];

  for (let i = 0; i < items.length; i += CHUNK_SIZE) {
    const chunk = items.slice(i, i + CHUNK_SIZE);
    result.push(...chunk.map(expensiveTransform));

    // Yield to the event loop — let input events be processed
    await new Promise(resolve => setTimeout(resolve, 0));
  }
  return result;
}

// For CPU-heavy work: Web Workers
const worker = new Worker(new URL('./heavyWorker.ts', import.meta.url));
```

**Do:**
- Use `scheduler.yield()` (or `setTimeout(0)`) to break up long tasks and yield to the browser.
- Move truly CPU-intensive work (image processing, large data transforms) to a Web Worker.
- Defer non-critical UI updates with `startTransition` — marks the update as non-urgent so React can interrupt it.
- Measure with Lighthouse / Chrome DevTools Performance panel to identify long tasks.

**Don't:**
- Parse/transform large arrays synchronously in response to a user interaction.
- Put heavy synchronous computation in a render function or `useMemo` dependency that runs on every keystroke.
- Use `setInterval` for animation — use `requestAnimationFrame`.

## Edge cases / when the rule does NOT apply

Server-rendered pages (RSC/SSR) do not run heavy computation on the browser main thread. CLI tools and Node.js backends operate on a server event loop where "main thread" behavior is different (though the same blocking principle applies).

## See also

- [`../agents/frontend-performance-engineer.md`](../agents/frontend-performance-engineer.md) — owns INP and Core Web Vitals.
- [`./code-split-by-route-and-lazy-load-heavy-components.md`](./code-split-by-route-and-lazy-load-heavy-components.md) — reducing parse/eval cost is complementary to reducing execution cost.

## Provenance

Google Core Web Vitals INP specification (web.dev/inp), Chrome DevTools long-task guidance, and the `scheduler.yield()` API proposal. Codifies `frontend-performance-engineer`'s main-thread discipline.

---

_Last reviewed: 2026-06-05 by `claude`_
