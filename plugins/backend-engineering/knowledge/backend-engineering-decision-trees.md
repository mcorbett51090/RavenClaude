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


## Capability map (dated — verify at build)

| Capability | 2026 state `[verify-at-build]` | Notes |
|---|---|---|
| Modular-monolith-first | mainstream guidance | Split on real need, not by default |
| Transactional outbox | established pattern | Avoids dual-write loss/phantom |
| Idempotency keys | standard for webhooks/payments | Dedup store required |
| Circuit breakers / bulkheads | mature (libs per language) | Fail fast, isolate |
| Backoff + jitter | standard | Avoid synchronized retry storms |
| Redis / cache-aside | mature | Invalidation is the hard part |
