# Design the JWT subject/scope and the RLS entitlement key together

**Status:** Absolute rule — a token that authenticates the right user against the wrong entitlement key still leaks. The combined design escalates to `ravenclaude-core/security-reviewer`.

**Domain:** Embedding / row-level security

**Applies to:** `tableau`

---

## Why this exists

Embedding auth and row-level security are two halves of one control, and teams build them in two places by two people, so they drift. The JWT says *who* the embedded session is (`sub`); the RLS data policy says *which rows that identity may see* (the entitlement key, e.g. `tenant_id`). If the host app mints a JWT for `amy@corp.com` but the viz filters on a `tenant_id` that Amy's session resolves to the *wrong* tenant — or the RLS keys off email while the entitlements table keys off an internal user id that doesn't match — you get a confidently-authenticated session showing another tenant's rows. The auth succeeded; the isolation failed. The only safe design treats the JWT `sub`/scope and the RLS entitlement key as **one bound contract**: the identity in the token is exactly the identity the entitlements table is keyed on, verified end-to-end.

## How to apply

Make the JWT `sub` resolve to the *same* identity the RLS policy keys on, and prove the binding with a cross-population test.

```
# Contract (write it down, review it as one unit):
#   JWT.sub          = amy@corp.com          ← the embedded Tableau user
#   Entitlements.key = user_name             ← what the RLS policy filters on
#   RLS predicate    : [Entitlements].[user_name] = USERNAME()
#   Binding          : USERNAME() inside Tableau == JWT.sub  (verify this resolves equal)

# If multi-tenant, the tenant must come from the TRUSTED token path, never a client param:
#   BAD : src=".../KPI?tenant=42"     ← caller-supplied; spoofable
#   GOOD: JWT.sub → Tableau user → Entitlements row → tenant   ← server-trusted chain
```

```js
// The sub is the load-bearing line: it is also the RLS key.
const token = jwt.sign(
  { iss: CLIENT_ID, sub: trustedUser.email /* == Entitlements.user_name */, aud: "tableau", scp: ["tableau:views:embed"] },
  SECRET, { algorithm: "HS256", expiresIn: "5m", keyid: SECRET_ID, header: { iss: CLIENT_ID } },
);
```

**Do:**
- Make the JWT `sub` resolve, inside Tableau, to the **exact identity** the entitlements table is keyed on.
- Derive every row-restricting value (tenant, region) from the **trusted token chain**, never from a client-supplied URL parameter.
- Test the binding by embedding **as two different populations** and confirming each sees only its own rows.
- Review the JWT design and the RLS policy **as one unit**, and **escalate the combined verdict to `ravenclaude-core/security-reviewer`**.

**Don't:**
- Pass a tenant/region as a viz URL parameter — that's caller-controlled and spoofable; it must come from the token.
- Key RLS on email while the entitlements table keys on an internal id (or vice versa) — the mismatch silently leaks.
- Sign off auth and RLS separately — a green auth test with no cross-population RLS test proves nothing.

## Edge cases / when the rule does NOT apply

- **Public/anon embeds** — no per-user token and no RLS, so there's no binding to design; only valid for genuinely public data.
- **Group-based RLS** — when RLS keys on `ISMEMBEROF()` rather than `USERNAME()`, the binding is JWT `sub` → user's group membership; the same end-to-end verification applies to the group resolution.
- **SAML SSO embeds** — the same rule holds with the IdP-asserted identity as the bound key instead of the JWT `sub`.

## See also

- [`./embed-connected-apps-jwt-not-trusted-tickets.md`](./embed-connected-apps-jwt-not-trusted-tickets.md) — how the JWT is minted in the first place
- [`./gov-rls-as-a-data-policy-not-a-hidden-filter.md`](./gov-rls-as-a-data-policy-not-a-hidden-filter.md) — the RLS half of the contract
- [`../knowledge/governance-embedding-decision-trees.md`](../knowledge/governance-embedding-decision-trees.md) — `## Decision Tree: Embedding auth` (the JWT→RLS-binding note)
- [`../agents/tableau-admin.md`](../agents/tableau-admin.md) — owns this rule; escalates the verdict to `ravenclaude-core/security-reviewer`
- Tableau Help, "Connected Apps" + "Row-level security options" `[verify-at-build]`

## Provenance

Codifies the `tableau-admin` discipline #5 ("the JWT's scopes and the embedded user's RLS entitlement must be designed together") and house opinions #6/#8. Grounded in the Connected Apps direct-trust JWT model + Tableau RLS — re-verify claim names and `USERNAME()` resolution against current Tableau Help. The combined *verdict* is owned by `ravenclaude-core/security-reviewer`.

---

_Last reviewed: 2026-05-30 by `claude`_
