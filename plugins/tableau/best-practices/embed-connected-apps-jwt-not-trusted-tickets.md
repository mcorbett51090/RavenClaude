# Embed with Connected Apps + a signed JWT, not trusted tickets or embedded credentials

**Status:** Absolute rule — trusted tickets and embedded service-account credentials are deprecated/insecure. The embedding-auth *verdict* escalates to `ravenclaude-core/security-reviewer`.

**Domain:** Embedding / authentication

**Applies to:** `tableau`

---

## Why this exists

The old way to embed an authenticated viz — **trusted tickets** — has the host server request a one-time ticket from Tableau and pass it in a URL; the alternative hack is to embed a shared service-account's credentials in the page. Both are now legacy/insecure `[verify-at-build]`: trusted tickets are being retired, and embedded credentials mean every viewer shares one identity (no per-user RLS, and the credential leaks into the browser). The modern, supported path is a **Connected App** with **direct-trust JWT**: the host app mints a **short-lived JWT** signed with the Connected App's secret (server-side), and the **Embedding API v3** exchanges it for a Tableau session as the named user. The secret never touches the browser, the token expires in minutes, and the session is the real user — so RLS applies per viewer. If you're choosing embedding auth and reaching for a trusted ticket, you've picked something that isn't on the supported tree.

## How to apply

Create + enable a Connected App at the site level, mint a short-lived JWT **server-side**, and hand it to the Embedding API v3.

```js
// SERVER-SIDE ONLY — the Connected App secret must never reach the browser.
import jwt from "jsonwebtoken";

const token = jwt.sign(
  {
    iss: CONNECTED_APP_CLIENT_ID, // the Connected App's client id
    sub: "amy@corp.com", // the Tableau username to embed AS (drives RLS)
    aud: "tableau",
    scp: ["tableau:views:embed"], // least-privilege scope
    jti: crypto.randomUUID(),
  },
  CONNECTED_APP_SECRET, // stored in a vault/env on the server, NOT in JS sent to the client
  {
    algorithm: "HS256",
    expiresIn: "5m", // SHORT-LIVED
    keyid: CONNECTED_APP_SECRET_ID,
    header: { iss: CONNECTED_APP_CLIENT_ID },
  },
);
```

```html
<!-- Browser: pass the server-minted token to the Embedding API v3 web component -->
<tableau-viz
  id="viz"
  src="https://prod.example.com/views/Finance/KPI"
  token="<%= serverMintedJwt %>"
></tableau-viz>
<script type="module" src="https://prod.example.com/javascripts/api/tableau.embedding.3.latest.min.js"></script>
```

**Do:**
- Create + **enable** the Connected App at the **site level** (a site/server-admin action) before any JWT will validate.
- Mint the JWT **server-side**; keep the secret in a vault/env, never in browser JS.
- Make tokens **short-lived** (minutes) and scope them least-privilege (`tableau:views:embed`).
- Set `sub` to the real Tableau user so per-viewer RLS applies — see the companion rule on binding scope to the RLS key.
- **Escalate the auth verdict to `ravenclaude-core/security-reviewer`**: where the JWT is minted, how the secret is stored, token lifetime, and the RLS binding.

**Don't:**
- Use **trusted tickets** for new embeds — they're legacy/being retired `[verify-at-build]`.
- Embed a shared service-account credential — one identity for all viewers kills per-user RLS and leaks the credential.
- Sign the JWT in client-side JavaScript — that ships the secret to every browser.

## Edge cases / when the rule does NOT apply

- **Truly public data** — a public/anon embed with no per-user auth and no RLS is fine *only* when the data is genuinely public for everyone; verify, don't assume.
- **Host already federates identity** — when the host app federates via your IdP and a full SSO session into Tableau is acceptable, **SAML/OIDC SSO** is a valid alternative to per-request JWTs (heavier, IdP-coupled).
- **Connected Apps require site-admin enablement** — if the Connected App isn't created/enabled at the site, the JWT won't validate; that's a `requires:` prerequisite, not a code bug.

## See also

- [`./embed-scope-the-jwt-and-rls-together.md`](./embed-scope-the-jwt-and-rls-together.md) — bind the JWT `sub`/scope to the RLS entitlement key
- [`./gov-rls-as-a-data-policy-not-a-hidden-filter.md`](./gov-rls-as-a-data-policy-not-a-hidden-filter.md) — the RLS the embedded session must respect
- [`../knowledge/governance-embedding-decision-trees.md`](../knowledge/governance-embedding-decision-trees.md) — `## Decision Tree: Embedding auth`
- [`../agents/tableau-admin.md`](../agents/tableau-admin.md) — owns this rule; escalates the verdict to `ravenclaude-core/security-reviewer`
- Tableau Help, "Connected Apps" (direct trust) + "Tableau Embedding API v3" `[verify-at-build]`

## Provenance

Codifies constitution house opinion #8 ("Embed with Connected Apps + JWT, never a trust ticket hack or embedded credentials") and the `tableau-admin` discipline #5. Grounded in Tableau Connected Apps (direct-trust JWT) and Embedding API v3 — re-verify JWT claim names, scopes, and the trusted-ticket deprecation status against current Tableau Help. The auth *verdict* is owned by `ravenclaude-core/security-reviewer`.

---

_Last reviewed: 2026-05-30 by `claude`_
