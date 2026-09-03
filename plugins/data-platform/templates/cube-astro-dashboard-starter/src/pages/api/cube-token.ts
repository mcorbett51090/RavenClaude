// ---------------------------------------------------------------------------
// Server-side Cube-audience JWT mint — Astro APIRoute equivalent of the
// Next.js starter's app/api/cube-token/route.ts. Same security posture,
// carried over deliberately (see this starter's README "What's verified"):
// no client input accepted, rate-limited, no-store, session resolved
// server-side only.
// ---------------------------------------------------------------------------

import type { APIRoute } from "astro";
import jwt from "jsonwebtoken";
import crypto from "crypto";
import { getSession } from "@/lib/session";

export const prerender = false; // must run per-request, not at build time

const DEFAULT_EXPIRES_IN_SECONDS = 900; // 15 min
const MIN_SIGNING_KEY_BYTES = 32; // HS256 minimum

// Naive per-process rate limiter — same caveat as the Next.js starter: fine
// for a single-instance deployment, replace with a shared store (Redis,
// etc.) before running more than one instance.
const RATE_LIMIT_MAX_REQUESTS = 30;
const RATE_LIMIT_WINDOW_MS = 60_000;
const requestLog = new Map<string, number[]>();

// Bounded eviction (FORGE dashboard-top1pct P0-5, 2026-09-03): requestLog grew
// one entry per distinct session.userId, forever, with no eviction. Every call
// opportunistically sweeps stale keys at most once per SWEEP_INTERVAL_MS, so
// the map's size tracks active users in the current window, not total users
// ever seen. Same fix as the Next.js starter's route.ts — verified via a
// standalone simulated-time test proving the map does not grow unbounded
// across the process lifetime.
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
  // the sweep can't reclaim them. Same fix as the Next.js starter's route.ts.
  if (timestamps.length > RATE_LIMIT_MAX_REQUESTS) {
    requestLog.set(key, timestamps);
    return true;
  }
  timestamps.push(now);
  requestLog.set(key, timestamps);
  return timestamps.length > RATE_LIMIT_MAX_REQUESTS;
}

const NO_STORE = { "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff" };

export const POST: APIRoute = async () => {
  // tenantId + userId come from the SERVER-VERIFIED session — never from
  // the request body. This route intentionally reads no input.
  const session = await getSession();

  if (isRateLimited(session.userId)) {
    return new Response(JSON.stringify({ error: "cube-token: rate limit exceeded." }), {
      status: 429,
      headers: { "Content-Type": "application/json", ...NO_STORE },
    });
  }

  // process.env, NOT import.meta.env (FORGE dashboard-top1pct P0-5, 2026-09-03):
  // confirmed empirically this session that import.meta.env.X || <fallback>
  // reads for JWT_ISSUER/JWT_KEY_VERSION got frozen to their literal fallback
  // at BUILD time when the var was unset during `astro build` — Vite's
  // dead-code-elimination collapsed the `||` expression to a constant. A bare
  // import.meta.env.JWT_SIGNING_KEY (no `||`) happened to compile correctly to
  // a runtime process.env read in this Astro/Vite version, but process.env.X
  // sidesteps Vite's static-replace plugin entirely (it only targets
  // import.meta.env.*) and is the fix plan.md calls for — applied to all
  // three vars here for consistency and to not depend on that no-`||`
  // compilation detail holding across Astro/Vite version bumps.
  const signingKey = process.env.JWT_SIGNING_KEY;
  const signingKeyUsable = Boolean(signingKey) && signingKey!.length >= MIN_SIGNING_KEY_BYTES;
  if (!signingKeyUsable) {
    return new Response(
      JSON.stringify({
        error: `cube-token: env var JWT_SIGNING_KEY must be a string of >= ${MIN_SIGNING_KEY_BYTES} bytes.`,
      }),
      { status: 500, headers: { "Content-Type": "application/json", ...NO_STORE } },
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

  return new Response(JSON.stringify({ token, expiresIn: DEFAULT_EXPIRES_IN_SECONDS }), {
    status: 200,
    headers: { "Content-Type": "application/json", ...NO_STORE },
  });
};
