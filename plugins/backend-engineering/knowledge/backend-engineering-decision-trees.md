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

## Decision Tree: Rate limiting — where and at what granularity?

**When this applies:** You are adding rate limiting to a backend service or endpoint and need to decide where the limit lives and how fine-grained it should be. Typically triggered when traffic spikes cause cascading failures, costs spike, or an abuse vector is identified.

**Last verified:** 2026-06-05 against standard backend resilience patterns and OWASP API4.

```mermaid
flowchart TD
    START[Adding a rate limit] --> Q1{Is there a gateway or reverse proxy in front?}
    Q1 -->|Yes| Q2{Is the limit purely IP/token-level coarse protection?}
    Q2 -->|Yes - global protection| GATEWAY[Enforce at the gateway - no app code needed]
    Q2 -->|No - per-tenant or per-resource granularity| BOTH[Gateway coarse limit + app-layer fine-grained limit]
    Q1 -->|No gateway| Q3{Is this a public-facing endpoint?}
    Q3 -->|Yes| APPRATE[App-layer token bucket per caller - Redis atomic counter]
    Q3 -->|No - internal service| Q4{Can one caller saturate the downstream?}
    Q4 -->|Yes| APPRATE
    Q4 -->|No - low-traffic internal| NONE[Bulkhead concurrency limit is sufficient]
    BOTH --> RETURN[Return 429 with Retry-After + RateLimit headers]
    APPRATE --> RETURN
    GATEWAY --> RETURN
```

**Rationale per leaf:**
- *Gateway only* — coarse IP/token rate limiting at the reverse proxy keeps attack traffic out before it hits the app; zero app-code cost.
- *Gateway + app layer* — the gateway absorbs burst; the app layer enforces per-tenant/resource fairness the gateway can't reason about.
- *App-layer token bucket* — Redis `INCR` + `EXPIRE` gives atomic per-caller counts; use when no gateway exists or when the limit requires business context.
- *Bulkhead only* — low-traffic internal services do not need a per-request counter; a concurrency bulkhead prevents pool saturation.

**Tradeoffs summary:**

| Method | Cost / time | Blast radius | Approval gate? | Use when |
|---|---|---|---|---|
| Gateway only | Low | Coarse - all callers share | Gateway team approval | Coarse abuse protection, no per-tenant need |
| App-layer bucket | Medium | Per caller | None | Per-tenant fairness, no gateway |
| Gateway + app layer | High | Fine-grained | Gateway team approval | Public API with per-tenant SLAs |
| Bulkhead only | Low | Per dependency | None | Internal service, low traffic |

## Decision Tree: Background job failure — retry, DLQ, or compensate?

**When this applies:** A background job or async worker has failed after processing a message. You need to decide whether to retry the message, move it to a dead-letter queue, or issue a compensating action. Triggered by an exception, a downstream timeout, or a constraint violation in the worker.

**Last verified:** 2026-06-05 against standard queue-reliability patterns (SQS, RabbitMQ, Kafka).

```mermaid
flowchart TD
    START[Job failed] --> Q1{Is the failure transient - network blip/timeout/temporary unavailability?}
    Q1 -->|Yes| Q2{Has the job exceeded max retries?}
    Q2 -->|No| RETRY[Retry with exponential backoff and jitter]
    Q2 -->|Yes| DLQ[Move to DLQ - alert on delivery]
    Q1 -->|No - deterministic failure - bad data/constraint/bug| Q3{Was any partial state written?}
    Q3 -->|No| DLQ
    Q3 -->|Yes - partial side effects exist| Q4{Are the side effects reversible?}
    Q4 -->|Yes| COMPENSATE[Issue compensating action - then DLQ for audit]
    Q4 -->|No - irreversible| ALERT[DLQ + page on-call - manual remediation needed]
    RETRY --> Q5{Is the operation idempotent?}
    Q5 -->|No| STOP[STOP - make it idempotent before retrying]
    Q5 -->|Yes| PROCEED[Retry is safe - proceed]
```

**Rationale per leaf:**
- *Retry with backoff* — transient failures are expected; backoff + jitter avoids synchronized retry storms.
- *DLQ* — after max retries or a deterministic failure, the message needs human inspection; a DLQ preserves it.
- *Compensating action* — if partial state was written, issue a semantic undo before parking the message.
- *Alert + manual* — irreversible partial side effects cannot be auto-compensated; escalate immediately.

**Tradeoffs summary:**

| Method | Cost / time | Blast radius | Approval gate? | Use when |
|---|---|---|---|---|
| Retry | Low | None if idempotent | None | Transient failure, idempotent job |
| DLQ | Low | Deferred - human reviews | None | Max retries exceeded or bad data |
| Compensate + DLQ | Medium | Undo the partial write | None | Partial side effects, reversible |
| Alert + manual | High | Immediate escalation | On-call | Irreversible partial side effects |

## Decision Tree: Should this state be stored in a cache or in the database?

**When this applies:** You have a piece of application state and must decide whether it belongs in a cache (Redis/in-process) or in the primary database. Triggered when adding a new data concept or when performance profiling shows repeated expensive reads.

**Last verified:** 2026-06-05 against cache-aside and data-access best practices.

```mermaid
flowchart TD
    START[A piece of state to store] --> Q1{Is this the source of truth - does losing it break correctness?}
    Q1 -->|Yes - system of record| DB[Store in the database - cache is optional acceleration]
    Q1 -->|No - computed/derived/session| Q2{Can it be cheaply recomputed or re-fetched on cache miss?}
    Q2 -->|No - expensive to recompute| DB
    Q2 -->|Yes| Q3{Is it read far more often than it is written?}
    Q3 -->|No - write-heavy| DB
    Q3 -->|Yes - read-heavy| Q4{Do you have a clear invalidation trigger?}
    Q4 -->|No| TTLONLY[Cache with short TTL only - no explicit invalidation]
    Q4 -->|Yes| CACHEASIDE[Cache-aside with explicit invalidation on write]
    DB --> OPTCACHE[Optionally layer a cache on top for hot reads]
    CACHEASIDE --> STAMPEDE{Hot key risk?}
    STAMPEDE -->|Yes| SINGLEFLIGHT[Add single-flight lock - stampede protection]
    STAMPEDE -->|No| DONE[Cache-aside is sufficient]
```

**Rationale per leaf:**
- *Database (source of truth)* — correctness and durability requirements always win; the database is the last line of defense.
- *Short-TTL-only cache* — without a clear invalidation trigger, a TTL is the safety net; accept bounded staleness.
- *Cache-aside with invalidation* — the standard pattern: write invalidates the cache; reads populate it on miss.
- *Single-flight lock* — a hot key with many concurrent misses needs stampede protection to avoid a thundering-herd DB hit.

**Tradeoffs summary:**

| Method | Cost / time | Blast radius | Approval gate? | Use when |
|---|---|---|---|---|
| Database only | Low | None | None | Source of truth, write-heavy |
| TTL-only cache | Low | Bounded staleness | None | No clear invalidation trigger |
| Cache-aside + invalidation | Medium | Stale on miss | None | Read-heavy, clear write trigger |
| Single-flight + cache-aside | Medium-high | None | None | Hot key, concurrent misses |
