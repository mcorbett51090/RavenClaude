---
scenario_id: 2026-06-05-slow-query-missing-composite-index
contributed_at: 2026-06-05
plugin: database-engineering
product: postgres
product_version: "15"
scope: likely-general
tags: [explain, composite-index, seq-scan, selectivity, sargability]
confidence: high
reviewed: false
---

## Problem

A dashboard query — "the most recent 50 orders for one customer, newest first" — went from snappy to 2–4 seconds as the `orders` table crossed ~40M rows. The query was `WHERE customer_id = $1 AND status = 'open' ORDER BY created_at DESC LIMIT 50`. There was a single-column B-tree on `customer_id`, so the team assumed it was indexed and the slowness was "just table size." `EXPLAIN (ANALYZE, BUFFERS)` told a different story: the planner used the `customer_id` index to find the customer's rows, then did a **bitmap heap scan + a sort** of every one of that customer's ~30k orders to filter `status` and order by `created_at`, discarding all but 50.

## Constraints context

- Read-heavy OLTP table; the same query shape runs thousands of times a minute from the app.
- Write volume is real (new orders insert constantly), so adding indexes is not free — each one is write amplification.
- A few large customers have tens of thousands of orders; the average customer has a handful. The plan that's fine for a small customer is pathological for a whale.
- Postgres 15, default `random_page_cost`, stats fresh (ruled out a stale-stats false alarm with `ANALYZE` first).

## Attempts

- Tried: adding a separate single-column index on `status`. Useless — `status='open'` matches a large fraction of rows, so it's not selective on its own, and the planner correctly ignored it. A non-selective column doesn't deserve its own index.
- Tried: adding an index on `created_at` to "help the ORDER BY." It let one query shape avoid a sort but forced a scan across all customers; the planner wouldn't combine it well with the `customer_id` filter. Wrong column order for this predicate.
- Tried: the **composite index matching the predicate and the sort**: `(customer_id, status, created_at DESC)`. The plan collapsed to a single index range scan — equality on `customer_id` and `status`, then walking `created_at` in index order and stopping at 50. No heap sort, no over-fetch. 2.5 s → ~3 ms.
- Tried (refinement): a **partial** composite `(customer_id, created_at DESC) WHERE status = 'open'` since the dashboard only ever wants open orders. Smaller index, same plan, less write cost on closed-order updates.

## Resolution

**Read the plan, then match one composite index to the predicate's *shape*, not one index per column.** The winning order is: **equality columns first, then the range/sort column last** — `(customer_id, status, created_at DESC)`. That lets a single index serve the `WHERE` (equality on the leading columns) *and* the `ORDER BY ... LIMIT` (the trailing column is already in sorted order, so the planner reads the first 50 and stops).

Why the single-column indexes failed: an index only helps if the query's access is **sargable** against it and the column is **selective**. `customer_id` alone was selective but left a 30k-row sort+filter; `status` alone wasn't selective; `created_at` alone ignored the customer filter. The composite encodes the whole access pattern in one structure.

The trap is "we have an index on `customer_id`, so this is indexed" — being *touched* by an index is not being *served* by one. The plan shows the difference: a `Bitmap Heap Scan` with a `Sort` node above it eating thousands of rows to return 50 is the signature of a missing composite, not a too-big table.

**Action for the next engineer:** before adding any index, run `EXPLAIN (ANALYZE, BUFFERS)` and look for a `Sort` or a large `Rows Removed by Filter` above an index scan. Build **one** composite index ordered `equality → equality → range/sort`, and use a `WHERE` clause to make it partial if the query always filters on a stable value. Verify the new plan is an index scan with the `LIMIT` honored, and confirm the write cost is acceptable.

Cross-reference: the canonical rules are [`../best-practices/match-the-index-to-the-predicate.md`](../best-practices/match-the-index-to-the-predicate.md), [`../best-practices/read-the-plan-before-tuning.md`](../best-practices/read-the-plan-before-tuning.md), and the "Which index (or none)?" + "When to add a partial index?" trees in [`../knowledge/database-engineering-decision-trees.md`](../knowledge/database-engineering-decision-trees.md).
