# Memoize only when a measured performance problem exists

**Status:** Pattern
**Domain:** React implementation / performance
**Applies to:** `frontend-engineering`

---

## Why this exists

`useMemo`, `useCallback`, and `React.memo` carry a cost: they allocate extra memory, add comparison overhead on every render, and obscure data flow. When applied prematurely — wrapping everything "just in case" — they add complexity without measurable benefit and can even slow things down (the comparison cost exceeds the render cost for cheap computations). The React team is explicit: memoization is an optimization for measured bottlenecks, not a default posture.

## How to apply

Profile first. Use React DevTools Profiler or the browser's performance timeline to identify which components render unnecessarily and how expensive those renders are. Then apply memoization surgically.

```typescript
// Correct use: expensive computation, stable inputs
const sortedItems = useMemo(
  () => expensiveSort(items),    // proven expensive in the profiler
  [items]                        // only re-sort when items reference changes
);

// Correct use: stable callback reference for a memoized child
const handleSubmit = useCallback(
  (data: FormData) => submitMutation.mutate(data),
  [submitMutation]  // submitMutation is stable from a library hook
);

// Overkill: cheap computation
const label = useMemo(() => `Hello, ${name}`, [name]); // just write it inline
```

**Do:**
- Profile before adding `useMemo` / `useCallback` / `React.memo`.
- Apply `React.memo` to a component that: (a) renders frequently, (b) with the same props, and (c) is itself expensive to render.
- Stabilize the dependency array by ensuring object/array values used as deps are themselves memoized or primitive.

**Don't:**
- Wrap every component in `React.memo` by default.
- Put every function in `useCallback` "for safety."
- Use `useMemo` for simple string/number expressions.
- Use memoization to hide a deeper data-flow or re-render bug — fix the source first.

## Edge cases / when the rule does NOT apply

Context values that are objects and would cause every consumer to re-render on every parent render are a legitimate `useMemo` use case even without explicit profiling — the blast radius is architectural. Passing a callback to a dependency array of a child's `useEffect` also warrants `useCallback` to avoid spurious effect re-runs.

## See also

- [`../agents/react-implementation-engineer.md`](../agents/react-implementation-engineer.md) — owns hooks correctness and performance.
- [`../agents/frontend-performance-engineer.md`](../agents/frontend-performance-engineer.md) — owns profiling and Core Web Vitals.

## Provenance

React docs ("useMemo — Should you add useMemo everywhere?") and the React team's explicit guidance against premature memoization. Codifies the `react-implementation-engineer` position in this plugin.

---

_Last reviewed: 2026-06-05 by `claude`_
