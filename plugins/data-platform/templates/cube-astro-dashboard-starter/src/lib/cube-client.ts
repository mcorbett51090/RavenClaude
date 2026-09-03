import cubejs, { type CubeApi } from "@cubejs-client/core";

// One client per distinct request tag (FORGE dashboard-top1pct P2-17,
// 2026-09-03) — see knowledge/dashboard-query-cost-instrumentation.md.
// `CubeApiOptions.headers` is set at CONSTRUCTION time, not per query, so a
// widget-tagged X-Request-Id needs its own client instance per tag rather
// than a shared singleton. Every instance still shares the SAME token cache
// below (they all wrap the same `fetchToken` closure) — no extra token-fetch
// traffic. Same pattern as the Next.js starter's lib/cube-client.ts.
const clientsByTag = new Map<string, CubeApi>();
let cachedToken: string | null = null;
let cachedTokenExpiryMs = 0;

const REFRESH_MARGIN_MS = 60_000; // refetch 60s before actual expiry

async function fetchToken(): Promise<string> {
  const now = Date.now();
  if (cachedToken && now < cachedTokenExpiryMs - REFRESH_MARGIN_MS) {
    return cachedToken;
  }

  const res = await fetch("/api/cube-token", { method: "POST" });
  if (!res.ok) throw new Error(`cube-token fetch failed: ${res.status}`);
  const { token, expiresIn } = await res.json();
  cachedToken = token;
  cachedTokenExpiryMs = now + expiresIn * 1000;
  return token;
}

/**
 * Returns a CubeApi client whose token is fetched from our own
 * /api/cube-token route (never minted client-side) and reused until it's
 * close to expiry.
 *
 * @param requestTag Page+widget identity (e.g. "dashboard.kpi-card.current"),
 *   sent as the `X-Request-Id` header Cube's own docs document for
 *   end-to-end request tracing — how a query in Cube's Query History /
 *   warehouse query log is attributable back to the widget that issued it.
 *   Omit for an untagged/ad-hoc query (falls back to the shared default
 *   client).
 */
export function getCubeClient(requestTag?: string): CubeApi {
  const key = requestTag ?? "__default__";
  const cached = clientsByTag.get(key);
  if (cached) return cached;

  const client = cubejs(fetchToken, {
    apiUrl: import.meta.env.PUBLIC_CUBE_API_URL || "http://localhost:4000/cubejs-api/v1",
    ...(requestTag ? { headers: { "X-Request-Id": requestTag } } : {}),
  });
  clientsByTag.set(key, client);
  return client;
}
