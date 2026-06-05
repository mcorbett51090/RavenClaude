---
name: embedding-connected-apps-jwt
description: A step-by-step setup for secure Tableau embedding with a Connected App (Direct Trust) + a server-minted JWT and the Embedding API v3 — minting the right claims, scoping the token, and binding the JWT identity to the RLS entitlement key. Use when embedding a viz in an app with per-user or per-tenant data isolation. The auth verdict escalates to ravenclaude-core/security-reviewer.
---

# Embedding with Connected Apps + JWT (Direct Trust)

> **Owner:** `tableau-admin` (primary). **Security verdict:** escalates to
> `ravenclaude-core/security-reviewer` — this is an access control, not a convenience feature.
> **Grounded in:** [`../../knowledge/governance-embedding-decision-trees.md`](../../knowledge/governance-embedding-decision-trees.md)
> *Embedding auth* tree + [`../../best-practices/embed-connected-apps-jwt-not-trusted-tickets.md`](../../best-practices/embed-connected-apps-jwt-not-trusted-tickets.md)
> + [`../../best-practices/embed-scope-the-jwt-and-rls-together.md`](../../best-practices/embed-scope-the-jwt-and-rls-together.md).

A repeatable procedure for the **supported, modern** embedding-auth path: a **Connected App**
(Direct Trust) on the Tableau site, a **JWT minted server-side** by your application, and the
**Embedding API v3** web component rendering the viz. It replaces deprecated/insecure **trusted
tickets** and embedded service-account credentials.

## When to use

Embedding a Tableau viz in a customer-facing or internal app where users authenticate through
*your* app and must see only *their* data (per-user or per-tenant isolation). Not for a public,
unauthenticated, all-data viz (that needs no JWT).

## The hard rule before you start

**The JWT identity and the RLS entitlement key are ONE design, built together.** A token that
authenticates the right user against the wrong entitlement key still leaks (see the scenario
`2026-06-05-embedding-jwt-scope-and-rls-mismatch.md`). Decide the entitlement key (`tenant_id`,
`region`, `customer_id`) and how the JWT `sub` maps to it **before** writing any code.

## Steps

1. **Create the Connected App (Direct Trust) on the Tableau site.** A **site/server admin**
   creates it (Settings → Connected Apps → New → Direct Trust) and **enables** it. Capture the
   **client ID** (`iss`), generate a **secret**, and capture the **secret ID** (`kid`). The
   secret is shared between Tableau and your app — store it in a secret manager, **never** in
   committed config or client-side code. `[verify-at-build]` the exact UI path against current
   Tableau Help.
2. **Decide the RLS design in parallel.** The published data source enforces row-level security
   via an entitlements table + a row-level **data policy** keyed on the entitlement key, and the
   JWT `sub` must resolve to that key. (RLS mechanism choice → the *RLS mechanism* tree; the
   data-policy approach is a **Data Management** add-on `[verify-at-build]`.)
3. **Mint the JWT server-side** with the required claims:
   - `iss` = Connected App **client ID**
   - `kid` = **secret ID** (in the JWT header), signed (HS256) with the **secret value**
   - `sub` = **the actual per-user / per-tenant identity** (so the data policy resolves the right
     rows — *not* a shared service account)
   - `aud` = `"tableau"` `[verify-at-build]`
   - `exp` = short-lived (minutes); also `jti` / `iat` as required
   - **`scp` = an ARRAY** of scopes — for embedding, `["tableau:views:embed"]` (add
     `tableau:views:embed_authoring` etc. only if needed). The scope claim **must be an array
     even for a single entry.** `[verify-at-build]` the exact required/allowed scopes against the
     Access Scopes for Connected Apps doc each engagement.
4. **Render with the Embedding API v3 web component.** Load the v3 library and use the
   `<tableau-viz>` component, passing the minted JWT as the token. The token authenticates the
   embedded session; the viz inherits the published data source's RLS. `[verify-at-build]` the
   current component attribute names.
5. **Test isolation with TWO real identities, not one.** A single-tenant test passes while a
   cross-tenant leak hides. Confirm tenant A cannot see tenant B's rows, and that an absent /
   wrong `sub` fails closed.
6. **Escalate the verdict to `ravenclaude-core/security-reviewer`** with the threat model: who
   the populations are, the entitlement key, where the secret is stored and how it's rotated,
   token lifetime, and what a single-row cross-tenant leak would cost.

## Troubleshooting (field-tested)

- **401 at viz load** → almost always a missing/malformed **claim**, not the secret. Check `iss`
  / `kid` / `sub` / `aud` / `exp` and that **`scp` is an array**, before regenerating anything.
- **Auth works but data leaks across tenants** → the `sub` doesn't map to the entitlement key
  (often a shared service-account `sub`). Mint per-tenant; re-test with two tenants.
- **Tempted to scope with a URL/dashboard filter** → that's a convenience filter, not a control;
  it's removable. Use the RLS data policy.
- **"Connected App secret invalid"** → confirm the Connected App is **enabled** at the site level
  and the `kid` matches the secret you signed with.

## Output

```
Embedding design: <where the viz is embedded; per-user or per-tenant isolation>
Connected App: <client ID (iss), secret ID (kid) — secret in: <secret manager ref>>
JWT claims: <sub mapping to entitlement key; scp array; exp lifetime>
RLS binding: <entitlements table + data-policy key; how sub → key resolves>
Isolation test: <two-identity result — A cannot see B; wrong sub fails closed>
Security escalation: <threat model handed to ravenclaude-core/security-reviewer>
```

Follow the team **Output Contract** + the cross-plugin **Structured Output Protocol**. Never
ship the secret in any artifact; bundle a **reference**, not a literal.

## See also

- [`../../knowledge/governance-embedding-decision-trees.md`](../../knowledge/governance-embedding-decision-trees.md) — the *Embedding auth* + *RLS mechanism* trees
- [`../../scenarios/2026-06-05-embedding-jwt-scope-and-rls-mismatch.md`](../../scenarios/2026-06-05-embedding-jwt-scope-and-rls-mismatch.md) — the 401 + leak field note
- [`../../templates/embedding-design-spec.md`](../../templates/embedding-design-spec.md) — the design template
- [`../../agents/tableau-admin.md`](../../agents/tableau-admin.md) — the owning agent

## Sources (verified 2026-06-05)

- [Configure Connected Apps with Direct Trust — Tableau Help](https://help.tableau.com/current/online/en-us/connected_apps_direct.htm)
- [Access Scopes for Connected Apps — Tableau Help](https://help.tableau.com/current/online/en-us/connected_apps_scopes.htm)
- [Authentication and Embedding — Embedding API v3](https://help.tableau.com/current/api/embedding_api/en-us/docs/embedding_api_auth.html)
- [Tableau connected-apps JWT samples (GitHub)](https://github.com/tableau/connected-apps-jwt-samples)
