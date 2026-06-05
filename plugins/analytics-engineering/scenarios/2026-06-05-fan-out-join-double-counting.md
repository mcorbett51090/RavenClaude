---
scenario_id: 2026-06-05-fan-out-join-double-counting
contributed_at: 2026-06-05
plugin: analytics-engineering
product: snowflake
product_version: "unknown"
scope: likely-general
tags: [fan-out, join, grain, double-counting, revenue, semantic-layer]
confidence: high
reviewed: false
---

## Problem

A finance mart `fct_orders_enriched` reported revenue ~18% higher than the source system's own total, and the gap grew month over month. Two dashboards built on the same mart disagreed with each other depending on whether they filtered by shipment carrier. The root cause was a classic **fan-out join**: `orders` (one row per order) was joined to `order_shipments` (one row per *shipment*, and a single order can ship in multiple parcels), and the order-level `order_total` was summed *after* the join — so every order that shipped in three parcels counted its revenue three times.

## Constraints context

- Warehouse: a columnar cloud warehouse (the pattern is dialect-independent — same trap on BigQuery/Redshift/Databricks).
- The mart was the base for a governed `revenue` metric, so the inflated number propagated to every BI tool that consumed the semantic layer — the single-definition guarantee made the *wrong* number consistent everywhere, which is worse than inconsistent: it looked authoritative.
- The grain of `fct_orders_enriched` was never written down. The model name said "orders" but the join had silently changed the grain to one-row-per-order-line-per-shipment.
- A reconciliation against the source total existed but ran monthly, so the drift had been live for weeks before anyone noticed.

## Attempts

- Tried: adding `SELECT DISTINCT` to collapse the duplicate rows. It removed *identical* duplicate rows but not the revenue double-count — the shipment columns differed per row, so the rows weren't identical and the `SUM(order_total)` was still multiplied. `DISTINCT` papers over a grain bug without fixing it.
- Tried: a `unique` test on `order_id` in the mart. It correctly *failed* — which is what surfaced that the grain was no longer one-row-per-order. The failing test was the diagnosis, not a nuisance to silence.
- Tried: aggregating the shipment side to the order grain *before* joining — `order_shipments` collapsed to one row per `order_id` (e.g. `count(*) as shipment_count`, `min(shipped_at) as first_shipped_at`) in an intermediate model, then joined to `orders` one-to-one. Revenue matched the source total exactly. This is the fix.
- Tried (alternative for the cases that genuinely need shipment grain): keeping the fan-out grain but moving the revenue measure to a separate one-row-per-order fact and letting the semantic layer join them as separate entities, so revenue is only ever summed at its native grain.

## Resolution

**State the grain, then never join below it without re-aggregating.** The fix order:

1. **Write the grain in the model's `schema.yml` description** ("one row per order") and back it with a `unique` (or `dbt_utils.unique_combination_of_columns`) test on the grain key. The test turns a silent double-count into a loud CI failure.
2. **Aggregate the many-side to the one-side's grain before joining** — collapse `order_shipments` to one row per `order_id` in an intermediate model, then join one-to-one. Never `SUM` an order-grain measure across a row set that a join has fanned out.
3. **If you genuinely need the finer grain in the same model**, keep the additive measure (revenue) in a fact at *its* native grain and expose the finer-grain attributes as a separate model; let the semantic layer compose them so a measure is only summed at the grain where one row = one event.
4. **Reconcile against the source total in CI**, not monthly — a `relationships`/row-count or a singular reconciliation test catches the drift on the build that introduces it.

The trap is that a fan-out join produces *more rows, all of which look valid*; nothing errors, the numbers are just bigger. The grain declaration plus a grain-key uniqueness test is what converts "plausibly large" into "provably wrong."

**Action for the next engineer:** when a sum is mysteriously high, check the join cardinality before checking the SQL math — count rows before and after each join and confirm the grain key is still unique. The fix is almost always "re-aggregate the many-side to the grain," never "`SELECT DISTINCT`."

Cross-reference: this is the field-note complement to [`../best-practices/state-the-grain-explicitly.md`](../best-practices/state-the-grain-explicitly.md) and [`../best-practices/test-relationships-across-mart-joins.md`](../best-practices/test-relationships-across-mart-joins.md). The semantic-layer propagation angle is [`../best-practices/one-definition-per-metric.md`](../best-practices/one-definition-per-metric.md) — a single definition makes a grain bug uniformly wrong.
