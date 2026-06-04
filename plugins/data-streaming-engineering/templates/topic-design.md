# Topic design

| Topic | Key (ordering) | Partitions | Retention | Schema (registry) |
|---|---|---|---|---|
| orders | order_id | 12 | 7d | orders-value v2 (backward-compat) |
| order-state | order_id | 12 | compacted | order-state v1 |

- Order is per-partition; key = ordering guarantee.
- Schema evolution: additive only; compatibility = backward.
