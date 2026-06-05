---
scenario_id: 2026-06-05-server-state-in-redux-refactor
contributed_at: 2026-06-05
plugin: frontend-engineering
product: react
product_version: "unknown"
scope: likely-general
tags: [state-management, server-cache, tanstack-query, redux, refactor]
confidence: high
reviewed: false
---

## Problem

A mid-size React SPA had grown a large Redux store where ~80% of the slices were copies of API responses (`users`, `orders`, `products`, `invoices` …), each with hand-written `loading`/`error`/`data` flags, a thunk to fetch, a thunk to refetch, and bespoke reducers to merge updates. The bug parade that triggered the engagement: stale lists after a create/edit (the cache wasn't invalidated), two components fetching the same resource twice on mount (no dedup), and a "spinner that never stops" when an error thunk forgot to flip `loading: false`. The team's proposed fix was "more Redux discipline" — a stricter convention for the loading flags.

## Constraints context

- The state was **server state** — data owned by the backend, fetched over HTTP, with a freshness/TTL question — being stored as if it were **client state** (app-owned UI state).
- Every server slice re-implemented, by hand, what a server-cache library gives for free: caching, deduplication, background refetch, stale-while-revalidate, and invalidation.
- Genuinely client-only state in the same store (theme, the multi-step form's in-progress values, sidebar open/closed, selected filters) was a small minority of the slices and was working fine.
- A full rewrite was off the table; the refactor had to be incremental, slice by slice, shippable each step.

## Attempts

- Tried: the "more discipline" path — a lint rule and a code-review checklist for the loading flags. Reduced new occurrences slightly but didn't address the root cause (server state modeled as client state), and did nothing for dedup or invalidation. Treating the symptom.
- Tried: a custom `useFetch` hook wrapping the thunks. Centralized the loading-flag boilerplate but still had no shared cache across components, so the double-fetch-on-mount bug survived. Re-implementing a cache badly.
- Tried (the fix): adopted a **server-cache library** (TanStack Query) for the server slices and **kept Redux for the genuinely client-only state**. Migrated incrementally — one resource at a time, deleting its slice + thunks + flags and replacing them with a `useQuery`/`useMutation` pair keyed by the resource. Mutations declared the query keys they invalidate, so create/edit auto-refreshes the affected lists.

## Resolution

**Server state is not client state — and the cure is not "more store discipline," it's the right tool for each kind.** The defining question for every piece of state: *does it come from the server?*

1. **Server data → a server-cache library** (TanStack Query / SWR, or RSC where the framework supports it). It is a cache with a TTL and an invalidation story, not app state. The library gives caching, request dedup, background refetch, stale-while-revalidate, and declarative invalidation — exactly the four bugs the team was hand-fixing.
2. **Client-only state → the smallest workable scope** — `useState` for one component, Context for a stable subtree, a store (Redux/Zustand/Jotai) only for truly cross-cutting client state with complex transitions. Redux didn't get *deleted*; it got *right-sized* to the ~20% of state that was actually client state.
3. **Invalidation replaces manual refetch.** Once a mutation declares which query keys it touches, "stale list after create" stops being a bug class — the cache refetches the affected keys automatically. That single change retired most of the parade.
4. **Migrate incrementally, per resource.** Each slice → query is independently shippable; you never need a big-bang rewrite.

Putting server responses in Redux is the single most common React state-management mistake: you inherit the obligation to re-implement a cache (badly), and every loading-flag/dedup/stale-data bug flows from that. The blast radius drops the moment you stop conflating the two.

**Action for the next engineer:** before adding another Redux slice, ask "is this server data?" If yes, it belongs in TanStack Query / SWR / RSC, not the store — and the fix for a server-state-in-Redux codebase is migration, not discipline. Reserve the store for the client state that's left.

Cross-reference: this is the field-note complement to [`../best-practices/server-state-is-not-client-state.md`](../best-practices/server-state-is-not-client-state.md) and [`../best-practices/derive-state-dont-duplicate-it.md`](../best-practices/derive-state-dont-duplicate-it.md); the where-does-state-live and which-global-store-if-any trees are in [`../knowledge/frontend-engineering-decision-trees.md`](../knowledge/frontend-engineering-decision-trees.md). TanStack Query caching/invalidation model: https://tanstack.com/query/latest/docs/framework/react/guides/important-defaults (retrieved 2026-06-05).
