# Bind ID Tokens to the Requesting Client — Validate aud and iss

**Status:** Absolute rule
**Domain:** Auth & Identity — Token validation
**Applies to:** `auth-identity`

---

## Why this exists

An ID token is only valid for the application that requested it. The `aud` (audience) claim identifies the intended recipient as your OAuth client ID; the `iss` (issuer) claim identifies the provider that issued it. Without validating both, a token issued for a different application — possibly controlled by an attacker — could be accepted as valid by your application. This is called a "confused deputy" attack: your server acts on behalf of the attacker's client because it didn't check who the token was issued for. Google's ID token spec, the OIDC Core spec, and every managed provider require `aud` and `iss` validation server-side. The existing `validate-id-tokens-server-side.md` rule covers the full validation pipeline; this rule narrows to the audience/issuer binding, which is the claim teams most often skip or misconfigure.

## How to apply

**Full validation checklist (server-side, every time a token is accepted):**

```typescript
import { jwtVerify, createRemoteJWKSet } from "jose";

const GOOGLE_JWKS = createRemoteJWKSet(
  new URL("https://www.googleapis.com/oauth2/v3/certs"),
);

async function verifyGoogleIdToken(idToken: string): Promise<GoogleClaims> {
  const { payload } = await jwtVerify(idToken, GOOGLE_JWKS, {
    issuer: ["https://accounts.google.com", "accounts.google.com"], // both forms are valid
    audience: process.env.GOOGLE_CLIENT_ID,  // MUST match your OAuth client ID exactly
    clockTolerance: 30,                      // seconds of leeway for clock skew only
  });

  // Additional checks jose does not enforce automatically:
  if (!payload.sub) throw new Error("Missing sub claim");
  if (payload.nonce && payload.nonce !== expectedNonce) {
    throw new Error("Nonce mismatch"); // only when you set a nonce in the request
  }

  return payload as GoogleClaims;
}
```

**The four claims to validate — in order:**

| Claim | What to check | If it fails |
|---|---|---|
| `iss` | Must be `https://accounts.google.com` or `accounts.google.com` for Google; your provider's issuer URL for others | Reject — wrong or forged issuer |
| `aud` | Must exactly match your OAuth client ID (the `GOOGLE_CLIENT_ID` env var) | Reject — token for a different app |
| `exp` | Must be in the future (with ≤30 s clock-skew tolerance) | Reject — expired token |
| `sub` | Must be present and non-empty; treat as the stable user identifier | Reject — missing identity claim |

**Multi-tenant / multi-app scenario:**

If you operate more than one OAuth client (e.g., web app and mobile app), the `aud` array may contain multiple valid audiences. Still validate that your specific client ID is in the `aud` set — do not accept any non-empty `aud`.

**Supabase Auth path:** Supabase Auth validates `aud`, `iss`, and `exp` internally when you call `supabase.auth.getUser()` on the server. Validate that you are always calling `getUser()` on the server-side client (not the browser client) for any trust decision.

**Do:**
- Store the expected `aud` (your client ID) in an environment variable — never hardcode the string in validation logic.
- Validate `iss` against an allowlist of known-good issuer URLs, not just presence.
- Log and alert on `aud`/`iss` mismatches — they indicate either misconfiguration or active token-theft probing.

**Don't:**
- Skip `aud` validation because "we only use one provider" — this is the condition under which confused-deputy attacks succeed.
- Accept a token with an `aud` of `*` or an empty string.
- Validate the signature but skip the claims — signature validity proves authenticity; claim values prove the token is for your app.

## Edge cases / when the rule does NOT apply

- **Access tokens (not ID tokens):** access token `aud` validation is resource-server-specific and follows RFC 9068 (JWT Profile for OAuth 2.0 Access Tokens) rather than OIDC Core. The validation is still required; the `aud` value will be the resource server identifier, not the OAuth client ID.
- **Supabase service-role key usage (internal):** the service-role key bypasses RLS and is not a user token — it has no `aud`/`iss` to validate. The rule that applies instead is `never-hardcode-client-secrets.md`: it must never leave the server and must never be sent to a browser.

## See also

- [`../agents/auth-architect.md`](../agents/auth-architect.md) — designs the token validation strategy
- [`../agents/auth-implementation-engineer.md`](../agents/auth-implementation-engineer.md) — implements the server-side token verification
- [`./validate-id-tokens-server-side.md`](./validate-id-tokens-server-side.md) — the full server-side validation rule (this rule is a focused sub-rule)

## Provenance

Codifies OIDC Core 1.0 §3.1.3.7 (ID Token Validation), specifically the `aud` and `iss` validation requirements. Confused-deputy / audience-confusion attacks are documented in "OAuth 2.0 Security Best Current Practice" (RFC 9700) §2.4.

---

_Last reviewed: 2026-06-05 by `claude`_
