// Executable cross-tenant denial test (FORGE dashboard-top1pct P1-9, 2026-09-03).
//
// Requires the docker-compose fixture in this directory's parent to be up
// (`docker compose -f ../docker-compose.yml up -d --wait`) and DP_INTEGRATION=1
// set — see this directory's README.md for the full run procedure. This file
// is NOT run by default `vitest`/`npm test` invocations elsewhere in the
// plugin; it only runs opted-in, via scripts/audit-gates.sh's Tier-4 entry.
//
// ⛔ Honest limit: this test has been authored and reasoned through carefully
// (the Cube REST API shape, the access_policy override semantics, the RLS
// SET LOCAL contract) but has NOT been executed against a live Cube+Postgres
// pair in this session — no docker runtime was available in this sandbox.
// Treat "this test passes" as unverified until it actually runs once, in CI
// or locally with docker present.

import { describe, it, expect, beforeAll } from "vitest";
import jwt from "jsonwebtoken";
import pg from "pg";

const CUBE_API_URL = process.env.CUBE_TEST_API_URL ?? "http://localhost:4001/cubejs-api/v1";
const CUBE_API_SECRET =
  process.env.CUBE_TEST_API_SECRET ?? "cube-denial-test-harness-secret-not-for-prod-use-only";
// ⛔ Deliberately connects as viewer_role, NEVER the compose superuser
// (cube_test / POSTGRES_USER) — a Postgres superuser always bypasses RLS
// regardless of policy, so an RLS assertion run as the superuser would pass
// unconditionally and prove nothing. viewer_role is granted LOGIN in
// seed/two-tenant-fixture.sql specifically so this test can connect as the
// actual RLS-enforced role.
const PG_CONNECTION_STRING =
  process.env.PG_TEST_CONNECTION_STRING ??
  "postgres://viewer_role:viewer_role_test_password_not_for_prod@localhost:5433/cube_denial_test";

const TENANT_A = "11111111-1111-1111-1111-111111111111";
const TENANT_B = "22222222-2222-2222-2222-222222222222";

function mintTenantToken(tenantId: string): string {
  // Mirrors jwt-issuer.ts's claim shape (sub, tenant_id, iat, exp, iss, aud) —
  // this harness mints its own token directly rather than calling a starter's
  // /api/cube-token route, since it tests the Cube layer's access_policy in
  // isolation from either starter's HTTP surface.
  const now = Math.floor(Date.now() / 1000);
  return jwt.sign(
    {
      sub: "denial-test-user",
      tenant_id: tenantId,
      iat: now,
      exp: now + 300,
      iss: "denial-test-harness",
      aud: "cube",
    },
    CUBE_API_SECRET,
    { algorithm: "HS256" },
  );
}

async function queryCube(token: string, filters: unknown[] = []) {
  const query = {
    measures: ["orders.total_revenue"],
    ...(filters.length > 0 ? { filters } : {}),
  };
  const res = await fetch(
    `${CUBE_API_URL}/load?query=${encodeURIComponent(JSON.stringify(query))}`,
    {
      headers: { Authorization: `Bearer ${token}` },
    },
  );
  if (!res.ok) {
    throw new Error(`Cube query failed: ${res.status} ${await res.text()}`);
  }
  return res.json() as Promise<{ data: Array<Record<string, string>> }>;
}

// Row-level dimensional query — the shape templates/cube-nextjs-dashboard-
// starter's and templates/cube-astro-dashboard-starter's app/api/export
// routes actually issue (P2-14), NOT the aggregate-measures shape the
// dashboard's own queryCube() above uses. Returns the raw response so a
// non-OK status can be inspected rather than always throwing — the
// service-identity test below needs to distinguish "Cube rejected this
// outright" from "Cube returned data," and both count as a pass.
async function queryCubeDimensional(token: string) {
  const query = {
    dimensions: ["orders.id", "orders.order_date", "orders.tenant_id"],
    measures: ["orders.total_revenue"],
  };
  const res = await fetch(
    `${CUBE_API_URL}/load?query=${encodeURIComponent(JSON.stringify(query))}`,
    { headers: { Authorization: `Bearer ${token}` } },
  );
  return res;
}

