# Memoize only when a measured performance problem exists

**Status:** Pattern
**Domain:** React implementation / performance
**Applies to:** `frontend-engineering`

---

## Why this exists

`useMemo`, `useCallback`, and `React.memo` carry a cost: they allocate extra memory, add comparison overhead on every render, and obscure data flow. When applied prematurely — wrapping everything "just in case" — they add complexity without measurable benefit and can even slow things down (the comparison cost exceeds the render cost for cheap computations). The React team is explicit: memoization is an optimization for measured bottlenecks, not a default posture.

## Current default posture: enable the React Compiler

The **React Compiler shipped its first stable release, v1.0, on 2025-10-07** (announced at React Conf 2025). It performs build-time **automatic memoization** of components and hooks — no manual rewrites — so with the compiler enabled, hand-written `useMemo` / `useCallback` / `React.memo` are **largely unnecessary**: the compiler memoizes automatically. First-party integration guides exist for **Vite, Expo, and Next.js**, and it's compatible with **React 17+**. Compiler-powered lint rules now ship in `eslint-plugin-react-hooks`' `recommended` / `recommended-latest` presets.

**So the new default is:** enable the React Compiler from the start on new apps (and adopt it on existing ones). "Memoize only when measured" now means — the compiler is the default memoization posture, and **hand-written memoization is the exception**, reserved for the measured hot spots the compiler cannot cover. Everything below governs those residual cases.

## How to apply

Enable the compiler first. Then, for anything it doesn't cover, profile before reaching for a manual hook. Use React DevTools Profiler or the browser's performance timeline to identify which components render unnecessarily and how expensive those renders are. Then apply memoization surgically.

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

React Compiler v1.0 stable (2025-10-07): https://react.dev/blog/2025/10/07/react-compiler-1 ; React versions: https://react.dev/versions (retrieved 2026-07-09).

---

_Last reviewed: 2026-07-09 by `claude`_
