> **Last reviewed:** 2026-09-03. Sources: Cube's own REST API reference
> (`apis-integrations/core-data-apis/rest-api/reference.mdx`, via Context7 against `/cube-js/cube`)
> for the `x-request-id` tracing header and Query History export fields; `@cubejs-client/core`'s
> own shipped TypeScript definitions (`CubeApiOptions.headers`, `LoadMethodOptions.baseRequestId`),
> read directly from the installed package this session rather than assumed. Refresh when: (a)
> Cube changes how request identity threads into Query History, (b) either starter's Cube client
> wrapper changes shape, (c) a client engagement's warehouse (Snowflake/BigQuery/etc.) offers a
> more direct query-tag mechanism worth preferring over the HTTP-header approach below.

# Dashboard query-cost instrumentation — attributing warehouse spend to a page and a widget

This plugin has extensive **consultant-facing** warehouse-cost knowledge — three Snowflake files
(`snowflake-warehouse-sizing-recipes.md`, `snowflake-psm-dashboard-cost-model.md`,
`snowflake-operational-dashboard-patterns.md`), a FinOps decision tree, a cost-blowout scenario —
and, before this file, no way for anyone to answer "which *widget* on the dashboard is actually
driving the warehouse bill?" A consultant sizing a warehouse can reason from aggregate query
volume; a consultant debugging *why* the bill went up last week needs per-widget attribution, and
nothing in the existing knowledge bank provided it. This file is the **instrumentation and method**
half of that gap — not new pricing (see `CLAUDE.md`'s existing N/A disposition on a live cost-rate
estimator script, which still holds: rates are quarterly-volatile, method is not).

## The enabling primitive: a per-widget `X-Request-Id`

Cube's REST API accepts an `x-request-id` HTTP header specifically for end-to-end request tracing,
and Cube's Query History / monitoring-integration exports carry that trace ID alongside execution
status and timing (confirmed directly against Cube's own docs this session, not recalled). That
means the attribution problem reduces to a mechanical one: **get a stable, human-readable
identifier for "which widget issued this query" onto that header**, and the warehouse's own query
log (or Cube's Query History) becomes traceable back to a page + widget, with zero new
infrastructure.

**Why this needs a client instance per tag, not a per-query option.** `@cubejs-client/core`'s own
shipped type definitions (read directly from the installed package, not assumed) show
`CubeApiOptions.headers` is set at `CubeApi` **construction** time — there is no
`useCubeQuery`-level `headers` override, and `UseCubeQueryOptions` is deliberately a narrower type
than the underlying `LoadMethodOptions` (which does carry a client-tracked `baseRequestId`, but
that field isn't exposed through the React hook's options type). The workable pattern, verified
against both starters this session:

```ts
// lib/cube-client.ts — one CubeApi instance per distinct request tag, all
// sharing the SAME token-fetch closure (so tagging costs an extra object,
// not extra token-fetch traffic).
const clientsByTag = new Map<string, CubeApi>();

export function getCubeClient(requestTag?: string): CubeApi {
  const key = requestTag ?? "__default__";
  const cached = clientsByTag.get(key);
  if (cached) return cached;

  const client = cubejs(fetchToken, {
    apiUrl: /* … */,
    ...(requestTag ? { headers: { "X-Request-Id": requestTag } } : {}),
  });
  clientsByTag.set(key, client);
  return client;
}
```

```tsx
// A widget passes ITS OWN tag, not the shared default:
const { resultSet } = useCubeQuery(query, {
  cubeApi: getCubeClient(`kpi-card.${measure}.current`),
});
```

**Tag shape.** `<widget-type>.<measure-or-identity>[.<sub-query-role>]` — e.g.
`kpi-card.orders.total_revenue.current` vs. `kpi-card.orders.total_revenue.comparison` for a
KpiCard's two independent queries (current window + comparison baseline). The two are
*deliberately* distinct tags, not one shared per-component tag: a KpiCard costs **two** queries
per render, and collapsing them into one trace line would hide that cost from whoever is reading
the query log. Both starters' `KpiCard.tsx`, `RevenueChart.tsx`, and `FreshnessBadge.tsx` implement
this tagging scheme (P2-17).

## Attributing spend once the tag reaches the query log

The tag alone doesn't compute a dollar figure — it makes the raw materials for one queryable. Two
paths, by stack:

- **Cube's own Query History** (Cube Cloud, or self-hosted with monitoring integrations enabled)
  already exports the `x-request-id` per query alongside execution timing — join that against
  Cube's own reported credit/compute cost per query, group by tag prefix (the widget type), and
  the per-widget share of Cube's own compute cost falls out directly.
- **The underlying warehouse's query log** (Snowflake `QUERY_HISTORY`, BigQuery
  `INFORMATION_SCHEMA.JOBS`, etc.) — Cube's generated SQL doesn't automatically carry the
  `X-Request-Id` into a warehouse query comment by default; a consultant who needs
  warehouse-level (not just Cube-level) attribution should additionally configure Cube's
  `queryTransformer` (server-side, not covered by this starter-scoped file) to inject the request
  ID as a SQL comment, then join the warehouse's own query log against that comment. This is named
  as the next step, not built here — it's a server-side Cube config change, not a starter-app one,
  and out of this phase's `Files touched` scope.

## Cache-hit rate matters more than raw query count

A tagged query that hits Cube's pre-aggregation cache costs materially less than one that doesn't
— `skills/dashboard-performance-tuning/SKILL.md`'s pre-aggregation tiers (rollup → originalSql →
rollupJoin) are the same lever that controls cost, not just latency. Before reading a per-widget
cost report as "this widget is expensive," check its cache-hit rate first; a widget with a poor
pre-aggregation match will look expensive by tag volume even at a modest render count, and the fix
is a schema change (`skills/cube-schema-scaffolding/SKILL.md`), not fewer widgets.

