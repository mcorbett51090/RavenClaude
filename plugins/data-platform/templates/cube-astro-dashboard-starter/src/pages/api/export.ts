// ---------------------------------------------------------------------------
// CSV export route (FORGE dashboard-top1pct P2-14, 2026-09-03; hardened
// after mandatory security review the same session) — Astro APIRoute
// equivalent of the Next.js starter's app/api/export/route.ts. Same
// security posture: tenantId comes ONLY from the server-verified session
// (never request input); token minting and rate limiting are shared with
// api/cube-token.ts via lib/mint-cube-token.ts and lib/rate-limiter.ts, but
// this route uses its OWN, tighter rate-limit ceiling.
// ---------------------------------------------------------------------------

import type { APIRoute } from "astro";
import cubejs from "@cubejs-client/core";
import { getSession } from "@/lib/session";
import { mintCubeToken, SigningKeyUnusableError } from "@/lib/mint-cube-token";
import { createRateLimiter } from "@/lib/rate-limiter";
import { toCsvRow } from "@/lib/csv";

export const prerender = false; // must run per-request, not at build time

const EXPORT_TOKEN_EXPIRES_IN_SECONDS = 300;
const ROW_LIMIT = 5000;

// Tighter ceiling than api/cube-token.ts's 30/min — an export runs a
// 5000-row warehouse query, not a ~1ms HMAC sign (security review, P2-14).
const RATE_LIMIT_MAX_REQUESTS = 5;
const RATE_LIMIT_WINDOW_MS = 60_000;
const limiter = createRateLimiter(RATE_LIMIT_MAX_REQUESTS, RATE_LIMIT_WINDOW_MS);

const NO_STORE = { "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff" };

function jsonError(message: string, status: number) {
  return new Response(JSON.stringify({ error: message }), {
    status,
    headers: { "Content-Type": "application/json", ...NO_STORE },
  });
}

export const GET: APIRoute = async () => {
  const session = await getSession();

  if (!session?.tenantId || !session?.userId) {
    // Defensive branch (security review, P2-14): lib/session.ts's
    // placeholder always throws rather than returning a nullish session, so
    // this is currently unreachable — but a real getSession() wiring
    // commonly RETURNS null on no session rather than throwing. Fail closed
    // explicitly rather than letting an unscoped call reach the JWT mint.
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
    apiUrl: process.env.PUBLIC_CUBE_API_URL || "http://localhost:4000/cubejs-api/v1",
  });

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
    // cube/table/column names, and raw Postgres error text — a schema/data
    // disclosure channel if echoed verbatim. Log server-side, return a
    // fixed message + correlation id instead.
    const ref = crypto.randomUUID();
    console.error(`export ${ref}: Cube query failed`, err);
    return jsonError(`export: query failed (ref: ${ref})`, 502);
  }

  const rows = resultSet.tablePivot();
  const truncated = rows.length >= ROW_LIMIT;
  const header = ["order_id", "order_date", "customer_id", "total_revenue"];

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

  // Audit trail (security review, P2-14) — see the Next.js starter's
  // identical block for the full rationale.
  console.log(
    JSON.stringify({
      event: "dashboard.export",
      userId: session.userId,
      tenantId: session.tenantId,
      rowCount: rows.length,
      asOf,
    }),
  );

  return new Response(lines.join("\r\n") + "\r\n", {
    status: 200,
    headers: {
      "Content-Type": "text/csv; charset=utf-8",
      "Content-Disposition": `attachment; filename="dashboard-export-${asOf.slice(0, 10)}.csv"`,
      ...NO_STORE,
    },
  });
};
