# Cross-boundary denial test procedure (documented, not yet executed in CI)

Per data-platform CLAUDE.md §3 #3: *"Every stack ships a cross-boundary denial test
appropriate to its enforcement layer. No test, no merge."* This scaffold's enforcement
layer is Cube's `access_policy` (see `../../cube-schema-starter.yml`), backstopped by
Postgres RLS if Cube connects with a tenant-aware role (see
`../../rls-cross-tenant-test.sql` for that layer's own test).

**Honest status: this is a procedure, not a passing CI check.** Running it requires a live
Cube instance with `cube-schema-starter.yml` loaded against seeded multi-tenant data — this
scaffold provisions neither. Wire it into your engagement's CI once both exist.

## Procedure

1. Seed two tenants (`tenant-A`, `tenant-B`) in the underlying Postgres database per
   `../../database-schema-starter.sql`, each with at least one `fact_orders` row.
2. Mint a JWT via `POST /api/cube-token` **as tenant-A** (i.e. with `getSession()` wired to
   return `tenant-A`'s real session).
3. Using that token, query Cube directly for `orders.total_revenue` with an **explicit**
   filter for `tenant-B`:

   ```
   POST {CUBE_API_URL}/load
   Authorization: Bearer <tenant-A token>
   {
     "query": {
       "measures": ["orders.total_revenue"],
       "filters": [{ "member": "orders.tenant_id", "operator": "equals", "values": ["tenant-B"] }]
     }
   }
   ```

4. **Expected result: empty / zero, not tenant-B's real revenue.** `access_policy` in
   `cube-schema-starter.yml` must override the explicit filter attempt — this is exactly the
   acceptance criterion documented at the bottom of that file ("access_policy overrides
   explicit filter"). If tenant-B's real data comes back, the access policy is misconfigured
   or absent — stop and fix it before this scaffold goes anywhere near production data.

## Automating this

**Done (FORGE dashboard-top1pct P1-9, 2026-09-03):** `../../cube-denial-test-harness/` is the
executable version of the steps above — a docker-compose-backed Cube (pinned `v1.7.33`) +
Postgres fixture with a `vitest` test asserting the positive control (tenant A's own revenue
is non-zero) and the denial (tenant A cannot see tenant B's revenue, at both the Cube
`access_policy` layer and the Postgres RLS layer). It is opt-in (`DP_INTEGRATION=1`, needs
docker — never in the default CI run) and its own README states honestly that it has not yet
been executed against a live Cube+Postgres pair (no docker runtime was available in the
session that built it) — the reasoning above about a false-green script still applies until
that first real run happens. This procedure document stays as the authoritative manual
fallback for anyone who can't or doesn't want to run the harness.
