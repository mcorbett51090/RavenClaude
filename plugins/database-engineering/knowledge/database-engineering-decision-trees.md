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