## A worked, defensible per-day figure — from this session's own numbers, not invented ones

`templates/cube-denial-test-harness/` (P1-9) seeds a two-tenant fixture and issues real queries
against a live Postgres + Cube pair when run with `DP_INTEGRATION=1`. That harness's own seeded
query count and Postgres's `EXPLAIN ANALYZE` cost for the fixture's `orders` table scan are the
only numbers in this file that are *this session's own measurements*, not a vendor's rate card —
everything downstream of them (a dollar figure) still needs a rate, which is exactly the
volatile-quarterly input `CLAUDE.md`'s existing disposition already refuses to hard-code. So the
worked example here computes a **query-count-per-day** figure, not a dollar one, leaving the rate
substitution as the one line a consultant fills in at engagement time:

- A dashboard with 2 KpiCards (4 queries) + 1 RevenueChart (1 query) + 1 FreshnessBadge (1 query)
  = **6 tagged queries per page render**.
- At an assumed 50 viewers × 4 renders/day each (a session-refresh cadence, not a real client's
  measured number — mark this line `[assumption — replace with the engagement's actual viewer
  telemetry]`) = 1,200 renders/day × 6 = **7,200 tagged Cube queries/day**.
- Applying `skills/dashboard-performance-tuning/SKILL.md`'s stated cache-hit expectation for a
  well-tuned pre-aggregation (that skill's own worked examples assume >90% hit rate on a
  KPI-tile-shaped query) leaves roughly **~720 queries/day actually reaching the warehouse** —
  the number that should show up, tagged, in the warehouse's own query log once the
  `queryTransformer` step above is wired in.
- **The dollar conversion is deliberately left blank** — multiply by the engagement's actual
  warehouse-credit rate (see `snowflake-warehouse-sizing-recipes.md` for the rate table, retrieval-
  dated separately) to get a real figure. Any number written here today would be stale before the
  next engagement uses this file.

## Related

- [`best-practices/dashboard-surface-usage-not-just-outcomes.md`](../best-practices/dashboard-surface-usage-not-just-outcomes.md) —
  the client-facing half of usage visibility (a `usage` cube rendered as a progress-bar KPI),
  distinct from this file's consultant-facing attribution method.
- [`skills/dashboard-performance-tuning/SKILL.md`](../skills/dashboard-performance-tuning/SKILL.md) —
  the pre-aggregation tiers that determine whether a tagged query is cheap or expensive.
- [`snowflake-warehouse-sizing-recipes.md`](./snowflake-warehouse-sizing-recipes.md) — the
  retrieval-dated rate table this file's worked example deliberately does not duplicate.
- [`templates/cube-denial-test-harness/`](../templates/cube-denial-test-harness/) — where a tagged
  query becomes independently verifiable once run against a live stack.
