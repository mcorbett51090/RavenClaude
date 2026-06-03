---
name: oauth-oidc-flow-design
description: "Pick and implement the right OAuth 2.0 / OIDC flow by client type: Authorization Code + PKCE for SPA and native apps, confidential-client code flow for server-side apps, client-credentials for M2M. ID-token vs access-token vs refresh-token handling. Deprecated Implicit flow is never recommended."
---

# Skill: oauth-oidc-flow-design

> **Invoked by:** any agent designing or reviewing an OAuth/OIDC authentication flow; `ravenclaude-core/security-reviewer` when reviewing auth-flow changes.
>
> **When to invoke:** new authentication integration; switching flows; adding an API or M2M service account; auditing an existing flow for security.
>
> **Output:** documented flow selection rationale + client-type → flow mapping + token-handling guidance + anti-pattern flags.

---

## Boundary

This skill designs the OAuth/OIDC flow. Implementation details (setting up the Google Cloud OAuth client, Supabase provider configuration) are in the `google-sso-setup` skill. Session and token storage after the flow completes is in `session-and-token-management`. Data-row authorization is owned by `data-platform/rls-policy-authoring`.

---

## Flow selection by client type

| Client type | Correct flow | Never use |
|---|---|---|
| **SPA (React, Next.js client-side)** | Authorization Code + PKCE | Implicit |
| **Native / mobile app** | Authorization Code + PKCE | Implicit |
| **Server-rendered web app (Next.js SSR, Express)** | Authorization Code (confidential client, no PKCE required but PKCE still recommended) | Implicit |
| **Backend API / BFF (machine-to-user, acting on behalf of a user)** | Authorization Code (confidential client) | Implicit, Resource Owner Password |
| **Machine-to-machine (service account, daemon, CI)** | Client Credentials | Any user-facing flow |
| **TV / CLI / device with no browser** | Device Authorization Grant | Implicit |

### Why Implicit flow is never recommended

The OAuth 2.0 Implicit flow (`response_type=token`) returns an access token directly in the URL fragment. It was designed for SPAs before PKCE existed. It is deprecated by [OAuth 2.0 Security BCP (RFC 9700) and the OAuth 2.1 draft](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1) [unverified — verify current RFC numbers] because:

- The access token is exposed in the browser history and server logs via the URL fragment.
- It provides no binding between the authorization request and the token response (no code verifier).
- It cannot return a refresh token.
- PKCE solves the same SPA security problem without any of these weaknesses.

**The best-practice `use-authorization-code-pkce-never-implicit.md` is an absolute rule in this plugin.**

---

## Authorization Code + PKCE (SPA / native)

PKCE (Proof Key for Code Exchange) adds a code verifier/challenge that binds the browser that started the flow to the browser that completes it, defeating authorization code interception.

```
[Browser]                         [Auth Server (Google/Supabase)]
  |                                          |
  |-- generate code_verifier (random 43-128 chars, high entropy)
  |-- code_challenge = BASE64URL(SHA256(code_verifier))
  |                                          |
  |-- GET /authorize?                        |
  |     response_type=code                   |
  |     client_id=...                        |
  |     redirect_uri=...                     |
  |     code_challenge=<hash>                |
  |     code_challenge_method=S256           |
  |     scope=openid email profile           |
  |     state=<random CSRF nonce>            |
  |                                          |
  |          user authenticates + consents   |
  |                                          |
  |<-- redirect to redirect_uri?code=<code>&state=<nonce>
  |                                          |
  |-- verify state matches CSRF nonce        |
  |                                          |
  |-- POST /token                            |
  |     grant_type=authorization_code        |
  |     code=<code>                          |
  |     code_verifier=<original verifier>    |
  |     client_id=...                        |
  |     redirect_uri=...                     |
  |                                          |
  |<-- { access_token, id_token, refresh_token, expires_in }
```

The `code_verifier` is never sent to the authorization server during the first leg — only its hash. The token exchange proves the same party completed both legs.

**Supabase Auth handles PKCE automatically** when using `@supabase/ssr`. Do not disable it. [unverified — confirm PKCE is on by default in current Supabase Auth version]

---

## Authorization Code flow (confidential server client)

For server-side apps that can keep a `client_secret` confidential (Express, Next.js API routes, Django, etc.). The `client_secret` is included in the token exchange, providing authentication of the client itself — in addition to PKCE if used.

- Use PKCE regardless — defense in depth; it costs nothing.
- The `client_secret` never leaves the server.
- Token endpoint is called server-to-server, not from the browser.

---

## Client Credentials (M2M)

For service accounts, background jobs, CI pipelines, API-to-API calls with no human user in the loop.

```
[Service A]                        [Auth Server]
  |-- POST /token                       |
  |     grant_type=client_credentials   |
  |     client_id=<service-client-id>   |
  |     client_secret=<secret>          |  ← in env var, never in code
  |     scope=<required scope>          |
  |                                     |
  |<-- { access_token, expires_in }
```

