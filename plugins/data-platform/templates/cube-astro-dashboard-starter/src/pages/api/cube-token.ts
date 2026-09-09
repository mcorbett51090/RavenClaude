// ---------------------------------------------------------------------------
// Server-side Cube-audience JWT mint — Astro APIRoute. Token minting + rate
// limiting are now shared with api/export.ts via lib/mint-cube-token.ts and
// lib/rate-limiter.ts (factored out FORGE dashboard-top1pct P2-14,
// 2026-09-03, after security review found the two routes' hand-duplicated
// copies had already drifted on the export route's first draft).
// ---------------------------------------------------------------------------

import type { APIRoute } from "astro";
import { getSession } from "@/lib/session";
import { mintCubeToken, SigningKeyUnusableError } from "@/lib/mint-cube-token";
import { createRateLimiter } from "@/lib/rate-limiter";

export const prerender = false; // must run per-request, not at build time

const DEFAULT_EXPIRES_IN_SECONDS = 900; // 15 min
const RATE_LIMIT_MAX_REQUESTS = 30;
const RATE_LIMIT_WINDOW_MS = 60_000;

const limiter = createRateLimiter(RATE_LIMIT_MAX_REQUESTS, RATE_LIMIT_WINDOW_MS);
const NO_STORE = { "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff" };

function jsonResponse(body: unknown, status: number) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json", ...NO_STORE },
  });
}

export const POST: APIRoute = async () => {
  // tenantId + userId come from the SERVER-VERIFIED session — never from
  // the request body. This route intentionally reads no input.
  const session = await getSession();

  if (!session?.tenantId || !session?.userId) {
    // Defensive branch (security review, P2-14) — see api/export.ts's
    // identical branch for why this guards a currently-unreachable case
    // against the placeholder seam's future real wiring.
    return jsonResponse({ error: "cube-token: no authenticated session." }, 401);
  }

  if (limiter.isLimited(session.userId)) {
    return jsonResponse({ error: "cube-token: rate limit exceeded." }, 429);
  }

  let token: string;
  try {
    token = mintCubeToken(session.tenantId, session.userId, DEFAULT_EXPIRES_IN_SECONDS);
  } catch (err) {
    if (err instanceof SigningKeyUnusableError) {
      return jsonResponse({ error: `cube-token: ${err.message}` }, 500);
    }
    throw err;
  }

  return jsonResponse({ token, expiresIn: DEFAULT_EXPIRES_IN_SECONDS }, 200);
};
