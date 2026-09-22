// ---------------------------------------------------------------------------
// CSV export route (FORGE dashboard-top1pct P2-14, 2026-09-03; hardened
// after mandatory security review the same session — see this file's git
// history / the plugin CHANGELOG for the full finding list). Mechanism 2 of
// knowledge/dashboard-export-and-delivery-2026.md — a server-side,
// tenant-scoped export of ROW-LEVEL dimensional data (not just the
// dashboard's aggregate measures, which is a materially different query
// shape needing its own denial test — see
// templates/cube-denial-test-harness/tests/cross-tenant-denial.test.ts's
// "export-path denial" block).
//
// THE ONE RULE THIS FILE EXISTS TO ENFORCE (see best-practices/export-runs-
// under-the-viewer-scope-never-a-service-identity.md): tenantId comes ONLY
// from the server-verified session. Token minting and rate limiting are
// shared with ../cube-token/route.ts via lib/mint-cube-token.ts and
// lib/rate-limiter.ts — the export route uses its OWN, tighter rate-limit
// ceiling (this is not a per-widget operation) and its own limiter
// instance, but the same underlying mechanism, so a future fix to either
// lands once rather than needing to be re-applied per route.
// ---------------------------------------------------------------------------

import { NextResponse } from "next/server";
import cubejs from "@cubejs-client/core";
import { getSession } from "@/lib/session";
import { mintCubeToken, SigningKeyUnusableError } from "@/lib/mint-cube-token";
import { createRateLimiter } from "@/lib/rate-limiter";
import { toCsvRow } from "@/lib/csv";

const EXPORT_TOKEN_EXPIRES_IN_SECONDS = 300; // short-lived — this token exists only for this request
const ROW_LIMIT = 5000;

// Tighter ceiling than ../cube-token/route.ts's 30/min: an export runs a
// 5000-row warehouse query, not a ~1ms HMAC sign, and an uncapped export
// endpoint is a metered-spend / connection-pool-exhaustion vector (security
// review, P2-14) — the limiter belongs on the expensive route at least as
// much as the cheap one.
const RATE_LIMIT_MAX_REQUESTS = 5;
const RATE_LIMIT_WINDOW_MS = 60_000;
const limiter = createRateLimiter(RATE_LIMIT_MAX_REQUESTS, RATE_LIMIT_WINDOW_MS);

const NO_STORE_HEADERS = { "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff" };

// A GET route Next.js otherwise tries to statically prerender at build time
// (page.tsx needed the identical fix, for the identical reason: calling
// getSession() with no request in flight during the build is exactly what
// the seam correctly rejects). Caught by `npm run build` actually failing —
// not assumed.
export const dynamic = "force-dynamic";

function jsonError(message: string, status: number) {
  return NextResponse.json({ error: message }, { status, headers: NO_STORE_HEADERS });
}

export async function GET() {
  const session = await getSession();

  if (!session?.tenantId || !session?.userId) {
    // See ../cube-token/route.ts's identical branch for why this is
    // defensive-but-currently-unreachable against the placeholder seam.
    return jsonError("export: no authenticated session.", 401);
  }

  if (limiter.isLimited(session.userId)) {
    return jsonError("export: rate limit exceeded.", 429);
  }

  let token: string;
  try {
    token = mintCubeToken(session.tenantId, session.userId, EXPORT_TOKEN_EXPIRES_IN_SECONDS);
  } catch (err) {
    if (err instanceof SigningKeyUnusableError) {
      return jsonError(`export: ${err.message}`, 500);
    }
    throw err;
  }

  const cubeApi = cubejs(token, {
    apiUrl: process.env.NEXT_PUBLIC_CUBE_API_URL || "http://localhost:4000/cubejs-api/v1",
  });

  // Row-level dimensional query — deliberately NOT the dashboard's aggregate
  // measures shape. An export is expected to hand back the underlying rows,
  // not just a rolled-up KPI, which is exactly why this query shape needs
  // its own denial test rather than inheriting the dashboard's.
  const asOf = new Date().toISOString();
  let resultSet;
  try {
    resultSet = await cubeApi.load({
      dimensions: ["orders.id", "orders.order_date", "orders.customer_id"],
      measures: ["orders.total_revenue"],
      order: { "orders.order_date": "desc" },
      limit: ROW_LIMIT,
    });
  } catch (err) {
    // Security review (P2-14): Cube's error text can carry generated SQL,
    // cube/table/column names, and (on a downstream failure) raw Postgres
    // error text including offending literal values — a schema/data
    // disclosure channel if echoed verbatim to an authenticated viewer.
    // Log server-side, return a fixed message + correlation id instead.
    const ref = crypto.randomUUID();
    console.error(`export ${ref}: Cube query failed`, err);
    return jsonError(`export: query failed (ref: ${ref})`, 502);
  }

  const rows = resultSet.tablePivot();
  const truncated = rows.length >= ROW_LIMIT;
  const header = ["order_id", "order_date", "customer_id", "total_revenue"];

  // Provenance block — matches the on-screen widget footer discipline
  // (dashboard-set-data-freshness-slas.md): source, tenant, as-of. Routed
  // through toCsvRow (security review, P2-14) rather than raw template-
  // literal interpolation — session.tenantId is consumer-supplied via the
  // session seam and was previously written to the file with zero escaping.
  const lines: string[] = [
    toCsvRow([
      "# source",
      "orders.total_revenue, orders.id, orders.order_date, orders.customer_id",
    ]),
    toCsvRow(["# tenant", session.tenantId]),
    toCsvRow(["# as_of", asOf]),
    ...(truncated
      ? [
          toCsvRow([
            "# truncated",
            `true (row cap ${ROW_LIMIT} reached; this export is not complete)`,
          ]),
        ]
      : []),
    toCsvRow(header),
    ...rows.map((r) =>
      toCsvRow([
        r["orders.id"],
        r["orders.order_date"],
        r["orders.customer_id"],
        r["orders.total_revenue"],
      ]),
    ),
  ];

  // Audit trail (security review, P2-14): a bulk tenant-data export is
  // exactly the event a client asks about after an incident ("who pulled
  // our customer list, and when?") — the dashboard's own read path is at
  // least reconstructable from Cube's query log; a one-shot CSV download
  // was not, before this line. A real engagement routes this to the host
  // app's audit sink instead of stdout.
  console.log(
    JSON.stringify({
      event: "dashboard.export",
      userId: session.userId,
      tenantId: session.tenantId,
      rowCount: rows.length,
      asOf,
    }),
  );

  return new NextResponse(lines.join("\r\n") + "\r\n", {
    status: 200,
    headers: {
      "Content-Type": "text/csv; charset=utf-8",
      "Content-Disposition": `attachment; filename="dashboard-export-${asOf.slice(0, 10)}.csv"`,
      ...NO_STORE_HEADERS,
    },
  });
}
