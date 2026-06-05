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

## Decision Tree: Which transaction isolation level?

**When this applies:** You are opening a transaction and need to decide which isolation level to use. Typically triggered when a race condition, lost update, or phantom-read anomaly is suspected or needs to be prevented by design.

**Last verified:** 2026-06-05 against PostgreSQL documentation on transaction isolation.

```mermaid
flowchart TD
    START[A transaction that reads and writes] --> Q1{Does the transaction make decisions based on data it reads?}
    Q1 -->|No - blind write only| RC[READ COMMITTED is sufficient]
    Q1 -->|Yes - reads affect the write| Q2{Are phantom rows from concurrent inserts a problem?}
    Q2 -->|No - only updating rows known at start| Q3{Do you need to prevent lost updates?}
    Q3 -->|Yes - optimistic: detect and retry| RR[REPEATABLE READ - snapshot, retry on conflict]
    Q3 -->|Yes - pessimistic: lock immediately| SEL4UP[SELECT FOR UPDATE in READ COMMITTED]
    Q3 -->|No - last write wins is fine| RC
    Q2 -->|Yes - phantom inserts could corrupt the result| SERIAL[SERIALIZABLE - full snapshot isolation]
    SERIAL --> Q4{High contention expected?}
    Q4 -->|Yes| RETRY[Design for serialization failure retry]
    Q4 -->|No| DONE[SERIALIZABLE is correct here]
```

**Rationale per leaf:**
- *READ COMMITTED* — the PostgreSQL default; sees the latest committed version of each row; correct for most blind writes and simple reads.
- *REPEATABLE READ* — the transaction sees a snapshot from its start time; concurrent writes to the same rows fail with a serialization error you retry; good for optimistic patterns.
- *SELECT FOR UPDATE* — pessimistic lock; prevents concurrent updates without raising the isolation level; correct for "read-then-update" in READ COMMITTED.
- *SERIALIZABLE* — full snapshot isolation; prevents phantoms and write skew; the highest blast radius (retry on conflict); required when correctness depends on the total view of the dataset.

**Tradeoffs summary:**

| Method | Cost / time | Blast radius | Approval gate? | Use when |
|---|---|---|---|---|
| READ COMMITTED | Minimal | None | None | Default; blind writes or simple reads |
| SELECT FOR UPDATE | Low | Locks rows | None | Pessimistic read-then-update |
| REPEATABLE READ | Low-medium | Retry on conflict | None | Optimistic concurrent update |
| SERIALIZABLE | Medium | Retry on conflict | None | Phantom prevention or write skew |

## Decision Tree: When to add a partial index?

**When this applies:** You are adding an index to speed up a query and the query always includes a filter that selects a small subset of rows.

**Last verified:** 2026-06-05 against PostgreSQL documentation on partial indexes.

```mermaid
flowchart TD
    START[A slow query with a WHERE clause] --> Q1{Does the WHERE clause always include a selective filter on a stable value?}
    Q1 -->|No - filter varies across callers| STANDARD[Standard B-tree on the filtered column]
    Q1 -->|Yes - e.g. status = open, deleted_at IS NULL| Q2{What fraction of the table matches the filter?}
    Q2 -->|Small fraction - under 20 percent| PARTIAL[Partial index - include the WHERE clause in the index definition]
    Q2 -->|Large fraction - most rows match| STANDARD
    PARTIAL --> Q3{Are the indexed columns also in the SELECT list?}
    Q3 -->|Yes| COVERING[Partial covering index - add INCLUDE columns to avoid heap fetch]
    Q3 -->|No| DONE[Partial index is sufficient]
    STANDARD --> Q4{Does the planner choose the index?}
    Q4 -->|No| ANALYZE[Run ANALYZE then re-check - may be a stats issue]
    Q4 -->|Yes| DONE
```

**Rationale per leaf:**
- *Partial index* — an index with a `WHERE` clause that matches the query's filter; smaller, faster to build, and cheaper to maintain than a full-table index on the same column.
- *Partial covering index* — adds `INCLUDE` columns so the query can be answered entirely from the index without a heap fetch; maximum read speed, slightly higher write and storage cost.
- *Standard B-tree* — when the filter is not selective enough to justify a partial index, a full index is the correct choice.

**Tradeoffs summary:**

| Method | Cost / time | Blast radius | Approval gate? | Use when |
|---|---|---|---|---|
| Standard B-tree | Low | Full index maintained | None | Filter varies or covers most rows |
| Partial index | Low-medium | Smaller, targeted | None | Selective stable filter, small subset |
| Partial covering | Medium | Wider index entry | Schema review | Read-heavy, avoid heap fetch |

## Decision Tree: Add a NOT NULL column to a live table — how?

**When this applies:** You need to add a column with a NOT NULL constraint to a table that is receiving concurrent writes. A naive ALTER TABLE will take a long lock and potentially block reads and writes for minutes on a large table.

**Last verified:** 2026-06-05 against PostgreSQL documentation on ALTER TABLE and lock behavior.

```mermaid
flowchart TD
    START[Add NOT NULL column to a live table] --> Q1{Does the column need a non-trivial default value that must be backfilled?}
    Q1 -->|No - NULL is the initial value and app will always write it| Q2{Is PostgreSQL 11 or later?}
    Q2 -->|Yes| IMMDEFAULT[ALTER TABLE ADD COLUMN ... NOT NULL DEFAULT literal - instant in PG11+]
    Q2 -->|No - older PG| EXPAND[Add as nullable first, then backfill, then set NOT NULL]
    Q1 -->|Yes - computed default or FK-derived value| EXPAND
    EXPAND --> STEP1[Step 1 - ALTER TABLE ADD COLUMN new_col TYPE NULL]
    STEP1 --> STEP2[Step 2 - backfill in batches - see backfill rule]
    STEP2 --> STEP3[Step 3 - ALTER TABLE ADD CONSTRAINT NOT NULL NOT VALID]
    STEP3 --> STEP4[Step 4 - VALIDATE CONSTRAINT - lightweight lock]
    IMMDEFAULT --> DONE[Deploy in one migration]
    STEP4 --> DONE
```

**Rationale per leaf:**
- *PG11+ instant default* — PostgreSQL 11 rewrote how constant defaults are stored; `ADD COLUMN ... DEFAULT constant NOT NULL` no longer rewrites the table; it is instant and safe.
- *Expand/contract for computed defaults* — when the default requires a backfill (a function, a JOIN-derived value), the expand/contract sequence spreads the change across safe, non-locking steps.
- *NOT VALID then VALIDATE* — `ADD CONSTRAINT NOT VALID` adds the constraint for new rows immediately without checking existing rows; `VALIDATE CONSTRAINT` checks existing rows under a ShareUpdateExclusiveLock (the lightest write-compatible lock) rather than an AccessExclusiveLock.

**Tradeoffs summary:**

| Method | Cost / time | Blast radius | Approval gate? | Use when |
|---|---|---|---|---|
| PG11+ instant default | Minimal | None | None | Constant default, PG11+ |
| Expand/contract | High - multi-deploy | Non-locking | Release coordination | Computed default or pre-PG11 |
