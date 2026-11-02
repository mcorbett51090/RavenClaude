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
//
// Dev-only fallback (review E-2, 2026-10-20): Vite loads .env files into
// import.meta.env, NOT process.env, so with bare process.env the README's
// `cp env.example .env && npm run dev` left JWT_SIGNING_KEY and
// CUBE_API_ORIGIN unset under `astro dev`. serverEnv() below falls back to
// import.meta.env ONLY when import.meta.env.DEV is true. In `astro build`
// DEV is the literal `false`, so that branch is dead code: the built server
// still reads process.env at runtime, and no .env value is inlined (checked
// by grepping dist/ for the key after an `astro build` with .env present).
// ---------------------------------------------------------------------------

import jwt from "jsonwebtoken";
import crypto from "crypto";

export const MIN_SIGNING_KEY_BYTES = 32;

export class SigningKeyUnusableError extends Error {}

// Static keys only: a bare or computed `import.meta.env[...]` makes Astro
// inline EVERY private .env value into the built chunk (observed with
// astro 4.16 build, review E-2). Each `import.meta.env.X` below sits in a
// branch that `astro build` compiles out, so none of them ships.
const DEV_DOTENV: Readonly<Record<string, string | undefined>> = import.meta.env.DEV
  ? {
      JWT_SIGNING_KEY: import.meta.env.JWT_SIGNING_KEY,
      JWT_ISSUER: import.meta.env.JWT_ISSUER,
      JWT_KEY_VERSION: import.meta.env.JWT_KEY_VERSION,
      CUBE_API_ORIGIN: import.meta.env.CUBE_API_ORIGIN,
      PUBLIC_CUBE_API_URL: import.meta.env.PUBLIC_CUBE_API_URL,
    }
  : {};

type ServerEnvName =
  "JWT_SIGNING_KEY" | "JWT_ISSUER" | "JWT_KEY_VERSION" | "CUBE_API_ORIGIN" | "PUBLIC_CUBE_API_URL";

/** Server-side env read: process.env first, then (astro dev only) the .env values Vite loaded. */
export function serverEnv(name: ServerEnvName): string | undefined {
  return process.env[name] ?? DEV_DOTENV[name];
}

export function mintCubeToken(tenantId: string, userId: string, expiresInSeconds: number): string {
  const signingKey = serverEnv("JWT_SIGNING_KEY");
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
    iss: serverEnv("JWT_ISSUER") || "data-platform-host",
    aud: "cube" as const,
    nonce: crypto.randomUUID(),
  };

  return jwt.sign(payload, signingKey, {
    algorithm: "HS256",
    header: { alg: "HS256", typ: "JWT", kid: serverEnv("JWT_KEY_VERSION") || "1" },
  });
}
