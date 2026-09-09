// ---------------------------------------------------------------------------
// Server-side Cube-audience JWT mint. Token minting + rate limiting are now
// shared with app/api/export/route.ts via lib/mint-cube-token.ts and
// lib/rate-limiter.ts (factored out FORGE dashboard-top1pct P2-14,
// 2026-09-03, after security review found the two routes' hand-duplicated
// copies had already drifted on the export route's first draft).
//
// SECURITY (revised after mandatory security review): responses carry
// Cache-Control: no-store (a JWT is not cacheable content) on every
// response path, and the route applies a per-session rate limit.
// ---------------------------------------------------------------------------

import { NextResponse } from "next/server";
import { getSession } from "@/lib/session";
import { mintCubeToken, SigningKeyUnusableError } from "@/lib/mint-cube-token";
import { createRateLimiter } from "@/lib/rate-limiter";

const DEFAULT_EXPIRES_IN_SECONDS = 900; // 15 min — see lib/mint-cube-token.ts
const MAX_EXPIRES_IN_SECONDS = 1800; // 30 min hard ceiling
const RATE_LIMIT_MAX_REQUESTS = 30;
const RATE_LIMIT_WINDOW_MS = 60_000;

const limiter = createRateLimiter(RATE_LIMIT_MAX_REQUESTS, RATE_LIMIT_WINDOW_MS);
const NO_STORE_HEADERS = { "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff" };

export async function POST() {
  // tenantId + userId come from the SERVER-VERIFIED session — never from
  // the request body. This route intentionally accepts no input.
  const session = await getSession();

  if (!session?.tenantId || !session?.userId) {
    // Defensive branch (security review, P2-14): the current lib/session.ts
    // placeholder always throws rather than returning a nullish session, so
    // this is currently unreachable — but a real getSession() wiring (e.g.
    // NextAuth's getServerSession()) commonly RETURNS null on no session
    // rather than throwing, and the Session type here doesn't force a null
    // check at the call site. Fail closed explicitly rather than letting an
    // unscoped call reach the JWT mint.
    return NextResponse.json(
      { error: "cube-token: no authenticated session." },
      { status: 401, headers: NO_STORE_HEADERS },
    );
  }

  if (limiter.isLimited(session.userId)) {
    return NextResponse.json(
      { error: "cube-token: rate limit exceeded." },
      { status: 429, headers: NO_STORE_HEADERS },
    );
  }

  let token: string;
  try {
    token = mintCubeToken(session.tenantId, session.userId, DEFAULT_EXPIRES_IN_SECONDS);
  } catch (err) {
    if (err instanceof SigningKeyUnusableError) {
      return NextResponse.json(
        { error: `cube-token: ${err.message}` },
        { status: 500, headers: NO_STORE_HEADERS },
      );
    }
    throw err;
  }

  return NextResponse.json(
    { token, expiresIn: DEFAULT_EXPIRES_IN_SECONDS },
    { headers: NO_STORE_HEADERS },
  );
}

// expiresInSeconds is intentionally not client-configurable above 30 min —
// mirrors jwt-issuer.ts's validateInput ceiling.
void MAX_EXPIRES_IN_SECONDS;