- No refresh token — re-acquire with client credentials when expired.
- Scope the client to the minimum required permissions.
- Rotate the client secret on a schedule (e.g., 90 days). [unverified — check your org's secret-rotation policy]
- Do not use a human user's credentials for M2M; create a dedicated service account.

---

## Token types and handling

| Token | What it contains | Who validates it | Where to store |
|---|---|---|---|
| **ID token** (OIDC `id_token`) | User identity claims (`sub`, `email`, `name`, `picture`). A signed JWT. | Server-side: verify signature + `iss` + `aud` + `exp`. Never trust unverified. | Decode claims server-side only; do not store in localStorage. |
| **Access token** | Authorization to call APIs. May be opaque or a JWT. Short-lived (seconds to minutes). | API server via introspection or JWT verification. | HttpOnly cookie or server-side session. Never localStorage. |
| **Refresh token** | Long-lived credential to get new access tokens without re-authenticating. | Auth server only. | Server-side session or HttpOnly cookie with `SameSite=Strict`. High-value target — rotate on use. |

**Storage rule:** never store any token in `localStorage`. The `never-store-tokens-in-localstorage.md` best-practice is an absolute rule. Use HttpOnly + Secure + SameSite cookies (managed automatically by Supabase SSR and most auth libraries).

### ID token validation (server-side)

Before trusting any claim in an OIDC `id_token`:

1. Verify the signature using the issuer's JWKS endpoint (e.g., `https://accounts.google.com/.well-known/openid-configuration` → `jwks_uri`). [unverified — confirm Google's OIDC discovery URL]
2. Check `iss` matches the expected issuer (e.g., `https://accounts.google.com`).
3. Check `aud` matches your application's `client_id`.
4. Check `exp` is in the future.
5. Check `iat` is not too far in the past (clock-skew tolerance, typically ±5 minutes).
6. If present, validate `nonce` matches the value you sent in the authorization request.

The `validate-id-tokens-server-side.md` best-practice is an absolute rule. Use a well-maintained library (`google-auth-library`, `jose`, `jsonwebtoken` with explicit algorithm pinning) — do not roll your own verification. Route to `ravenclaude-core/security-reviewer` before shipping.

---

## Refresh token rotation

- On every token refresh, the auth server issues a new refresh token and invalidates the old one.
- If the old token is presented again (replay), the auth server detects the reuse and can revoke the entire grant.
- Supabase Auth implements refresh token rotation by default. [unverified — confirm in current Supabase Auth docs]
- Store refresh tokens in HttpOnly cookies, not localStorage.
- Detect and handle `refresh_token_already_used` or `invalid_refresh_token` errors gracefully (redirect to login).

---

## State parameter (CSRF protection)

Always include a random, unguessable `state` parameter in the authorization request. Verify it matches on return. Without it, an attacker can forge the callback and inject their authorization code into your user's session.

Supabase Auth handles `state` automatically. If rolling your own, generate a cryptographically random value, store it in a short-lived session cookie (HttpOnly), and validate on callback.

---

## Anti-patterns this skill flags

- Using the Implicit flow (`response_type=token`) for any new implementation — deprecated, unsafe
- Disabling PKCE for a SPA or native app — PKCE is mandatory for public clients
- Storing `id_token` or `access_token` in `localStorage` — see `never-store-tokens-in-localstorage.md`
- Trusting `id_token` claims without server-side signature verification — see `validate-id-tokens-server-side.md`
- Sharing a single OAuth client (client_id + secret) between environments — use separate clients per environment
- Resource Owner Password Credentials grant — the user's password is handled by your app; use a redirect-based flow instead
- `client_secret` present in front-end code or a `NEXT_PUBLIC_` env var — server-side only
- Omitting `state` parameter — opens CSRF attack vector
- Using a user's personal credentials as a service account — use dedicated M2M client credentials

---

## See also

- Skill: [`../google-sso-setup/SKILL.md`](../google-sso-setup/SKILL.md) — provider setup (Supabase + Google Cloud config)
- Skill: [`../session-and-token-management/SKILL.md`](../session-and-token-management/SKILL.md) — what to do with tokens after the flow completes
- Best-practice: [`../../best-practices/use-authorization-code-pkce-never-implicit.md`](../../best-practices/use-authorization-code-pkce-never-implicit.md)
- Best-practice: [`../../best-practices/never-store-tokens-in-localstorage.md`](../../best-practices/never-store-tokens-in-localstorage.md)
- Best-practice: [`../../best-practices/validate-id-tokens-server-side.md`](../../best-practices/validate-id-tokens-server-side.md)
- RFC: OAuth 2.0 Security BCP — [datatracker.ietf.org/doc/html/rfc9700](https://datatracker.ietf.org/doc/html/rfc9700) [unverified — confirm current RFC]
- Security escalation: [`../../../ravenclaude-core/agents/security-reviewer.md`](../../../ravenclaude-core/agents/security-reviewer.md)
