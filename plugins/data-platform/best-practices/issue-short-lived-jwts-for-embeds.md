# Issue short-lived, server-signed JWTs for dashboard embeds

**Status:** Absolute rule — embed tokens are 5-15 min, server-issued, and carry a signed `tenant_id` the viewer cannot influence.

**Domain:** Embed auth / JWT issuance

**Applies to:** `data-platform`

---

## Why this exists

A JWT is the carrier of the tenant boundary into the embed, so its issuance discipline is what makes the closeness-to-data invariant trustworthy. Long-lived tokens are an anti-pattern: stateless revocation otherwise requires a revocation list (operational overhead), and a reused "API token" gives every viewer the same scope. The token's `tenant_id` claim is the source-of-truth the RLS / `securityContext` layer scopes on — if the front-end can construct or edit it, the whole isolation model collapses. The plugin's hook flags `exp` > 30 min in issuance code precisely because this is the recurring break.

## How to apply

The host app's server issues the token after authenticating the session; the front-end only ever *requests* it and passes it to the embed.

```ts
// Server-side issuer — signing key from env, never inline; 5-15 min expiry
const token = jwt.sign(
  {
    sub: user.id,                 // subject
    tenant_id: session.tenantId,  // the boundary — from the authenticated session, NOT the URL
    iss: "app.example.com",       // issuer
    aud: "cube",                  // audience: which embed tool
  },
  process.env.JWT_SIGNING_SECRET, // env var, never hard-coded
  { expiresIn: "10m" },           // 5-15 min; refresh at ~80% of lifetime
);
```

**Do:**
- Carry `sub`, `tenant_id`, `iat`, `exp`, `iss`, `aud` on every embed JWT; add `allowed_dashboards` / `nonce` for defense in depth.
- Refresh from the host app's issuer endpoint at ~80% of token lifetime; rate-limit that endpoint (it is a DoS surface).
- Prefer **RS256 + JWKS** for productized SaaS with many tenants (rotate without coordinating); HS256 shared-secret is fine for a single SMB engagement.

**Don't:**
- Let `exp` exceed 30 minutes, or hard-code the signing key in source.
- Derive `tenant_id` from a URL/query parameter, or let front-end React code *construct* the JWT.
- Try to use app-issued JWTs for Power BI Embedded — it uses an Azure AD token via MSAL, not an app-issued one.

## Edge cases / when the rule does NOT apply

- **Power BI Embedded (App-Owns-Data)** — the "JWT" is the Azure AD access token acquired via MSAL with a service principal; tenant scoping is via DAX roles / `EffectiveIdentity`, so the 5-15 min app-issued-token rule doesn't apply verbatim.
- **Static (non-interactive) Metabase embeds** — a signed iframe URL covers the case; the short-lived-refresh pattern matters most for interactive/SDK embeds.
- **Internal admin-only dashboards** with no tenant axis — token still server-issued and short-lived, but there's no `tenant_id` boundary to carry.

## See also

- [`../knowledge/embedded-analytics-landscape-2026.md`](../knowledge/embedded-analytics-landscape-2026.md) — the 2026 embed-auth standard + per-tool patterns (Superset guest token, Cube Bearer, Metabase, Power BI)
- [`../knowledge/multi-tenant-rls-patterns.md`](../knowledge/multi-tenant-rls-patterns.md) — the `tenant_id` claim as the source-of-truth for the enforcement layer
- [`./enforce-tenant-isolation-closest-to-data.md`](./enforce-tenant-isolation-closest-to-data.md)

## Provenance

Distilled from `data-platform/CLAUDE.md` house opinion #4 and the §7 hook (flags `exp` > 30 min and inline secrets), the canonical claims/expiration/rotation/anti-pattern sections of the `jwt-embed-issuance` skill, and the JWT-claim-driven scoping section of `knowledge/multi-tenant-rls-patterns.md` (retrieved 2026-05-21).

---

_Last reviewed: 2026-05-30 by `claude`_