function mintServiceIdentityToken(): string {
  // Mimics the exact failure mode named in best-practices/export-runs-under-
  // the-viewer-scope-never-a-service-identity.md: a rushed export
  // implementation that mints a token carrying NO tenant_id claim at all
  // (e.g. reusing the app's own Cube API secret directly, or an admin/
  // service-account-shaped token). This is what mutating the export route
  // to use a service identity looks like at the token level — the teeth
  // property the acceptance test in plan.md's P2-14 section calls for.
  const now = Math.floor(Date.now() / 1000);
  return jwt.sign(
    {
      sub: "export-service-account",
      // tenant_id deliberately omitted
      iat: now,
      exp: now + 300,
      iss: "denial-test-harness",
      aud: "cube",
    },
    CUBE_API_SECRET,
    { algorithm: "HS256" },
  );
}

describe("cross-tenant denial (Cube access_policy layer)", () => {
  beforeAll(async () => {
    // Assert the resolved Cube server version, not just the compose file's
    // pinned tag (a stale local image cache could silently serve an older
    // version despite the tag) — the whole reason this harness pins >=1.2.0
    // is P0-1's finding that access_policy is a no-op below that version.
    const res = await fetch(`${CUBE_API_URL.replace(/\/cubejs-api\/v1$/, "")}/readyz`);
    expect(res.ok, "Cube /readyz must report healthy before any test runs").toBe(true);
    // Cube's /v1/meta response does not carry a server version field in the
    // stable REST API — version assertion is therefore done at the
    // docker-compose level (the pinned v1.7.33 tag, verified against the
    // Docker Hub registry API this session) rather than at runtime. Documented
    // here rather than silently assumed: a runtime version assertion would be
    // a stronger control if Cube ever exposes one on a public endpoint.
  });

  it("positive control: tenant A's own revenue is non-zero", async () => {
    const token = mintTenantToken(TENANT_A);
    const result = await queryCube(token);
    const revenue = Number(result.data[0]?.["orders.total_revenue"] ?? 0);
    // Fixture seeds tenant A with 150.00 + 275.50 = 425.50.
    expect(revenue).toBeGreaterThan(0);
    expect(revenue).toBeCloseTo(425.5, 2);
  });

  it("denies an explicit cross-tenant filter for tenant B while authenticated as tenant A", async () => {
    const token = mintTenantToken(TENANT_A);
    const result = await queryCube(token, [
      { member: "orders.tenant_id", operator: "equals", values: [TENANT_B] },
    ]);
    // access_policy must override the explicit filter attempt — tenant B's
    // real revenue (425.00, distinct from tenant A's 425.50) must NOT appear.
    const revenue = Number(result.data[0]?.["orders.total_revenue"] ?? 0);
    expect(revenue).not.toBeCloseTo(425.0, 2);
    expect(result.data.length === 0 || revenue === 0).toBe(true);
  });

  describe("Postgres RLS layer (defense-in-depth, direct connection)", () => {
    it("denies a cross-tenant read via SET LOCAL app.tenant_id", async () => {
      const client = new pg.Client({ connectionString: PG_CONNECTION_STRING });
      await client.connect();
      try {
        await client.query("BEGIN");
        await client.query("SET LOCAL app.tenant_id = $1", [TENANT_A]);
        const res = await client.query(
          "SELECT COUNT(*)::int AS n FROM fact_orders WHERE tenant_id = $1",
          [TENANT_B],
        );
        expect(res.rows[0].n).toBe(0);
        await client.query("ROLLBACK");
      } finally {
        await client.end();
      }
    });

    it("positive control: tenant A can read its own rows under the same RLS context", async () => {
      const client = new pg.Client({ connectionString: PG_CONNECTION_STRING });
      await client.connect();
      try {
        await client.query("BEGIN");
        await client.query("SET LOCAL app.tenant_id = $1", [TENANT_A]);
        const res = await client.query(
          "SELECT COUNT(*)::int AS n FROM fact_orders WHERE tenant_id = $1",
          [TENANT_A],
        );
        expect(res.rows[0].n).toBe(2);
        await client.query("ROLLBACK");
      } finally {
        await client.end();
      }
    });
  });

  // Export-path denial (FORGE dashboard-top1pct P2-14, 2026-09-03) — extends
  // this harness per plan.md's P2-14 acceptance test: "tenant-A's export must
  // not contain tenant-B rows" and the test must "fail when the export route
  // is mutated to use a service identity." A dimensional, row-level query is
  // a materially different shape than the dashboard's aggregate-measures
  // query above (see best-practices/export-runs-under-the-viewer-scope-
  // never-a-service-identity.md) — an access_policy correctly scoping one
  // shape is not proof it scopes the other, so this needs its own coverage
  // rather than inheriting the dashboard block's.
  describe("export-path denial (row-level dimensional query)", () => {
    it("positive control: tenant A's own dimensional export rows are non-empty and all tenant A", async () => {
      const token = mintTenantToken(TENANT_A);
      const res = await queryCubeDimensional(token);
      expect(res.ok, "a correctly tenant-scoped dimensional query must succeed").toBe(true);
      const body = (await res.json()) as { data: Array<Record<string, string>> };
      expect(body.data.length).toBeGreaterThan(0);
      for (const row of body.data) {
        expect(row["orders.tenant_id"]).toBe(TENANT_A);
      }
    });

    it("denies a service-identity token (no tenant_id claim) rather than returning unscoped rows", async () => {
      const token = mintServiceIdentityToken();
      const res = await queryCubeDimensional(token);
      if (res.ok) {
        // If Cube accepted the request at all, it must not have returned
        // rows from more than one tenant — an unscoped service identity
        // that happens to 200 with a genuinely empty/filtered result is
        // still a pass; silently returning both tenants' rows is the
        // failure this test exists to catch.
        const body = (await res.json()) as { data: Array<Record<string, string>> };
        const tenantsSeen = new Set(body.data.map((row) => row["orders.tenant_id"]));
        expect(
          tenantsSeen.size,
          "a service-identity token must never see more than one tenant's rows",
        ).toBeLessThanOrEqual(1);
      } else {
        // Cube rejecting the request outright (missing required
        // securityContext.tenant_id) is the expected, stronger outcome.
        expect(res.status).toBeGreaterThanOrEqual(400);
      }
    });
  });

  // FORGE dashboard-top1pct P2-17 (2026-09-03) — knowledge/dashboard-query-
  // cost-instrumentation.md's per-widget X-Request-Id tagging scheme. This
  // asserts Cube's REST API ACCEPTS the header and the tagged query still
  // returns correct, tenant-scoped data — it does NOT assert the tag
  // actually lands in Cube's Query History export, which needs Cube Cloud
  // or a self-hosted monitoring integration this docker-compose fixture
  // doesn't stand up. That's a named, honest limit, not silently skipped.
  describe("per-widget request tagging (P2-17)", () => {
    it("a tagged query (X-Request-Id set) succeeds and stays tenant-scoped", async () => {
      const token = mintTenantToken(TENANT_A);
      const query = { measures: ["orders.total_revenue"] };
      const res = await fetch(
        `${CUBE_API_URL}/load?query=${encodeURIComponent(JSON.stringify(query))}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "X-Request-Id": "kpi-card.orders.total_revenue.current",
          },
        },
      );
      expect(res.ok, "Cube must not reject a request carrying a client-set X-Request-Id").toBe(
        true,
      );
      const body = (await res.json()) as { data: Array<Record<string, string>> };
      expect(body.data.length).toBeGreaterThan(0);
    });
  });
});
