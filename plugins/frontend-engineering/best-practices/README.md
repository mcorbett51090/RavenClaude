# frontend-engineering — best-practice docs

Named, citable rules for the `frontend-engineering` plugin's specialists. Each file is **one rule**.

---

## Index

_22 rules across rendering strategy, state, React implementation, performance, accessibility, and TypeScript._

| Doc | Status | Use when |
|---|---|---|
| [`rendering-strategy-per-route.md`](./rendering-strategy-per-route.md) | Absolute rule | Choosing SSG / ISR / SSR / RSC / CSR — match each route to its real need. |
| [`server-state-is-not-client-state.md`](./server-state-is-not-client-state.md) | Absolute rule | API data — manage with a server-cache library, not a global store. |
| [`derive-state-dont-duplicate-it.md`](./derive-state-dont-duplicate-it.md) | Absolute rule | Any value computable from existing state — derive in render, don't store separately. |
| [`lift-and-pass-via-composition-not-drilling.md`](./lift-and-pass-via-composition-not-drilling.md) | Pattern | Sharing state across siblings — lift to common ancestor; use composition over drilling. |
| [`no-prop-drilling-beyond-two-levels.md`](./no-prop-drilling-beyond-two-levels.md) | Pattern | Passing a prop through 3+ intermediate components — use context or composition instead. |
| [`compose-dont-configure.md`](./compose-dont-configure.md) | Pattern | Building components — small composable units over a mega-component with boolean flags. |
| [`forms-are-controlled-and-validated-at-the-edge.md`](./forms-are-controlled-and-validated-at-the-edge.md) | Absolute rule | Any form — controlled inputs, schema validation at submit, no ad-hoc inline checks. |
| [`loading-and-error-states-are-the-feature.md`](./loading-and-error-states-are-the-feature.md) | Absolute rule | Any async data — loading and error UI are required, not optional edge cases. |
| [`fetch-where-the-framework-intends.md`](./fetch-where-the-framework-intends.md) | Absolute rule | Choosing where to fetch data — server by default (RSC/loader); client only when required. |
| [`use-effect-is-for-synchronizing-not-fetching.md`](./use-effect-is-for-synchronizing-not-fetching.md) | Absolute rule | Data loading — use a server-cache library; useEffect is for external system sync, not fetch. |
| [`memoize-only-when-measured.md`](./memoize-only-when-measured.md) | Pattern | useMemo / useCallback / React.memo — apply only after profiling shows a genuine bottleneck. |
| [`accessibility-is-implementation.md`](./accessibility-is-implementation.md) | Absolute rule | Any UI component — semantic HTML first, ARIA to fill gaps, keyboard and focus operable. |
| [`focus-management-for-dynamic-content.md`](./focus-management-for-dynamic-content.md) | Absolute rule | Modals, drawers, form results, route changes — move focus explicitly to the new content. |
| [`typescript-strict-at-the-boundaries.md`](./typescript-strict-at-the-boundaries.md) | Absolute rule | TypeScript setup — enable strict; no any at boundaries; types are the cheapest tests. |
| [`never-type-any-at-api-boundaries.md`](./never-type-any-at-api-boundaries.md) | Absolute rule | API response types and component props — parse/validate with zod; never cast with any. |
| [`the-bundle-is-a-budget.md`](./the-bundle-is-a-budget.md) | Absolute rule | Bundle size — set a budget, analyze regularly, split and lazy-load to stay within it. |
| [`code-split-by-route-and-lazy-load-heavy-components.md`](./code-split-by-route-and-lazy-load-heavy-components.md) | Absolute rule | Any route or heavy component — route-level split is the minimum; lazy-load anything over 50kB. |
| [`optimize-images-and-fonts.md`](./optimize-images-and-fonts.md) | Pattern | Images and web fonts — compress, use modern formats, reserve dimensions, swap gracefully. |
| [`avoid-layout-shift-reserve-space-for-async-content.md`](./avoid-layout-shift-reserve-space-for-async-content.md) | Absolute rule | CLS — reserve space for images/skeletons; never inject content above existing content. |
| [`keep-the-main-thread-unblocked.md`](./keep-the-main-thread-unblocked.md) | Absolute rule | INP — break up long tasks; yield to the browser; offload CPU-heavy work to Web Workers. |
| [`preconnect-and-prefetch-critical-resources.md`](./preconnect-and-prefetch-critical-resources.md) | Pattern | LCP — preconnect to third-party origins; preload the LCP image; prefetch likely-next routes. |
| [`test-ids-are-engineering-not-optional.md`](./test-ids-are-engineering-not-optional.md) | Absolute rule | Any interactive component — add data-testid at build time so E2E tests have stable selectors. |

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — plugin team constitution.
- [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md) — marketplace-wide best-practice docs.
