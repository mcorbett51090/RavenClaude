# Use Authorization Code + PKCE — never the Implicit flow

**Status:** Absolute rule — the Implicit flow is deprecated by OAuth 2.0 Security BCP and OAuth 2.1. No new implementation uses it, and existing implementations must migrate.

**Domain:** OAuth/OIDC flow design

**Applies to:** `auth-identity`

---

## Why this exists

The OAuth 2.0 Implicit flow (`response_type=token`) was the original recommendation for SPAs before Proof Key for Code Exchange (PKCE) existed. It returns an access token directly in the URL fragment (`#access_token=...`). This creates multiple serious security problems:

1. **Access token in browser history** — the URL fragment is stored in the browser's history and can be recovered by any page on the same origin via `document.referrer` or history APIs.
2. **Access token in server logs** — some proxies and analytics tools log full URLs including fragments.
3. **No request binding** — there is no cryptographic binding between the authorization request and the token response. An authorization code interception attack is possible.
4. **No refresh token** — the Implicit flow cannot issue a refresh token, forcing frequent re-authentication or long-lived access tokens.
5. **No client authentication** — even if a `client_secret` exists, it cannot be safely used in the Implicit flow.

The [OAuth 2.0 Security Best Current Practice (BCP)](https://datatracker.ietf.org/doc/html/rfc9700) and the [OAuth 2.1 draft](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1) both formally deprecate the Implicit flow for these reasons. [unverified — confirm current RFC numbers and draft status]

**PKCE (Authorization Code + PKCE) solves all of these** without any of the weaknesses:
- The authorization code is short-lived and single-use.
- The `code_verifier` cryptographically binds the request to the code exchange.
- Tokens are returned only in the token endpoint response, not in the URL.
- Refresh tokens are supported.

---

## How to apply

For every public client (SPA, native/mobile app, CLI with browser redirect), use Authorization Code + PKCE.

**Flow summary:**

```
1. App generates: code_verifier (random 43-128 chars, high entropy)
                  code_challenge = BASE64URL(SHA256(code_verifier))

2. Authorization request:
   GET /authorize?
     response_type=code           ← not "token"
     client_id=...
     redirect_uri=...
     code_challenge=<hash>        ← PKCE challenge
     code_challenge_method=S256   ← SHA-256
     scope=openid email profile
     state=<random CSRF nonce>    ← CSRF protection

3. User authenticates + consents

4. Callback: /callback?code=<auth_code>&state=<nonce>
   → Verify state matches

5. Token exchange (server-side or PKCE-protected):
   POST /token
     grant_type=authorization_code
     code=<auth_code>
     code_verifier=<original verifier>  ← PKCE proof
     client_id=...
     redirect_uri=...

6. Token endpoint returns: access_token, id_token, refresh_token
```

The `code_verifier` is never sent to the authorization server in step 2 — only its hash. Step 5 proves the same party completed both steps.

**In practice for this stack:**

Supabase Auth and Auth.js both implement Authorization Code + PKCE automatically for Google SSO. The developer does not need to implement the flow manually — they call `signInWithOAuth({ provider: 'google' })` and the library handles PKCE. [unverified — confirm PKCE default in current Supabase Auth and Auth.js versions]

**Do:**
- Use `response_type=code` (authorization code), not `response_type=token` (implicit)
- Verify `code_challenge_method=S256` is configured (SHA-256 hash, not plain)
- Verify PKCE is not disabled in your auth library configuration
- Include the `state` parameter for CSRF protection

**Don't:**
- Use `response_type=token` for any new SPA, mobile, or browser-based implementation
- Disable PKCE in Supabase Auth, Auth.js, or any auth library that enables it by default
- Use the Hybrid flow (`response_type=code token`) — it shares the Implicit flow's URL-fragment exposure risk

---

## Migrating from Implicit to Authorization Code + PKCE

If an existing application uses the Implicit flow:

1. Switch `response_type=token` → `response_type=code` in the authorization request.
2. Add PKCE parameters (`code_challenge`, `code_challenge_method=S256`).
3. Add a server-side or library-handled token exchange for the authorization code.
4. Update token storage to use HttpOnly cookies (not localStorage — see `never-store-tokens-in-localstorage.md`).
5. Route the migration to `ravenclaude-core/security-reviewer` before deploying.

If using a managed provider (Supabase Auth, Auth.js), switching may be as simple as updating the library configuration and removing the Implicit-flow settings.

---

## Edge cases / when this rule does NOT apply

This rule applies to every interactive (user-facing) OAuth flow. The only flows where it does not apply:

- **Client Credentials** — M2M (no user interaction; no authorization code flow at all)
- **Device Authorization Grant** — for TV / CLI devices with no browser; has its own security considerations
- **SAML** — different protocol entirely

The rule applies to all SPA, web app, and native-app flows. It is not conditional on the scope of the requested permissions.

---

## See also

- Skill: [`../skills/oauth-oidc-flow-design/SKILL.md`](../skills/oauth-oidc-flow-design/SKILL.md) — full flow-selection decision tree
- Best-practice: [`./never-store-tokens-in-localstorage.md`](./never-store-tokens-in-localstorage.md) — the companion rule on token storage
- RFC: OAuth 2.0 Security BCP [unverified — verify at datatracker.ietf.org/doc/html/rfc9700]
- Security escalation: [`../../ravenclaude-core/agents/security-reviewer.md`](../../ravenclaude-core/agents/security-reviewer.md)

## Provenance

Derived from OAuth 2.0 Security BCP (RFC 9700 [unverified]) and OAuth 2.1 draft, which formally deprecate the Implicit flow; from the `oauth-oidc-flow-design` skill's flow-selection table; and from industry-wide consensus (2019–2026) on PKCE as the correct mechanism for public clients.

---

_Last reviewed: 2026-06-03 by `claude`_
