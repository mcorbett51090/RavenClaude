# OAuth 2.0 / OIDC + Google SSO — the protocol reference

> **Last reviewed:** 2026-06-03. Sources: Google Identity docs ("Verify the Google ID token", "OpenID Connect", "OAuth 2.0 for client-side web apps"), Supabase Auth docs ("Login with Google", `signInWithOAuth` reference), the OAuth 2.1 draft coverage (WorkOS / Pockit / Java Code Geeks migration write-ups), and OWASP (Session Management + CSRF cheat sheets) — all retrieved 2026-06-03. Refresh when: (a) OAuth 2.1 advances from draft to RFC, (b) Google changes its consent-screen / verification / token mechanics, or (c) Supabase changes its Google-provider or PKCE/session flow.
>
> Mark any positioning that you cannot re-confirm at build time `[verify-at-build]`.

## OAuth 2.0 vs OIDC — the one-line distinction

- **OAuth 2.0 is authorization** — it issues an **access token** that lets a client call an API *on a user's behalf*. It says nothing standard about *who the user is*.
- **OpenID Connect (OIDC)** is a thin **authentication** layer on top of OAuth 2.0. It adds the **ID token** — a signed JWT asserting *who the user is* (`sub`, `email`, etc.) — and a standard `/userinfo` endpoint. **"Sign in with Google" is OIDC.** `[verified 2026-06-03]`

**Rule of thumb:** if you want to *log a user in*, you want OIDC and the **ID token**. If you want to *call an API as the user*, you want the **access token**. Most SSO needs the ID token; don't use an access token as proof of identity.

## The flows — and which to use

| Flow | Use for | Status |
|---|---|---|
| **Authorization Code + PKCE** | **SPAs, native/mobile, and (in OAuth 2.1) all clients** | **Current recommendation.** `[verified 2026-06-03]` |
| **Authorization Code (confidential, client-secret)** | Server-side web apps / backends that can hold a secret | Current; **OAuth 2.1 also mandates PKCE here** |
| **Client Credentials** | Machine-to-machine (no user) | Current |
| **Device Authorization (device code)** | Input-constrained devices (TV, CLI) | Current |
| **Implicit** (`response_type=token`) | — | **DEPRECATED / removed in OAuth 2.1** `[verified 2026-06-03]` |
| **Resource Owner Password (ROPC)** | — | Discouraged / removed in OAuth 2.1 |

### Why Implicit is dead
The Implicit grant returned the access token directly in the **URL fragment**, where it lands in **browser history, server logs, and the `Referer` header**, cannot be sender-constrained, and — because it skips the token endpoint — **cannot use PKCE**. OAuth 2.1 removes it; Authorization Code + PKCE replaces it for every browser/SPA client. Modern browsers' CORS + `fetch` support makes Auth-Code + PKCE fully workable for SPAs. `[verified 2026-06-03 — WorkOS / Pockit OAuth 2.1 coverage]`

