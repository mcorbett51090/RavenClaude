// ---------------------------------------------------------------------------
// Shared Cube-audience JWT mint — Astro-side twin of the Next.js starter's
// lib/mint-cube-token.ts (factored out FORGE dashboard-top1pct P2-14,
// 2026-09-03). Both cube-token.ts and export.ts call this now.
//
// process.env, NOT import.meta.env (FORGE dashboard-top1pct P0-5,
// 2026-09-03): confirmed empirically that an import.meta.env.X || fallback
// read gets frozen to the literal fallback at BUILD time when the var is
// unset during `astro build` — Vite's dead-code-elimination collapses the
// `||` expression to a constant. process.env.X sidesteps Vite's
// static-replace plugin entirely (it only targets import.meta.env.*).
// ---------------------------------------------------------------------------

import jwt from "jsonwebtoken";
import crypto from "crypto";

export const MIN_SIGNING_KEY_BYTES = 32;

export class SigningKeyUnusableError extends Error {}

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
