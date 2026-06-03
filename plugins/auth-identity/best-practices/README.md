# Auth-identity best-practice docs

Named, citable rules for the `auth-identity` plugin covering Google SSO, OAuth/OIDC flow design, session and token management, and the identity → data-authorization seam to the `data-platform` plugin. Each file is one rule — read, applied, and cited as a whole.

---

## Index

_5 rules. Each file is one named, citable rule; read and apply it whole._

| Doc | Status | Use when |
|---|---|---|
| [`prefer-managed-auth-over-rolling-your-own.md`](./prefer-managed-auth-over-rolling-your-own.md) | Pattern — strong default; deviate only with a documented, specific constraint and a security-reviewer sign-off. | You are deciding whether to use Supabase Auth / Clerk / Auth0 / Auth.js vs. implementing authentication from scratch. |
| [`use-authorization-code-pkce-never-implicit.md`](./use-authorization-code-pkce-never-implicit.md) | Absolute rule — the Implicit flow is deprecated by OAuth 2.0 Security BCP. No new implementation uses it. | You are choosing an OAuth/OIDC flow for a SPA, native app, or any browser-based client. |
| [`never-store-tokens-in-localstorage.md`](./never-store-tokens-in-localstorage.md) | Absolute rule — localStorage is XSS-exfiltratable. HttpOnly + Secure + SameSite cookies only. | You are deciding where to store access tokens, refresh tokens, or session identifiers in a web app. |
| [`validate-id-tokens-server-side.md`](./validate-id-tokens-server-side.md) | Absolute rule — verify signature + iss + aud + exp server-side before trusting any identity claim. | You are writing code that accepts an OIDC ID token or any JWT as proof of identity — especially from a mobile app or external caller. |
| [`authenticate-the-person-authorize-the-data-separately.md`](./authenticate-the-person-authorize-the-data-separately.md) | Absolute rule / Pattern — authentication proves identity; data authorization (which rows) is a separate layer owned by `data-platform` RLS. | You are designing access control for a multi-tenant app, implementing data queries for an authenticated user, or handing off from this plugin to the `data-platform` RLS layer. |

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
