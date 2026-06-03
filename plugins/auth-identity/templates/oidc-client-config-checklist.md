# OIDC / OAuth client configuration checklist

> Pre-flight checklist before deploying or shipping any OAuth/OIDC client configuration. Run through every item; each `[ ]` must be ticked before the implementation goes to production.
>
> **Use with:** `auth-architecture-decision-record.md` and a `ravenclaude-core/security-reviewer` sign-off.

---

## 1. Redirect URIs

- [ ] Every redirect URI is explicitly registered in the provider (Google Cloud Console, Supabase, Auth0, etc.)
- [ ] No trailing-slash mismatch between registered URI and actual callback URI
- [ ] `http://localhost:*` URIs are registered only for dev/test OAuth clients, never for the production client
- [ ] Registered URIs use `https://` in production (not `http://`)
- [ ] Wild-card redirect URIs are not used (e.g., `https://example.com/*` is not acceptable — each path is explicit)
- [ ] The `next` / `redirect_to` post-login parameter is validated server-side as a relative path on your own domain (prevents open redirect)

---

## 2. Scopes

- [ ] Scopes limited to what the application actually uses
- [ ] Baseline scopes present: `openid`, `email`, `profile` (for Google SSO sign-in)
- [ ] No Drive, Calendar, Gmail, or other Google API scopes unless the app has a documented feature requiring them
- [ ] Sensitive scopes (if any) have been reviewed and noted in the ADR with business justification
- [ ] Google consent screen submitted for verification if using sensitive/restricted scopes or reaching > 100 test users [unverified — confirm current Google verification policy]

---

## 3. PKCE

- [ ] PKCE (`code_challenge_method=S256`) is enabled for all public clients (SPA, native/mobile apps)
- [ ] `code_verifier` is high-entropy (43-128 chars, cryptographically random)
- [ ] Implicit flow (`response_type=token`) is not used anywhere — deprecated and unsafe
- [ ] For Supabase Auth: PKCE is on by default — confirm it has not been disabled [unverified]
- [ ] For Auth.js v5: PKCE is on by default for Google — confirm not disabled [unverified]

---

## 4. Token validation (server-side)

- [ ] `id_token` signature verified against the issuer's JWKS endpoint (not a hardcoded public key)
- [ ] `iss` claim checked against the expected issuer (e.g., `https://accounts.google.com`)
- [ ] `aud` claim checked against your application's `client_id`
- [ ] `exp` claim checked — library must reject expired tokens automatically
- [ ] `iat` reasonableness checked — reject tokens issued far in the future (clock-skew attack)
- [ ] `nonce` validated if included in the authorization request
- [ ] Algorithm explicitly pinned (`RS256` for Google) — never accept `alg: none`
- [ ] Verification using a maintained library (`jose`, `google-auth-library`, `jsonwebtoken` with algorithm pin)
- [ ] No unverified client-supplied identity claims trusted

---

## 5. Cookie configuration

- [ ] Session / token cookie has `HttpOnly` flag — not readable by JavaScript
- [ ] Session / token cookie has `Secure` flag — only sent over HTTPS
- [ ] Session / token cookie has `SameSite=Lax` (minimum) or `SameSite=Strict`
- [ ] Verified in browser DevTools → Application → Cookies → auth cookie flags
- [ ] No auth tokens stored in `localStorage`, `sessionStorage`, or React state (see `never-store-tokens-in-localstorage.md`)

---

## 6. CSRF

- [ ] `SameSite=Lax` or `SameSite=Strict` on auth cookies (primary mitigation)
- [ ] `state` parameter included in authorization request and validated on callback
- [ ] State value is cryptographically random and stored in a short-lived HttpOnly cookie
- [ ] For state-mutating API endpoints: CSRF token or additional `Origin`/`Referer` check applied where `SameSite=Lax` is not sufficient

---

## 7. Secret handling

- [ ] `client_secret` is in a server-side env var (not committed to git, not in client code)
- [ ] `client_secret` is not in any `NEXT_PUBLIC_` env var
- [ ] No secrets in browser-side code, `localStorage`, or client-visible config
- [ ] Supabase `service_role` key (if used) is server-side only
- [ ] Embed JWT signing secret (if any) is server-side only — see `data-platform/best-practices/embed-never-ship-the-service-key.md`
- [ ] `.env` files are in `.gitignore`; no secrets in git history
- [ ] Secrets are rotatable without redeploying client-side code

---

## 8. Token lifetimes

- [ ] Access token lifetime: ≤ 1 hour (Supabase default [unverified])
- [ ] Refresh token rotation on every use: enabled
- [ ] Embed JWTs (if any): 5-15 minute expiry per `data-platform` embed-JWT rule
- [ ] No long-lived API tokens shared across multiple users or tenants
- [ ] `exp` > 30 min in any embed JWT issuance code flags the data-platform hook

---

## 9. Consent screen

- [ ] OAuth consent screen status: **Production** (not **Testing**) for external users
- [ ] App name, support email, and developer contact email are accurate
- [ ] Privacy policy and terms of service URLs provided (if required by Google)
- [ ] App logo uploaded (optional but improves user trust)

---

## 10. Environment separation

- [ ] Separate OAuth clients for development and production (different `client_id` + `client_secret`)
- [ ] Production OAuth client has no `localhost` redirect URIs
- [ ] Staging / preview environments use their own OAuth clients or are clearly scoped

---

## 11. Logout and revocation

- [ ] Logout calls the server-side `signOut()` / token revocation endpoint — not just a cookie clear
- [ ] All auth cookies cleared on logout
- [ ] User is redirected to a public page after logout (not a page that requires auth)
- [ ] Refresh token is revoked server-side (not just expired client-side)

---

## 12. Security review

- [ ] `ravenclaude-core/security-reviewer` sign-off obtained for:
  - [ ] OAuth client configuration
  - [ ] Token verification code
  - [ ] Session cookie configuration
  - [ ] Any embed JWT issuance code

---

## Provenance

Items derived from:
- OAuth 2.0 Security BCP [unverified — verify at datatracker.ietf.org]
- Google OAuth 2.0 documentation [unverified — verify at developers.google.com/identity/protocols/oauth2]
- Supabase Auth documentation [unverified — verify at supabase.com/docs/guides/auth]
- This plugin's `oauth-oidc-flow-design`, `session-and-token-management`, `protect-spa-and-api` skills and absolute best-practices

---

## See also

- Template: [`./auth-architecture-decision-record.md`](./auth-architecture-decision-record.md)
- Template: [`./supabase-google-sso-setup.md`](./supabase-google-sso-setup.md)
- Best-practice: [`../best-practices/use-authorization-code-pkce-never-implicit.md`](../best-practices/use-authorization-code-pkce-never-implicit.md)
- Best-practice: [`../best-practices/never-store-tokens-in-localstorage.md`](../best-practices/never-store-tokens-in-localstorage.md)
- Best-practice: [`../best-practices/validate-id-tokens-server-side.md`](../best-practices/validate-id-tokens-server-side.md)
