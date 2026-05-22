---
name: cube-schema-scaffolding
description: Scaffold Cube semantic-layer schemas with mandatory `securityContext` baked in for multi-tenant customer-facing dashboards. Includes measure/dimension patterns, pre-aggregation hints, view-level partner-facing query surface, and the cross-boundary denial test. Used by `dashboard-builder` on Case-C productized-SaaS engagements.
---

# Skill: cube-schema-scaffolding

> **Invoked by:** `dashboard-builder` (primary). Also consulted by `ravenclaude-core/security-reviewer` for `access_policy` correctness.
>
> **When to invoke:** scaffolding a new Cube schema for Case C (productized SaaS) or Case B (client deliverable when Cube is the chosen layer). Designing measures + dimensions + pre-aggregations. Authoring `securityContext` policies for multi-tenant scoping.
>
> **Output:** Cube `cubes/` directory scaffold with `securityContext` baked in, measure + dimension authoring, pre-aggregation hints, and cross-boundary denial test pattern.

## When Cube is the right choice

Cube (Apache 2.0 OSS, with Cube Cloud as the managed option) is the strongest semantic layer for:

- **Case C — productized SaaS** dashboards where multiple tenants will query the same data model with row-level scoping
- **Case B — client deliverable** when the engagement requires a *governance layer* between the dashboard and the warehouse (caching, access control, pre-aggregation)
- **Replacing raw-SQL endpoints** in any customer-facing dashboard

Cube is NOT the right choice for:

- Case A (portfolio) — Evidence.dev OSS handles static dashboards more directly
- Case D (pipes only) — no dashboard work
- Single-tenant simple read dashboards on small data — Metabase OSS or Superset against the DB is lighter

## Minimum scaffold

```
project/
├── cube.js                   # Cube server config (or cube-deployment.yml for Cube Cloud)
├── schema/
│   ├── cubes/
│   │   ├── Orders.yml
│   │   ├── Customers.yml
│   │   └── Tenants.yml
│   └── views/
│       └── OrderAnalytics.yml
└── .env                       # CUBEJS_API_SECRET, CUBEJS_DB_*, etc.
```

## Required pieces

### 1. `securityContext` policy on every cube touching tenant-scoped data

```yaml
cubes:
  - name: orders
    sql_table: fact_orders
    measures:
      - name: total_revenue
        sql: amount
        type: sum
      - name: order_count
        sql: id
        type: count
    dimensions:
      - name: tenant_id
        sql: tenant_id
        type: string
      - name: order_date
        sql: order_date
        type: time
    access_policy:
      - role: viewer
        conditions:
          - filter:
              member: orders.tenant_id
              operator: equals
              values:
                - "{ securityContext.tenant_id }"
```

The `access_policy` injects `WHERE tenant_id = '<jwt-claim-tenant_id>'` into every query at plan time, before SQL is generated. The DB connection account is intentionally tenant-blind.

### 2. JWT-claim contract

Cube's `securityContext` is populated from the JWT claims passed in the `Authorization: Bearer <jwt>` header. The JWT issuer ([`./jwt-embed-issuance.md`](jwt-embed-issuance.md)) must include `tenant_id` in its claims.

### 3. Pre-aggregation hints (for production)

```yaml
cubes:
  - name: orders
    pre_aggregations:
      - name: daily_by_tenant
        measures: [total_revenue, order_count]
        dimensions: [tenant_id]
        time_dimension: order_date
        granularity: day
        refresh_key:
          every: 1 hour
        scheduled_refresh: true
```

Pre-aggregations are tenant-aware by including `tenant_id` in dimensions. Cube partitions the pre-agg per tenant; queries scoped by `securityContext.tenant_id` hit the right partition.

### 4. Views for partner-facing surfaces

Views isolate the partner-facing query surface from the underlying cubes. Useful when the dashboard exposes simplified metrics + dimensions, and you want to control what's queryable.

## Cross-boundary denial test (every Cube schema ships one)

```python
# tests/test_cube_tenant_isolation.py
import requests
import jwt
import time

def test_cube_denies_cross_tenant_access():
    # Issue JWT for tenant A
    token_a = jwt.encode({
      "tenant_id": "tenant-A-uuid",
      "exp": int(time.time()) + 300
    }, CUBE_SECRET, algorithm="HS256")

    # Try to filter for tenant B's data
    r = requests.get(
        "http://localhost:4000/cubejs-api/v1/load",
        params={"query": {
            "measures": ["orders.total_revenue"],
            "filters": [{"member": "orders.tenant_id", "operator": "equals", "values": ["tenant-B-uuid"]}]
        }},
        headers={"Authorization": f"Bearer {token_a}"}
    )

    # Cube's securityContext should force tenant_id = tenant-A-uuid
    # The explicit filter for tenant-B is overridden by the access_policy
    data = r.json()["data"]
    assert all(row["orders.tenant_id"] == "tenant-A-uuid" for row in data)
    # Or: no rows for tenant-B
    assert not any(row["orders.tenant_id"] == "tenant-B-uuid" for row in data)
```

This test ships in the engagement's CI; failure means `access_policy` is missing or misconfigured.

## Common pitfalls

- **`access_policy` missing from a cube** — Cube serves whatever the query asks for. Catastrophic for multi-tenant.
- **Pre-aggregation that doesn't include `tenant_id` as a dimension** — pre-agg is shared across tenants; cross-tenant leak.
- **Views without their own `access_policy`** — `access_policy` on the underlying cube doesn't always propagate; verify on each view.
- **`CUBEJS_API_SECRET` hard-coded in source** — env var only; the hook catches inline secrets.
- **JWT verification disabled in dev → forgotten in prod** — `CUBEJS_API_SECRET` must be set in every env; absence = no verification = all queries allowed.
- **Hot-path queries hitting raw warehouse** — if a query bypasses pre-aggs, it bills the underlying warehouse on every viewer interaction. Monitor `requests/sec` per cube.

## Anti-patterns this skill flags

- Cube schema without `access_policy` on a tenant-scoped cube
- Pre-aggregation without `tenant_id` dimension
- `CUBEJS_API_SECRET` in source (use env var)
- Views inheriting access_policy implicitly (verify per view)
- No cross-boundary denial test in the engagement's CI
- Customer-facing dashboard bypassing Cube and hitting raw warehouse directly
- `securityContext` populated client-side (must come from a signed JWT from the host app)
- Cube schema with no measures or only one dimension — under-modeled; the semantic layer's value is composability
- Failing to use views to isolate the partner-facing query surface from the cubes (exposes internal model to clients)

## References

- Knowledge: [`../knowledge/embedded-analytics-landscape-2026.md`](../knowledge/embedded-analytics-landscape-2026.md) — Cube's position in the landscape
- Knowledge: [`../knowledge/multi-tenant-rls-patterns.md`](../knowledge/multi-tenant-rls-patterns.md) — how Cube's access_policy fits the closeness-to-data invariant
- Skill: [`./jwt-embed-issuance.md`](jwt-embed-issuance.md) — JWT claims that populate `securityContext`
- Skill: [`./rls-policy-authoring.md`](rls-policy-authoring.md) — defense-in-depth RLS on the DB behind Cube
- Cube docs: [cube.dev/docs](https://cube.dev/docs/) (current API reference)
- Cube pricing (retrieved 2026-05-21): Free, Starter $40/dev/mo, Premium $80/dev/mo (embedded dashboards), Enterprise custom
