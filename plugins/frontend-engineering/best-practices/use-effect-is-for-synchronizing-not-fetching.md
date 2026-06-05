# Use useEffect to synchronize with external systems, not to fetch data

**Status:** Absolute rule
**Domain:** React implementation
**Applies to:** `frontend-engineering`

---

## Why this exists

`useEffect` was designed to synchronize a React component with an external system (a third-party widget, a browser API, a subscription). Using it to fetch data — the classic `useEffect(() => { fetch('/api/users').then(...) }, [])` — produces the "waterfall trap": the child can't start its fetch until its parent has rendered, which can't start until *its* parent has rendered. You also get double-fetches in React Strict Mode, manual loading/error/stale state management, and no caching. Data fetching belongs in a server-data library (TanStack Query, SWR, RSC loaders) that handles caching, deduplication, and staleness automatically.

## How to apply

```typescript
// Bad — useEffect data fetch
function UserProfile({ userId }: { userId: string }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetch(`/api/users/${userId}`)
      .then(r => r.json())
      .then(u => { setUser(u); setLoading(false); });
  }, [userId]);

  if (loading) return <Spinner />;
  return <div>{user?.name}</div>;
}

// Good — TanStack Query
function UserProfile({ userId }: { userId: string }) {
  const { data: user, isLoading } = useQuery({
    queryKey: ['user', userId],
    queryFn: () => fetch(`/api/users/${userId}`).then(r => r.json()),
  });

  if (isLoading) return <Spinner />;
  return <div>{user?.name}</div>;
}
```

**Do:**
- Use `useEffect` for: subscribing to browser events, synchronizing with a DOM widget, setting up a WebSocket listener, calling a third-party SDK's init method.
- Use a server-data library (TanStack Query, SWR, RSC data functions) for all API data fetching.
- In RSC/Next App Router: fetch in the server component; pass data down as props.

**Don't:**
- Put `fetch` / `axios` calls inside `useEffect` as the primary data-loading pattern.
- Manage `loading`, `error`, and `data` state manually alongside a `useEffect` fetch.
- Use `useEffect` to transform / derive state from other state — do that in the render function or a `useMemo`.

## Edge cases / when the rule does NOT apply

A one-off fire-and-forget side effect that is not data fetching (e.g., logging an analytics event when a component mounts) is fine in `useEffect`. If you are not using a server-data library and cannot add one, a well-structured `useEffect` with an `AbortController` is the fallback — but not the preferred approach.

## See also

- [`../agents/react-implementation-engineer.md`](../agents/react-implementation-engineer.md) — owns hooks correctness.
- [`./server-state-is-not-client-state.md`](./server-state-is-not-client-state.md) — the broader rule that server data belongs in a server-cache library.

## Provenance

React documentation (react.dev — "You Might Not Need an Effect") and TanStack Query rationale. Codifies `react-implementation-engineer` and `frontend-state-and-data-engineer` positions in this plugin's CLAUDE.md.

---

_Last reviewed: 2026-06-05 by `claude`_
