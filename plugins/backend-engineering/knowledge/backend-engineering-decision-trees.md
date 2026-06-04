# Backend Engineering — Decision Trees

_Decision trees + a dated capability map. Capability rows are `[verify-at-build]` — re-check against the vendor before quoting. Last reviewed: 2026-06-04._

Traverse before splitting a service or adding a cache.

## Decision Tree: Monolith or a separate service?

Default to a modular monolith; a split must buy something concrete.

```mermaid
graph TD
  A[New capability / growing system] --> B{Concrete need to split?}
  B -- No --> C[Module in the monolith - clear boundary]
  B -- Independent scaling --> D[Consider a service]
  B -- Team autonomy / deploy isolation --> D
  B -- Real tech/runtime boundary --> D
  D --> E{Owns its own data?}
  E -- No, shares the DB --> F[STOP - that's a distributed monolith; keep it a module]
  E -- Yes --> G{Communication can be eventual?}
  G -- Yes --> H[Async / events between services]
  G -- No --> I[Sync API - own the timeout/idempotency/fallback]
```

_Name the trade: a split buys autonomy/scale and pays in operational + consistency complexity._

## Decision Tree: Should this be cached, and how?

Cache deliberately; the invalidation story is the design.

```mermaid
graph TD
  A[An expensive read] --> B{Read-heavy and tolerant of slight staleness?}
  B -- No, must be fresh/transactional --> C[Don't cache - fix the query/index with database-engineering]
  B -- Yes --> D{Clear invalidation trigger?}
  D -- No --> E[Define one first, or use a short TTL only]
  D -- Yes --> F[Cache-aside: read-through, write invalidates]
  F --> G{Hot key with concurrent misses?}
  G -- Yes --> H[Add single-flight/lock - stampede protection]
  G -- No --> I[TTL as a safety net + monitor hit rate]
```


## Decision Tree: Sync call or async event?

Sync couples availability and latency; async decouples but pays in eventual consistency.

```mermaid
graph TD
  A[Crossing a boundary] --> B{Caller needs the result to continue right now?}
  B -- Yes --> C{Can the work be eventual without blocking the user?}
  C -- No --> D[Sync call - own its timeout, retry idempotent-only, fallback]
  C -- Yes --> E[Return fast; do the rest async]
  B -- No, fire-and-forget --> F{Multiple consumers or future ones?}
  F -- Yes --> G[Publish an event - consumers subscribe independently]
  F -- No, one known consumer --> H[Enqueue a command to that consumer]
  G --> I[Outbox for write-then-publish + idempotent consumers]
  H --> I
  E --> I
```

_A sync call makes the callee's downtime your downtime; if you don't need the answer now, an event removes that coupling at the cost of eventual consistency._

## Decision Tree: Where should this cache live, and write-through or cache-aside?

Place the cache by who must see fresh data, and pick the write policy by consistency need.

```mermaid
graph TD
  A[Adding a cache] --> B{Same data read by many instances/services?}
  B -- Yes --> C[Shared cache - Redis/Memcached]
  B -- No, per-instance hot data --> D[In-process cache - fast, but each node can diverge]
  C --> E{Writes frequent and reads must reflect them fast?}
  D --> E
  E -- Reads tolerate staleness, writes rare --> F[Cache-aside + TTL + invalidate on write]
  E -- Reads must be fresh right after a write --> G[Write-through - write cache+store together]
  E -- Write-heavy, read-rare --> H[Write-behind only if loss-on-crash is acceptable]
  F --> I[Add single-flight for hot-key stampede]
  G --> I
```

_In-process caching is fastest but every node holds its own copy — without an invalidation broadcast they drift; a shared cache trades a network hop for one coherent view._

## Decision Tree: Extract this module into a service now, or later?

Get the module boundary right inside the monolith first; extract only when a concrete force demands it.

```mermaid
graph TD
  A[A module is growing painful] --> B{Is its data + API boundary already clean?}
  B -- No --> C[Fix the boundary IN the monolith first - extraction won't fix coupling]
  B -- Yes --> D{Concrete force to split?}
  D -- Independent scaling profile --> E[Extract - it scales on a different axis]
  D -- Separate team owns deploy cadence --> E
  D -- Different runtime/tech genuinely required --> E
  D -- None, just 'feels big' --> F[Keep it a module - a clean seam costs nothing to leave in place]
  E --> G{Can it own its data fully?}
  G -- No, shares tables --> H[STOP - split the data first or it's a distributed monolith]
  G -- Yes --> I[Extract behind its API/events; sequence the data move]
```

_A clean module boundary is reversible and free to leave in place; a premature extraction is a network hop and a distributed transaction you can't easily take back._

## Capability map (dated — verify at build)

| Capability | 2026 state `[verify-at-build]` | Notes |
|---|---|---|
| Modular-monolith-first | mainstream guidance | Split on real need, not by default |
| Transactional outbox | established pattern | Avoids dual-write loss/phantom |
| Idempotency keys | standard for webhooks/payments | Dedup store required |
| Circuit breakers / bulkheads | mature (libs per language) | Fail fast, isolate |
| Backoff + jitter | standard | Avoid synchronized retry storms |
| Redis / cache-aside | mature | Invalidation is the hard part |
