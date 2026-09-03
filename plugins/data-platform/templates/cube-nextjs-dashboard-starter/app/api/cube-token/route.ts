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

function isRateLimited(key: string): boolean {
  const now = Date.now();
  const timestamps = (requestLog.get(key) ?? []).filter((t) => now - t < RATE_LIMIT_WINDOW_MS);
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
      { status: 429, headers: { "Cache-Control": "no-store" } },
    );
  }

  const signingKey = process.env.JWT_SIGNING_KEY;
  const signingKeyUsable = Boolean(signingKey) && signingKey!.length >= MIN_SIGNING_KEY_BYTES;
  if (!signingKeyUsable) {
    return NextResponse.json(
      {
        error: `cube-token: env var JWT_SIGNING_KEY must be a string of >= ${MIN_SIGNING_KEY_BYTES} bytes.`,
      },
      { status: 500, headers: { "Cache-Control": "no-store" } },
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
    { headers: { "Cache-Control": "no-store" } },
  );
}

// expiresInSeconds is intentionally not client-configurable above 30 min —
// mirrors jwt-issuer.ts's validateInput ceiling.
void MAX_EXPIRES_IN_SECONDS;
