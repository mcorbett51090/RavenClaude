// ---------------------------------------------------------------------------
// Server-side Cube-audience JWT mint. Follows the ../../jwt-issuer.ts pattern
// (kept in this scaffold as an inline, minimal version so the starter has no
// hard dependency on that file living at a fixed relative path — copy the
// two in sync, or replace this with an import if you vendor jwt-issuer.ts
// directly into your app).
//
// SECURITY (revised after mandatory security review): responses carry
// Cache-Control: no-store (a JWT is not cacheable content), and the route
// applies a per-session rate limit — a per-process in-memory limiter, which
// is fine for a single-instance dev/demo deployment and MUST be replaced
// with a shared store (Redis, etc.) before running more than one instance,
// since each instance would otherwise track its own independent counter.
// ---------------------------------------------------------------------------

import { NextResponse } from "next/server";
import jwt from "jsonwebtoken";
import crypto from "crypto";
import { getSession } from "@/lib/session";

const DEFAULT_EXPIRES_IN_SECONDS = 900; // 15 min — see jwt-issuer.ts
const MAX_EXPIRES_IN_SECONDS = 1800; // 30 min hard ceiling
const MIN_SIGNING_KEY_BYTES = 32; // HS256 minimum

// Naive per-process rate limiter — see the file header caveat above.
const RATE_LIMIT_MAX_REQUESTS = 30;
const RATE_LIMIT_WINDOW_MS = 60_000;
const requestLog = new Map<string, number[]>();

// Bounded eviction (FORGE dashboard-top1pct P0-5, 2026-09-03): requestLog grew
// one entry per distinct session.userId, forever, with no eviction — a slow
// memory leak in the file whose own header claims a considered security
// posture. Every call opportunistically sweeps stale keys (an empty
// timestamps array after the window filter below) at most once per
// SWEEP_INTERVAL_MS, so the map's size tracks active users in the current
// window, not total users ever seen.
const SWEEP_INTERVAL_MS = 5 * 60_000; // 5 min
let lastSweptAtMs = 0;

function sweepStaleEntries(now: number): void {
  if (now - lastSweptAtMs < SWEEP_INTERVAL_MS) return;
  lastSweptAtMs = now;
  for (const [key, timestamps] of requestLog) {
    const fresh = timestamps.filter((t) => now - t < RATE_LIMIT_WINDOW_MS);
    if (fresh.length === 0) {
      requestLog.delete(key);
    } else if (fresh.length !== timestamps.length) {
      requestLog.set(key, fresh);
    }
  }
}

function isRateLimited(key: string): boolean {
  const now = Date.now();
  sweepStaleEntries(now);
  const timestamps = (requestLog.get(key) ?? []).filter((t) => now - t < RATE_LIMIT_WINDOW_MS);
  // Return BEFORE pushing once already over the limit (found in security
  // review, 2026-09-03): the sweep bounds the number of KEYS, but a caller
  // already past the ceiling kept appending to its OWN array for the rest of
  // the window while receiving 429s — those entries are fresh, not stale, so
  // the sweep can't reclaim them. An authenticated user flooding this route
  // drove the per-request .filter() to O(current length) over a linearly
  // growing array: O(n^2) CPU across the window. Returning early here caps
  // each key's array at RATE_LIMIT_MAX_REQUESTS + 1 regardless of how many
  // more requests arrive.
  if (timestamps.length > RATE_LIMIT_MAX_REQUESTS) {
    requestLog.set(key, timestamps);
    return true;
  }
  timestamps.push(now);
  requestLog.set(key, timestamps);
  return timestamps.length > RATE_LIMIT_MAX_REQUESTS;
}

export async function POST() {
  // tenantId + userId come from the SERVER-VERIFIED session — never from
  // the request body. This route intentionally accepts no input.
  const session = await getSession();

  if (isRateLimited(session.userId)) {
    return NextResponse.json(
      { error: "cube-token: rate limit exceeded." },
      {
        status: 429,
        headers: { "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff" },
      },
    );
  }

  const signingKey = process.env.JWT_SIGNING_KEY;
  const signingKeyUsable = Boolean(signingKey) && signingKey!.length >= MIN_SIGNING_KEY_BYTES;
  if (!signingKeyUsable) {
    return NextResponse.json(
      {
        error: `cube-token: env var JWT_SIGNING_KEY must be a string of >= ${MIN_SIGNING_KEY_BYTES} bytes.`,
      },
      {
        status: 500,
        headers: { "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff" },
      },
    );
  }

  const now = Math.floor(Date.now() / 1000);
  const payload = {
    sub: session.userId,
    tenant_id: session.tenantId,
    iat: now,
    exp: now + DEFAULT_EXPIRES_IN_SECONDS,
    iss: process.env.JWT_ISSUER || "data-platform-host",
    aud: "cube" as const,
    nonce: crypto.randomUUID(),
  };

  const token = jwt.sign(payload, signingKey!, {
    algorithm: "HS256",
    header: { alg: "HS256", typ: "JWT", kid: process.env.JWT_KEY_VERSION || "1" },
  });

  return NextResponse.json(
    { token, expiresIn: DEFAULT_EXPIRES_IN_SECONDS },
    { headers: { "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff" } },
  );
}

// expiresInSeconds is intentionally not client-configurable above 30 min —
// mirrors jwt-issuer.ts's validateInput ceiling.
void MAX_EXPIRES_IN_SECONDS;
