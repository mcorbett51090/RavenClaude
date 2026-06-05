---
scenario_id: 2026-06-05-embedding-jwt-scope-and-rls-mismatch
contributed_at: 2026-06-05
plugin: tableau
product: embedding-api
product_version: "Embedding API v3; Tableau Cloud 2025.2"
scope: version-specific
tags: [embedding-api, connected-apps, jwt, rls, 401, scopes]
confidence: high
reviewed: false
---

## Problem

A customer-facing portal embedded a per-tenant dashboard via the Embedding API v3 + a
Connected App (Direct Trust) JWT. Two failures landed together: (1) the viz threw a **401 at
load** even though the JWT "looked valid," and (2) once that was fixed, **a tenant briefly saw
another tenant's rows** — the auth succeeded but the data wasn't isolated. Auth and RLS were
built by two people in two places and drifted.

## Permissions context

- Tableau Cloud site admin created the Connected App and held the secret; the portal backend
  minted the JWT server-side.
- The published data source enforced RLS via an entitlements table + a row-level data policy
  keyed on a `tenant_id` entitlement. The embedded user's identity (the JWT `sub`) had to map
  to a `tenant_id` for the policy to filter.
- This is a **security-control** design — escalated the verdict to
  `ravenclaude-core/security-reviewer` per the team constitution.

## Attempts

- Tried: assuming the JWT only needed `sub` + the Connected App `iss`/`kid` claims → **401**.
  The token authenticated nothing because the **`scp` (scope) claim was missing**. For
  embedding, the JWT must carry `scp` as an **array** (even for a single entry), e.g.
  `["tableau:views:embed"]` `[verify-at-build]` against the current Access Scopes doc.
- Tried: adding `tableau:views:embed` but minting the token for a generic service account →
  auth passed but **every tenant resolved to the same user**, so the data policy filtered on
  one `tenant_id` and leaked across tenants.
- Tried: filtering the viz with a URL parameter / dashboard filter for tenant scoping → this is
  a **convenience filter, not a control** — trivially removable, exactly the anti-pattern the
  RLS-as-a-data-policy rule warns against.
- **Worked:** mint the JWT with **`sub` = the actual per-tenant embedded user** (so the data
  policy resolves the right `tenant_id` entitlement) **and** the `scp` array carrying
  `tableau:views:embed`. The JWT's identity and the RLS entitlement key are designed **as one
  unit**: the token says *who*, the data policy decides *which rows*, and the entitlement key is
  the join between them.

## Resolution

**Scope the JWT and the RLS entitlement together — they are two halves of one control.** Leaf
in [`../knowledge/governance-embedding-decision-trees.md`](../knowledge/governance-embedding-decision-trees.md)
(*Embedding auth* tree → Connected App / Direct Trust JWT) plus
[`../best-practices/embed-scope-the-jwt-and-rls-together.md`](../best-practices/embed-scope-the-jwt-and-rls-together.md).
Durable lessons:

- **A 401 on embed is usually a missing/malformed claim, not a secret problem.** Check the
  required registered claims first — `iss` (Connected App client ID), `kid` (secret ID), `sub`
  (the user to authenticate), `aud`, `exp`, and the **`scp` array** — before regenerating the
  secret. The `scp` value must be an array even with one entry. `[verify-at-build]` the exact
  required claim set against Tableau's Connected Apps / Embedding API auth docs each engagement.
- **A token that authenticates the right user against the wrong entitlement key still leaks.**
  The `sub` that the JWT authenticates must be the same identity the row-level data policy keys
  on. Test the isolation with two real tenants, not one — a single-tenant test passes while the
  cross-tenant leak hides.
- **Never substitute a URL/dashboard filter for RLS** in an embedding-isolation design — it is
  removable and is not a security boundary.

Cross-reference: the auth verdict and the threat model (where the secret is stored, what a
single-row cross-tenant leak costs) go to `ravenclaude-core/security-reviewer`; this note is the
field-level symptom (401 + leak) that should trigger the combined design from the start.

**Sources (verified 2026-06-05):**
- [Configure Connected Apps with Direct Trust — Tableau Help](https://help.tableau.com/current/online/en-us/connected_apps_direct.htm)
- [Access Scopes for Connected Apps — Tableau Help](https://help.tableau.com/current/online/en-us/connected_apps_scopes.htm)
- [Authentication and Embedding — Embedding API v3](https://help.tableau.com/current/api/embedding_api/en-us/docs/embedding_api_auth.html)
