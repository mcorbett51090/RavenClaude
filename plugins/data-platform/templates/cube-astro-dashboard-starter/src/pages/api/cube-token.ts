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

function isRateLimited(key: string): boolean {
  const now = Date.now();
  const timestamps = (requestLog.get(key) ?? []).filter((t) => now - t < RATE_LIMIT_WINDOW_MS);
  timestamps.push(now);
  requestLog.set(key, timestamps);
  return timestamps.length > RATE_LIMIT_MAX_REQUESTS;
}

const NO_STORE = { "Cache-Control": "no-store" };

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

  const signingKey = import.meta.env.JWT_SIGNING_KEY as string | undefined;
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
    iss: (import.meta.env.JWT_ISSUER as string) || "data-platform-host",
    aud: "cube" as const,
    nonce: crypto.randomUUID(),
  };

  const token = jwt.sign(payload, signingKey!, {
    algorithm: "HS256",
    header: { alg: "HS256", typ: "JWT", kid: (import.meta.env.JWT_KEY_VERSION as string) || "1" },
  });

  return new Response(JSON.stringify({ token, expiresIn: DEFAULT_EXPIRES_IN_SECONDS }), {
    status: 200,
    headers: { "Content-Type": "application/json", ...NO_STORE },
  });
};
