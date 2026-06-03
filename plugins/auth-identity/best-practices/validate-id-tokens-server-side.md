# Validate ID tokens server-side — never trust unverified client-supplied identity claims

**Status:** Absolute rule — verify signature + iss + aud + exp server-side before trusting any identity claim. Never accept client-supplied claims at face value.

**Domain:** Token validation / identity verification

**Applies to:** `auth-identity`

---

## Why this exists

An OIDC `id_token` is a signed JWT. It contains identity claims (`sub`, `email`, `name`, `picture`) that your application uses to identify the user. But a JWT is just a base64-encoded JSON structure — anyone can create one. The claims in a JWT are only trustworthy if:

1. The signature is valid (proving the token was issued by the expected identity provider, not forged).
2. The `iss` (issuer) claim matches the expected provider (preventing tokens from a different issuer being accepted).
3. The `aud` (audience) claim matches your application's `client_id` (preventing tokens issued for another app being replayed against yours).
4. The `exp` (expiration) is in the future (preventing use of expired tokens).

If you skip any of these checks, an attacker can:

- **Skip signature verification:** forge an arbitrary identity claim (e.g., sign a token with their own key and set `email: admin@example.com`).
- **Skip `iss` check:** present a valid token from a different issuer (e.g., a token from their own Google Cloud project).
- **Skip `aud` check:** present a valid token issued for another application and replay it against yours (cross-audience attack).
- **Skip `exp` check:** use an expired token that was previously stolen.

These are not theoretical attacks — all four have been exploited in real applications.

---

## How to apply

**Server-side verification only.** Never trust unverified claims on the client (browser) side.

### Using Supabase Auth (recommended for this stack)

Supabase Auth handles ID-token verification automatically. When a user completes the Google OAuth flow via Supabase Auth, Supabase verifies the ID token from Google before creating the session. Your application uses `supabase.auth.getUser()` (which validates the session server-side), not the raw `id_token`.

```ts
// ✅ Correct: Supabase Auth has already verified the ID token
const { data: { user } } = await supabase.auth.getUser();
// user.id, user.email are from a verified, server-validated session
```

[unverified — confirm Supabase Auth performs ID-token signature verification; verify at supabase.com/docs/guides/auth]

### Verifying a Google ID token manually

Use this when your API receives a Google ID token from a client (e.g., a mobile app that passes the raw token to your API as a Bearer token).

```ts
// Using 'jose' library — npm install jose
// [unverified — package name and API; verify at npmjs.com/package/jose]
import { createRemoteJWKSet, jwtVerify } from "jose";

// Google's JWKS endpoint — public keys for ID token verification
// [unverified — verify current URL at accounts.google.com/.well-known/openid-configuration]
const GOOGLE_JWKS = createRemoteJWKSet(
  new URL("https://www.googleapis.com/oauth2/v3/certs"),
);

export async function verifyGoogleIdToken(token: string): Promise<{ sub: string; email: string }> {
  const { payload } = await jwtVerify(token, GOOGLE_JWKS, {
    issuer: ["https://accounts.google.com", "accounts.google.com"], // both forms [unverified]
    audience: process.env.GOOGLE_CLIENT_ID!, // your OAuth client_id
    // jose pins RS256 by inspecting the JWKS key type — alg:none is rejected automatically
  });

  if (!payload.sub || !payload.email) {
    throw new Error("Missing required claims");
  }

  // payload.exp is verified automatically by jwtVerify
  // payload.iat is available for additional clock-skew checks if needed

  return { sub: payload.sub as string, email: payload.email as string };
}
```

**Do NOT:**
```ts
// ❌ NEVER — decode without verification (trusts unverified claims)
import { decode } from "jsonwebtoken";
const claims = decode(idToken); // decode ≠ verify; no signature check

// ❌ NEVER — trust client-supplied email without verification
const email = req.body.email; // attacker can supply any email
const userId = req.headers["x-user-id"]; // can be forged

// ❌ NEVER — accept alg:none (allows unsigned tokens)
jwt.verify(token, "", { algorithms: ["none"] });

// ❌ NEVER — use a hardcoded public key instead of fetching from JWKS
// (hardcoded keys cannot be rotated; you'll miss Google's key rotation)
const publicKey = "-----BEGIN PUBLIC KEY-----\nMIIBIjANBg...";
```

---

## Required verification checklist

Every ID-token verification must check all five:

| Check | Why | Library behavior |
|---|---|---|
| **Signature** | Proves the token was signed by the expected provider | `jwtVerify` with JWKS: automatic |
| **`iss` (issuer)** | Prevents cross-issuer token replay | `issuer` option: automatic |
| **`aud` (audience)** | Prevents cross-application token replay | `audience` option: automatic |
| **`exp` (expiration)** | Prevents use of expired/stolen tokens | `jwtVerify`: automatic (throws if expired) |
| **`alg` pin** | Prevents `alg:none` and algorithm confusion attacks | `jose`: infers from JWKS key type; never pass `algorithms: ['none']` |

Optional but recommended:
- **`iat` clock-skew check** — reject tokens with `iat` more than 5 minutes in the future
- **`nonce`** — if you included a nonce in the authorization request, verify it here

---

## What to trust after verification

Only claims in a verified token are trustworthy:

| Claim | After verification — can you trust it? |
|---|---|
| `sub` | Yes — the user's stable, unique identifier at this issuer |
| `email` | Yes — but note: Google may mark `email_verified: false` for some accounts [unverified] |
| `name`, `picture` | Yes — display purposes; do not use for access control |
| Any claim in `app_metadata` (Supabase) | Yes, if you set it server-side; No, if the user set it (use `app_metadata` not `user_metadata`) |
| Any claim from an unverified JWT | No — treat as attacker-controlled |

---

## Edge cases / when this nuance applies

- **Supabase Auth session (most common case):** Supabase has already verified the ID token. Use `getUser()` — it validates the session server-side. This rule is satisfied by the managed provider.
- **Google One Tap / Sign In With Google button (client-side):** Google returns an ID token directly to the browser. That token **must be sent to your server for verification** before any user session is established. Do not create a session based solely on the client-side credential.
- **Service-to-service (M2M):** access tokens (not ID tokens) are the standard; see the Client Credentials flow in `oauth-oidc-flow-design` skill.
- **`email` claim and `email_verified`:** for Google accounts, `email_verified` should be `true` — reject or flag accounts where it is `false` before using the email claim for identity-based access control. [unverified — confirm Google's behavior]

---

## See also

- Skill: [`../skills/oauth-oidc-flow-design/SKILL.md`](../skills/oauth-oidc-flow-design/SKILL.md) — how the ID token was obtained and the full verification-step sequence
- Skill: [`../skills/protect-spa-and-api/SKILL.md`](../skills/protect-spa-and-api/SKILL.md) — using verified identity in API middleware
- Best-practice: [`./never-store-tokens-in-localstorage.md`](./never-store-tokens-in-localstorage.md) — where to store tokens before verifying them
- RFC: JSON Web Token Best Current Practices (RFC 8725) [unverified — verify at datatracker.ietf.org/doc/html/rfc8725]
- Security escalation: [`../../ravenclaude-core/agents/security-reviewer.md`](../../ravenclaude-core/agents/security-reviewer.md)

## Provenance

Derived from RFC 8725 (JWT Best Current Practices) [unverified], OAuth 2.0 Security BCP [unverified], Google Identity documentation on ID-token verification [unverified — verify at developers.google.com/identity/openid-connect/openid-connect#validatinganidtoken], and the `protect-spa-and-api` skill's token-verification middleware pattern.

---

_Last reviewed: 2026-06-03 by `claude`_
