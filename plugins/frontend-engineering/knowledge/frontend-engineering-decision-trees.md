# Frontend Engineering — Decision Trees

_Decision trees + a dated capability map. Capability rows are `[verify-at-build]` — re-check against the vendor before quoting. Last reviewed: 2026-06-04._

Traverse before choosing a rendering mode or a place for state.

## Decision Tree: Rendering strategy per route

Match each route to its real need; don't force one global mode.

```mermaid
graph TD
  A[A route] --> B{Needs SEO / fast first paint?}
  B -- No, behind login --> C[CSR is fine]
  B -- Yes --> D{Content personalized per request?}
  D -- No, same for everyone --> E{Changes rarely?}
  E -- Yes --> F[SSG]
  E -- No, periodically --> G[ISR]
  D -- Yes --> H[SSR / RSC]
  H --> I[Default server components; hydrate interactive islands]
```

_One global rendering mode is a mismatch on some route._

## Decision Tree: Where should this state live?

Server data is a cache; client state goes at the narrowest workable scope.

```mermaid
graph TD
  A[A piece of state] --> B{Comes from the server/API?}
  B -- Yes --> C[Server-cache lib: TanStack Query / RSC - NOT a global store]
  B -- No, client-only --> D{Used by one component?}
  D -- Yes --> E[Local useState]
  D -- No --> F{Small shared subtree?}
  F -- Yes --> G[Context]
  F -- No, truly global cross-cutting --> H[Store: Zustand/Redux]
  C --> I{Derived from other state?}
  I -- Yes --> J[Derive in render - don't store]
```


## Decision Tree: Server component or client component?

Default to a server component; reach for `"use client"` only where the browser is genuinely needed.

```mermaid
graph TD
  A[A component in the tree] --> B{Needs state, effects, event handlers, or browser APIs?}
  B -- No --> C[Server component - default; no JS shipped]
  B -- Yes --> D{Can the interactive part be a small leaf?}
  D -- Yes --> E[Push 'use client' down to that leaf only]
  D -- No, whole subtree is interactive --> F{Does it need server-only data/secrets?}
  F -- Yes --> G[Fetch on the server; pass data down as props to the client island]
  F -- No --> H[Client component is fine here]
  E --> I[Keep server parents passing serializable props in]
  G --> I
```

_Marking a high node `"use client"` forces its whole subtree to the client and ships their JS — keep the boundary as low and as small as the interactivity actually requires._

## Decision Tree: Client-side or server-side data fetching?

Fetch on the server by default; fetch on the client only when the data depends on the client.

```mermaid
graph TD
  A[Data a view needs] --> B{Known at request time, same per request shape?}
  B -- Yes --> C{Needs SEO or fast first paint?}
  C -- Yes --> D[Server fetch - RSC/loader; render with data present]
  C -- No, behind login app shell --> E{Refetch/realtime/optimistic interactions?}
  E -- Yes --> F[Client server-cache lib - TanStack Query/SWR]
  E -- No --> D
  B -- No, depends on client state/interaction --> F
  F --> G[Parallelize independent fetches - avoid waterfalls]
  D --> G
```

_Effect-based fetching deep in a leaf is the waterfall trap: the child can't start until the parent renders. Hoist and parallelize, or fetch on the server._

## Decision Tree: Optimistic update or wait for the server?

Show instant feedback when the write almost always succeeds and a rollback is cheap.

```mermaid
graph TD
  A[A mutation from the UI] --> B{Does the user need instant feedback?}
  B -- No --> C[Pending state + spinner; commit on server confirm]
  B -- Yes --> D{High success rate and a clear final state?}
  D -- No, often fails / multi-step --> C
  D -- Yes --> E{Can you cleanly roll back on failure?}
  E -- No --> C
  E -- Yes --> F[Optimistic update: apply locally, then reconcile]
  F --> G[On error: roll back + surface a retry]
  F --> H[On success: invalidate/refetch to reconcile server truth]
```

_Optimistic UI is a bet that the write succeeds; only take it when the rollback is clean and the failure rate low, or you'll flicker the user's data on every error._

## Capability map (dated — verify at build)

| Capability | 2026 state `[verify-at-build]` | Notes |
|---|---|---|
| React Server Components | GA in Next App Router | Default server, hydrate islands |
| TanStack Query / SWR | mature | Server-cache, not client state |
| INP (Core Web Vital) | replaced FID (2024) | Main-thread responsiveness |
| Code-splitting / dynamic import | standard | Per-route + heavy components |
| TypeScript strict | standard | Type the boundaries; no `any` |
| Vite / Next build | mature | Lean builds; analyze the bundle |
