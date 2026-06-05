# Code-split by route and lazy-load heavy components

**Status:** Absolute rule
**Domain:** Bundle performance
**Applies to:** `frontend-engineering`

---

## Why this exists

Shipping a single monolithic JavaScript bundle forces every user to download and parse the code for every route — including routes they will never visit. A 2 MB bundle is a slow first load and a Core Web Vitals failure (LCP, INP) that you chose. Route-level code splitting is the minimum: the user downloads only the code for the current route and lazy-loads the rest on demand. Heavy components (rich text editors, chart libraries, map renderers, PDF viewers) should be split out of the initial bundle even within a route.

## How to apply

```typescript
// Next.js — route-level splitting is automatic with the App Router.
// For heavy components within a route, use dynamic import:
import dynamic from 'next/dynamic';

const RichTextEditor = dynamic(() => import('./RichTextEditor'), {
  loading: () => <EditorSkeleton />,
  ssr: false,  // editor needs the browser DOM
});

// Vite / vanilla React — React.lazy + Suspense
import { lazy, Suspense } from 'react';
const ChartPage = lazy(() => import('./pages/ChartPage'));

function App() {
  return (
    <Suspense fallback={<PageSpinner />}>
      <ChartPage />
    </Suspense>
  );
}
```

**Do:**
- Split at route boundaries as the baseline; every page is its own chunk.
- Lazy-load any library over ~50 kB that is not needed for the initial render (charts, maps, video players, PDF renderers).
- Provide a meaningful loading skeleton, not a blank screen, while the chunk loads.
- Analyze the bundle with `next build --analyze` / `rollup-plugin-visualizer` / Webpack Bundle Analyzer to verify the split took effect.

**Don't:**
- Lazy-load components that are always visible above the fold — the loading flash degrades the experience.
- Split so aggressively that dozens of tiny parallel requests replace one larger one — find the right granularity.
- Forget to preload chunks for routes the user is likely to navigate to next (`<link rel="prefetch">`).

## Edge cases / when the rule does NOT apply

Server Components (Next App Router) are not shipped as client JS at all — they do not need explicit lazy-loading. A tiny SPA with a bundle under 100 kB total may not benefit from route splitting.

## See also

- [`../agents/frontend-performance-engineer.md`](../agents/frontend-performance-engineer.md) — owns bundle analysis and Core Web Vitals.
- [`./the-bundle-is-a-budget.md`](./the-bundle-is-a-budget.md) — the budget framing that motivates code-splitting.

## Provenance

Standard React / Next.js performance practice. Codifies `frontend-performance-engineer`'s bundle discipline and CLAUDE.md §2 ("The bundle is a budget").

---

_Last reviewed: 2026-06-05 by `claude`_
