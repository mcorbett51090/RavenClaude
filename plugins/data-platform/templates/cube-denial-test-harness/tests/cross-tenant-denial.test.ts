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
});
