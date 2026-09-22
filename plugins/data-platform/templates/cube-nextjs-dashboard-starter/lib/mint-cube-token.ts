// ---------------------------------------------------------------------------
// Shared Cube-audience JWT mint (factored out FORGE dashboard-top1pct P2-14,
// 2026-09-03 — see lib/rate-limiter.ts's header for why: this exact
// token-minting logic was hand-duplicated across api/cube-token/route.ts
// and api/export/route.ts, and security review caught the two copies
// already drifting on their FIRST duplication — one had a hardening fix
// the other lacked). Both routes call THIS module now; a future fix lands
// once.
// ---------------------------------------------------------------------------

import jwt from "jsonwebtoken";
import crypto from "crypto";

export const MIN_SIGNING_KEY_BYTES = 32; // HS256 minimum

export class SigningKeyUnusableError extends Error {}

/**
 * Mints a short-lived, tenant-scoped Cube-audience JWT. `tenantId`/`userId`
 * must come from the caller's own server-verified session — this function
 * accepts them as opaque strings and does no session resolution itself.
 */
export function mintCubeToken(tenantId: string, userId: string, expiresInSeconds: number): string {
  const signingKey = process.env.JWT_SIGNING_KEY;
  if (!signingKey || signingKey.length < MIN_SIGNING_KEY_BYTES) {
    throw new SigningKeyUnusableError(
      `env var JWT_SIGNING_KEY must be a string of >= ${MIN_SIGNING_KEY_BYTES} bytes.`,
    );
  }

  const now = Math.floor(Date.now() / 1000);
  const payload = {
    sub: userId,
    tenant_id: tenantId,
    iat: now,
    exp: now + expiresInSeconds,
    iss: process.env.JWT_ISSUER || "data-platform-host",
    aud: "cube" as const,
    nonce: crypto.randomUUID(),
  };

  return jwt.sign(payload, signingKey, {
    algorithm: "HS256",
    header: { alg: "HS256", typ: "JWT", kid: process.env.JWT_KEY_VERSION || "1" },
  });
}
