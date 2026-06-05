# Auth-identity best-practice docs

Named, citable rules for the `auth-identity` plugin covering Google SSO, OAuth/OIDC flow design, session and token management, and the identity → data-authorization seam to the `data-platform` plugin. Each file is one rule — read, applied, and cited as a whole.

---

## Index

_15 rules. Each file is one named, citable rule; read and apply it whole._

| Doc | Status | Use when |
|---|---|---|
| [`prefer-managed-auth-over-rolling-your-own.md`](./prefer-managed-auth-over-rolling-your-own.md) | Pattern — strong default; deviate only with a documented, specific constraint and a security-reviewer sign-off. | You are deciding whether to use Supabase Auth / Clerk / Auth0 / Auth.js vs. implementing authentication from scratch. |
| [`use-authorization-code-pkce-never-implicit.md`](./use-authorization-code-pkce-never-implicit.md) | Absolute rule — the Implicit flow is deprecated by OAuth 2.0 Security BCP. No new implementation uses it. | You are choosing an OAuth/OIDC flow for a SPA, native app, or any browser-based client. |
| [`never-store-tokens-in-localstorage.md`](./never-store-tokens-in-localstorage.md) | Absolute rule — localStorage is XSS-exfiltratable. HttpOnly + Secure + SameSite cookies only. | You are deciding where to store access tokens, refresh tokens, or session identifiers in a web app. |
| [`validate-id-tokens-server-side.md`](./validate-id-tokens-server-side.md) | Absolute rule — verify signature + iss + aud + exp server-side before trusting any identity claim. | You are writing code that accepts an OIDC ID token or any JWT as proof of identity — especially from a mobile app or external caller. |
| [`authenticate-the-person-authorize-the-data-separately.md`](./authenticate-the-person-authorize-the-data-separately.md) | Absolute rule / Pattern — authentication proves identity; data authorization (which rows) is a separate layer owned by `data-platform` RLS. | You are designing access control for a multi-tenant app, implementing data queries for an authenticated user, or handing off from this plugin to the `data-platform` RLS layer. |
| [`csrf-defense-for-cookie-sessions.md`](./csrf-defense-for-cookie-sessions.md) | Absolute rule — every cookie-authenticated session uses SameSite=Lax plus an anti-CSRF token on state-changing requests. | Implementing or reviewing any session that uses cookies (HttpOnly or otherwise) for authentication state. |
| [`least-privilege-oauth-scopes.md`](./least-privilege-oauth-scopes.md) | Absolute rule — request only the OAuth scopes the current feature needs; over-broad scopes trigger consent-screen warnings and widen the blast radius of token theft. | Configuring an OAuth provider in Supabase Auth or directly; reviewing any OAuth scope list in a PR. |
| [`rotate-refresh-tokens-on-use.md`](./rotate-refresh-tokens-on-use.md) | Absolute rule — refresh tokens are rotated on every use and the old token is immediately invalidated; reuse of a previous token triggers full session revocation. | Designing or implementing the token refresh endpoint or configuring a managed auth provider's rotation settings. |
| [`revoke-tokens-on-logout.md`](./revoke-tokens-on-logout.md) | Absolute rule — logout must revoke the refresh token at the server before clearing client-side state; client-only cookie-clear is not logout. | Implementing or reviewing any logout flow. |
| [`apple-signin-secret-must-rotate.md`](./apple-signin-secret-must-rotate.md) | Absolute rule — Apple Sign In's JWT client secret expires in ≤180 days; calendar-based or automated rotation is required or every Apple login fails after the expiry date. | Adding Apple Sign In; post-launch operations for any app using Apple SSO. |
| [`pkce-verifier-is-one-use-only.md`](./pkce-verifier-is-one-use-only.md) | Absolute rule — a fresh PKCE code_verifier is generated for each authorization request; never reuse or store in localStorage; delete immediately after the token exchange. | Implementing the PKCE OAuth callback in a SPA or native app (not using a managed provider). |
| [`server-side-session-for-ssr-apps.md`](./server-side-session-for-ssr-apps.md) | Absolute rule — SSR apps (Next.js App Router, SvelteKit, Nuxt) exchange the OAuth code and set session cookies server-side; the access token never passes through the browser JS context. | Building or reviewing the OAuth callback route in any SSR framework with Supabase Auth or another provider. |
| [`passkeys-need-a-fallback.md`](./passkeys-need-a-fallback.md) | Absolute rule — passkey/WebAuthn login must offer at least one fallback (magic link, social SSO, or email+password); passkey-only locks out the majority of users in 2026. | Adding passkey authentication; designing the login method list. |
| [`never-hardcode-client-secrets.md`](./never-hardcode-client-secrets.md) | Absolute rule — OAuth client secrets, service role keys, and JWT signing keys live only in environment variables or a secret manager; never in source control. | Any PR that touches auth configuration, provider wiring, or server-side token logic. |
| [`magic-link-expiry-and-single-use.md`](./magic-link-expiry-and-single-use.md) | Absolute rule — magic links expire in ≤15 minutes and are invalidated on first use; long-lived or reusable links are reusable stolen credentials. | Adding or configuring magic-link / OTP passwordless authentication. |

---

## Escalation

All auth-related code changes (OAuth client config, session management, token verification, embed JWT issuance) route to `ravenclaude-core/security-reviewer` before production deploy.

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — the `auth-identity` plugin team constitution
- [`../../data-platform/best-practices/README.md`](../../data-platform/best-practices/README.md) — data-platform best-practices (RLS, embed JWT, tenant isolation)
- [`../../data-platform/best-practices/enforce-tenant-isolation-closest-to-data.md`](../../data-platform/best-practices/enforce-tenant-isolation-closest-to-data.md) — the foundational invariant this plugin's seam connects to
- [`../../data-platform/best-practices/issue-short-lived-jwts-for-embeds.md`](../../data-platform/best-practices/issue-short-lived-jwts-for-embeds.md) — the companion rule for embed tokens issued after authentication
- [`../../../docs/best-practices/_TEMPLATE.md`](../../../docs/best-practices/_TEMPLATE.md) — the section shape every doc here follows
