# Database Engineering — Decision Trees

_Decision trees + a dated capability map. Capability rows are `[verify-at-build]` — re-check against the vendor before quoting. Last reviewed: 2026-06-04._

Traverse before adding an index or running a migration.

## Decision Tree: Which index (or none)?

Read the plan first; match the index to the predicate; weigh the write cost.

```mermaid
graph TD
  A[Slow query] --> B[Read EXPLAIN ANALYZE]
  B --> C{Bottleneck = seq scan on a selective filter?}
  C -- No, stale stats / bad estimate --> D[ANALYZE / fix stats first]
  C -- Yes --> E{Predicate shape?}
  E -- equality/range --> F[B-tree]
  E -- filtered subset only --> G[Partial index]
  E -- multi-column --> H[Composite, ordered by selectivity]
  E -- jsonb/full-text --> I[GIN]
  F --> J{Heap fetches dominate?}
  J -- Yes --> K[Covering INCLUDE index]
  J -- No --> L[Done - verify write cost acceptable]
```

_Function on the indexed column = non-sargable = the index won't be used. Rewrite instead._

## Decision Tree: Is this migration safe to run live?

Expand/contract and lock-awareness keep a migration off the outage list.

```mermaid
graph TD
  A[A schema change] --> B{Does it take a heavy lock on a hot table?}
  B -- Yes (volatile default / type change / SET NOT NULL / non-concurrent index) --> C[Use the safe form]
  C --> D[Nullable add + batched backfill + NOT VALID then VALIDATE]
  C --> E[CREATE INDEX CONCURRENTLY]
  B -- No --> F{Destructive / irreversible?}
  F -- Yes --> G[Split: expand now, contract after switch + verify]
  F -- No --> H[Ship it - still reversible + ordered]
  D --> I[Sequence across deploys with release-engineer]
  E --> I
  G --> I
```


## Decision Tree: Normalize or denormalize this?

Default to 3NF; denormalize only with a measured read win and the write cost named.

```mermaid
graph TD
  A[A data shape decision] --> B[Model normalized to 3NF first]
  B --> C{A read hot-path is measurably slow from joins?}
  C -- No --> D[Stay normalized - integrity is structural]
  C -- Yes --> E{Can an index or covering index fix it?}
  E -- Yes --> F[Add the index - no redundancy introduced]
  E -- No --> G{Read-heavy and slight staleness tolerable?}
  G -- Yes --> H[Materialized view - refresh on a schedule/trigger]
  G -- No, must be live + fast --> I[Redundant column + enforce sync in the same txn/trigger]
  I --> J[Name the write-amplification + consistency cost you accepted]
```

_Prefer a covering index or materialized view over redundant columns; redundant columns are a consistency bug you must now maintain by hand._

## Decision Tree: SQL or NoSQL for this access pattern?

Start relational; choose a non-relational store only when the access pattern genuinely fits it.

```mermaid
graph TD
  A[A new data store choice] --> B{Relationships, multi-row transactions, ad-hoc queries?}
  B -- Yes --> C[Relational - Postgres; it also does JSONB for flexible fields]
  B -- No --> D{Single-key lookups at extreme scale, known access pattern?}
  D -- Yes --> E[Key-value / wide-column - design around the access pattern]
  D -- No --> F{Documents fetched whole, schema varies per record?}
  F -- Yes --> G[Document store - but model for the query, not free-form]
  F -- No --> H{Full-text / vector / graph traversal is the core need?}
  H -- Yes --> I[Specialized engine for that one need]
  H -- No --> C
```

_"NoSQL for flexibility" usually means an un-modeled relational schema; Postgres JSONB covers most flexible-field needs without giving up joins and transactions._

## Decision Tree: Scaling reads — replica, cache, or partition?

Read the plan first; each lever fixes a different bottleneck and they don't substitute.

```mermaid
graph TD
  A[Reads are slow / overloaded] --> B[Read EXPLAIN + check the bottleneck]
  B --> C{A single query is slow on a big table?}
  C -- Yes --> D[Index / rewrite first; partition only if size truly demands]
  C -- No, the primary is CPU/IO saturated by read volume --> E{Stale-by-seconds acceptable for these reads?}
  E -- Yes, repeated identical reads --> F[Cache-aside with an invalidation trigger]
  E -- Yes, but varied analytical reads --> G[Read replica - route reads, accept replication lag]
  E -- No, must be strongly consistent --> H[Scale the primary / fix the query - replica lag would lie]
  F --> I[Monitor hit rate; a low-hit cache just adds a hop]
  G --> I
```

_A replica adds eventual-consistency lag, a cache adds an invalidation problem, partitioning adds operational complexity — pick by the bottleneck the plan shows, not by reflex._

## Capability map (dated — verify at build)

| Capability | 2026 state `[verify-at-build]` | Notes |
|---|---|---|
| PostgreSQL | GA, current major | Leaned-on here; principles port |
| CREATE INDEX CONCURRENTLY | GA | Online index without long lock |
| ADD CONSTRAINT NOT VALID + VALIDATE | GA | Add FK/CHECK without long lock |
| Partial / covering (INCLUDE) / GIN indexes | GA | Match to predicate |
| PgBouncer / built-in pooling | mature | Size to workload |
| Logical + physical replication | GA | Read replicas eventually consistent |
| PITR | GA (managed + self) | Test the restore |
