# Never ship the service/signing key to the browser — the embed gets a short-lived, scoped token only

**Status:** Absolute rule — the front-end requests and forwards a token; it never holds the secret that mints tokens. Security-sensitive: any embed-auth change escalates to `ravenclaude-core/security-reviewer`.

**Domain:** Embed auth / secret handling

**Applies to:** `data-platform`

---

## Why this exists

The companion to short-lived JWTs ([`issue-short-lived-jwts-for-embeds.md`](./issue-short-lived-jwts-for-embeds.md)) is *where the secret lives*. The JWT signing secret (or Supabase `service_role` key, or Superset/Metabase embedding secret, or a Cube API secret) can mint a token for **any tenant** — it is the master key to the whole isolation model. If it reaches the browser — bundled into client JS, exposed via `NEXT_PUBLIC_*`, hard-coded in a React component, or passed as a long-lived web-component attribute — any viewer can open dev-tools, sign their own `tenant_id: 'someone-else'` token, and the RLS/`securityContext` layer will faithfully serve them another tenant's data, because the layer trusts a *correctly signed* claim. The front-end must only ever hold a token that is already scoped to one tenant and expires in minutes; the secret that signs it stays server-side in an env var. The plugin's hook flags inline secrets in `.tsx/.ts/.js` for exactly this reason.

## How to apply

Server holds the secret and mints the scoped token; the browser fetches that token and forwards it to the embed. Nothing secret crosses to the client.

```ts
// SERVER ONLY (e.g. /api/embed-token) — secret from env, scoped to the session's tenant.
export async function POST(req: Request) {
  const session = await getSession(req);                 // authenticated server-side
  const token = jwt.sign(
    { sub: session.userId, tenant_id: session.tenantId, aud: "cube" },
    process.env.CUBE_API_SECRET!,                         // secret stays here, never sent
    { expiresIn: "10m" }
  );
  return Response.json({ token });                         // only the SCOPED token leaves
}
```

```tsx
// CLIENT — fetches the already-scoped token; the secret is never in this bundle.
const { token } = await fetch("/api/embed-token").then(r => r.json());
<DashboardEmbed apiToken={token} />          // short-lived, single-tenant; safe to expose
// ❌ NEVER: process.env.NEXT_PUBLIC_CUBE_SECRET — a NEXT_PUBLIC_ secret is shipped to every browser
```

**Do:**
- Keep the signing/service key in a **server-side** env var; expose only the minted, tenant-scoped, short-lived token to the browser.
- Mint the token in a server route after authenticating the session; derive `tenant_id` from the session, not the request body.
- Use Supabase `anon` (RLS-bound) keys client-side, `service_role` server-side only.
- Rate-limit the token endpoint — it's a DoS surface — and prefer RS256+JWKS so you can rotate without redeploying clients.

**Don't:**
- Put any signing secret / `service_role` key / embedding secret in client JS, a `NEXT_PUBLIC_*` var, a `.tsx` component, or a web-component attribute.
- Let front-end code *construct* (rather than merely forward) the JWT.
- Ship a "convenience" long-lived API token shared across viewers — that is the service key by another name.

## Edge cases / when the rule does NOT apply

- **Power BI Embedded (App-Owns-Data)** — the embed token is an Azure AD access token acquired server-side via MSAL with a service principal; the principal's secret stays in Key Vault / server env, never in the SPA — same rule, different mint flow.
- **Static (non-interactive) Metabase embeds** — a server-signed iframe URL carries the scope; the signing secret still stays server-side, the URL is the only thing that reaches the browser.
- **Supabase `anon` key client-side** — that key is *designed* to be public **because** it is RLS-bound and cannot escalate; it is not the service key and this rule doesn't forbid it.

## See also

- [`./issue-short-lived-jwts-for-embeds.md`](./issue-short-lived-jwts-for-embeds.md) — the token's expiry/claims discipline this rule protects the secret behind
- [`./embed-lock-csp-frame-ancestors-and-sandbox.md`](./embed-lock-csp-frame-ancestors-and-sandbox.md) — the iframe/CSP boundary around the token
- [`./enforce-tenant-isolation-closest-to-data.md`](./enforce-tenant-isolation-closest-to-data.md) — why a forged signed claim defeats the whole model
- [`../skills/jwt-embed-issuance/SKILL.md`](../skills/jwt-embed-issuance/SKILL.md) — the canonical server-issuer flow
- [`../templates/jwt-issuer.ts`](../templates/jwt-issuer.ts) — the server-side issuer scaffold

## Provenance

Distilled from CLAUDE.md §7 hook (inline-secret detection in `.tsx/.ts/.js`), the `jwt-embed-issuance` skill (secret from env, never inline; front-end only requests the token), and the `embed-csp-and-iframe-sandboxing` skill ("pass short-lived tokens, never long-lived secrets" as web-component attributes). Security-sensitive — escalate to `ravenclaude-core/security-reviewer`. `[verify-at-build]` Supabase key names (`anon` / `service_role`) — confirm against current Supabase API-keys docs.

---

_Last reviewed: 2026-05-30 by `claude`_