### Why PKCE everywhere (OAuth 2.1)
PKCE (Proof Key for Code Exchange) was optional in OAuth 2.0 (recommended for public clients). **OAuth 2.1 makes it mandatory for *every* client type, including confidential server apps that already hold a client secret** — because the client secret protects the *token endpoint* while PKCE protects the *authorization flow* against **authorization-code injection** (an attacker substituting their own code into the victim's session). Different attack, different defense; you want both. `[verified 2026-06-03]`

> **Status note:** OAuth 2.1 is still an **IETF Internet Draft** (`draft-ietf-oauth-v2-1`, early 2026) — but its security requirements (Implicit removed, PKCE mandatory) are **already enforced by Google, Microsoft, Auth0, Okta** and implemented in major auth servers. Treat them as current practice, not future. `[verified 2026-06-03]`

## The three tokens

| Token | What it is | Lifetime | Where it lives |
|---|---|---|---|
| **ID token** (OIDC) | Signed JWT asserting *who the user is* (`sub`, `email`, `iss`, `aud`, `exp`, `iat`, optional `nonce`, `hd`) | Short | Validated server-side, then discarded — **not** a session token |
| **Access token** | Bearer credential to call an API *as the user* | Short (minutes) | **In memory** on the client; never `localStorage` |
| **Refresh token** | Long-lived credential to mint new access tokens | Long (days), **rotated** | **HttpOnly + Secure + SameSite cookie** — JS can't read it |

**Token storage (OWASP, verified 2026-06-03):** the 2026 default for an OAuth-secured SPA is **short-lived access token in JavaScript memory** + **refresh token in an HttpOnly + Secure + SameSite cookie** set by the server. Never `localStorage`/`sessionStorage` — both are readable by any JS in the origin, so one XSS discloses every token. The HttpOnly cookie can't be read by JS or exfiltrated by an XSS payload; the browser sends it automatically to the refresh endpoint.

**CSRF (OWASP, verified 2026-06-03):** cookie-borne auth means cross-site requests carry the cookie automatically — so cookie auth **requires CSRF defense.** `SameSite=Lax`/`Strict` blocks most cross-site cookie sends; add an **anti-CSRF token on state-changing requests** as defense-in-depth for high-value operations.

## Google SSO specifics

### 1. Google Cloud OAuth client setup
In the **Google Cloud Console** → APIs & Services → Credentials:
- **Configure the OAuth consent screen** — app name, support email, scopes, authorized domains. External apps requesting sensitive/restricted scopes go through Google verification; **plain `openid email profile` SSO does not need verification** (keep scopes minimal to avoid it). `[verify-at-build]`
- **Create an OAuth 2.0 Client ID** (type: Web application) → you get a **client ID** and **client secret**.
- **Authorized redirect URIs** — the exact callback URL Google may redirect to after consent. **With Supabase this is the Supabase callback** (shape: `https://<project-ref>.supabase.co/auth/v1/callback`). The URI must match exactly. `[verified 2026-06-03 — Supabase "Login with Google"]`

### 2. Scopes — least privilege
Request **`openid email profile`** for plain "who is this user" SSO. Only add Gmail/Drive/Calendar scopes if a feature genuinely calls those Google APIs — broad scopes trigger Google's verification review, add consent-screen friction, and widen the blast radius of a leaked token.

### 3. ID-token validation (server-side — mandatory)
A Google ID token presented by the browser is **not** trustworthy until your server validates it. Verify **all** of:
- **Signature** — against Google's public keys at the `jwks_uri` from Google's OIDC discovery document. **These keys rotate** — honor the `Cache-Control` header; don't pin a key. `[verified 2026-06-03 — Google "Verify the Google ID token"]`
- **`iss`** ∈ { `accounts.google.com`, `https://accounts.google.com` }.
- **`aud`** == your app's OAuth **client ID** (prevents a token minted for a *different* app being replayed against yours).
- **`exp`** — not passed.
- **`nonce`** — matches the one you sent, when you set one (replay defense).
- Optionally **`hd`** — the Google Workspace hosted domain, if you restrict to an org.

`[verified 2026-06-03 — Google Identity "Verify the Google ID token" + "OpenID Connect"]`

## How Supabase Auth wraps the Google flow → Postgres `auth.uid()`

Supabase Auth sits in front of Google so you don't implement the OIDC dance yourself:

1. **Configure** — enable the Google provider in the Supabase dashboard, paste the Google **client ID + secret**, and add your app's callback to Supabase's **Redirect URL allow-list** (Authentication → URL Configuration). `[verified 2026-06-03]`
2. **Initiate** — the app calls `supabase.auth.signInWithOAuth({ provider: 'google', options: { redirectTo } })`. **`signInWithOAuth` supports the PKCE flow.** `[verified 2026-06-03 — Supabase JS reference]`
3. **Callback / code-exchange** — in server-side auth, the callback route calls **`exchangeCodeForSession`** to complete the PKCE flow and establish the session; Supabase sets the session (access + refresh) as cookies. `[verified 2026-06-03]`
4. **Session** — Supabase issues its **own session JWT** (it validates Google's tokens for you; the `provider_token` for calling Google APIs can be extracted from the session and stored securely if needed). `[verified 2026-06-03]`
5. **The RLS handoff** — Supabase's session JWT carries the user's `sub`, surfaced inside Postgres as **`auth.uid()`**. **This is the seam to the `data-platform` plugin:** its RLS policies key off `auth.uid()` to scope rows to the authenticated user/tenant. Authentication ends here; **authorization (which rows) is data-platform's lane** — see [`../CLAUDE.md`](../CLAUDE.md) §0. `[verified 2026-06-03]`

```
Google (OIDC, ID token)
   └─ Supabase Auth  ── signInWithOAuth (PKCE) → exchangeCodeForSession → session JWT (cookies)
        └─ Postgres: auth.uid()  ──seam──▶  data-platform RLS  (which rows?)
```

## The boundary this doc respects

Everything above is **authentication** — proving *who the user is*. **Authorization** — *what rows/tenant that identity may read* — is the `data-platform` plugin's RLS / embed-JWT lane. The `auth.uid()` claim is the contract between the two; this plugin produces it, data-platform consumes it.

## Refresh triggers

- OAuth 2.1 advances from draft to RFC (re-confirm "Implicit removed / PKCE mandatory" wording).
- Google changes consent-screen, verification, or ID-token mechanics.
- Supabase changes its Google-provider, PKCE, or session-cookie flow.

---

_Last reviewed: 2026-06-03 by `claude`. Flow-deprecation and Google/Supabase mechanics are re-verified before quoting to a client._
