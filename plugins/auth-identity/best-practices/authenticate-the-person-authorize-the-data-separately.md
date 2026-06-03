# Authenticate the person; authorize the data separately

**Status:** Absolute rule / Pattern — keep authentication (this plugin) and data authorization (data-platform RLS) as distinct, non-overlapping layers. A logged-in user is not an entitled-to-this-row user.

**Domain:** Auth/data boundary

**Applies to:** `auth-identity` (primary); `data-platform` (seam)

---

## Why this exists

Authentication and data authorization are often confused or collapsed into a single layer. The confusion causes security failures in both directions:

- **Over-granting:** a user is authenticated, so all data becomes accessible to them — no per-tenant or per-row scoping.
- **Under-granting / UX failure:** data-layer scoping is implemented in application code that doesn't fire consistently, resulting in access errors or incorrect data.
- **Maintenance failure:** the scoping logic is duplicated in application code, API middleware, and database queries — drift between copies causes bugs.

The correct model has exactly two layers:

| Layer | Question | Mechanism | Owned by |
|---|---|---|---|
| **Authentication** | "Who is this person?" | Google SSO → Supabase Auth → `auth.uid()` | `auth-identity` plugin |
| **Data authorization** | "Which rows can this person read?" | Postgres RLS via `auth.uid()` + `tenant_id` | `data-platform` plugin |

These layers are independent. A user can be:
- **Authenticated** but have no rows — new user, no tenant membership yet.
- **Authenticated** with one tenant's rows — the common case for B2B SaaS.
- **Authenticated** with admin access — can see more rows, but still scoped by the role-aware RLS policy.
- **Not authenticated** — the auth gate blocks them before they reach the data layer at all.

---

## The seam in practice

After this plugin establishes the user's identity:

1. `auth.uid()` is available in every Supabase Postgres query automatically (the JWT in the session cookie carries it).
2. The `data-platform` plugin's RLS policies use `auth.uid()` to scope rows:

```sql
-- data-platform's job — not this plugin's
CREATE POLICY "users see own tenant rows" ON orders
  FOR SELECT
  USING (
    tenant_id = (
      SELECT tenant_id FROM tenant_memberships
      WHERE user_id = auth.uid()
    )
  );
```

3. The application code does **not** add a `WHERE user_id = ?` clause as the load-bearing control. Application-code filters are acceptable as redundant defense-in-depth layers, but they are not the authoritative control.
4. For embedded analytics, the data-platform `gate-the-dashboard` skill issues a short-lived embed JWT that carries `tenant_id` — the embed tool's RLS / `securityContext` rules scope the data.

**This plugin does not implement RLS policies.** That would duplicate `data-platform`'s job and create the drift risk described above.

---

## How to apply

**In this plugin:**
- Establish `auth.uid()` via Supabase Auth or a verified OIDC session.
- Document the identity → RLS seam in the `auth-architecture-decision-record.md`.
- When a user asks "can I access this data?", the answer comes from the RLS policy, not from this plugin.

**Handoff to data-platform:**
- For Supabase / Postgres: apply the `data-platform/skills/rls-policy-authoring/SKILL.md`.
- For embedded BI: apply the `data-platform/skills/jwt-embed-issuance/SKILL.md` and `gate-the-dashboard` skill.
- For Cube / semantic layer: apply the `data-platform/skills/cube-schema-scaffolding/SKILL.md` (`securityContext` with `tenant_id`).

**Do:**
- Keep the auth gate (unauthenticated → redirect to login) in this plugin's middleware.
- Keep row-level scoping in the database RLS policy or semantic-layer `securityContext`.
- Document the boundary in the ADR so future engineers know which layer owns what.

**Don't:**
- Add `WHERE user_id = auth.uid()` clauses in application code as the load-bearing control (app-code filters drift; RLS is the authoritative layer).
- Implement multi-tenant data scoping in this plugin — that belongs in data-platform.
- Assume that a logged-in user should see all rows (unless you have explicitly designed a single-tenant, no-scoping architecture and documented it).

---

## Common failure mode: authentication as the only gate

```ts
// ❌ Wrong — authentication is the only control; all rows visible to all logged-in users
const { data: { user } } = await supabase.auth.getUser();
if (!user) redirect("/login");

// No RLS → user can read every order in the database
const { data: orders } = await supabase.from("orders").select("*");
```

```sql
-- ✅ Correct — RLS policy enforces tenant isolation at the database level
-- (data-platform's job, not auth-identity's)
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
CREATE POLICY "tenant_isolation" ON orders
  FOR SELECT
  USING (tenant_id = (
    SELECT tenant_id FROM tenant_memberships WHERE user_id = auth.uid()
  ));
-- Now `select("*")` from the app returns only the user's tenant's rows automatically
```

---

## Single-tenant exception

If the application is genuinely single-tenant (one set of users, no tenancy axis), document this explicitly in the ADR. A logged-in user can see all rows because there is only one tenant. The decision should be **active** ("we are single-tenant; no RLS tenant scoping is needed") not passive (RLS silently absent). When the application pivots to multi-tenant, the RLS layer must be added — having documented the assumption makes the migration scope obvious.

---

## See also

- Skill: [`../skills/authorization-rbac/SKILL.md`](../skills/authorization-rbac/SKILL.md) — application-layer role enforcement (authentication → roles → actions)
- Skill: [`../skills/gate-the-dashboard/SKILL.md`](../skills/gate-the-dashboard/SKILL.md) — the seam in action for embedded analytics
- data-platform: [`../../data-platform/skills/rls-policy-authoring/SKILL.md`](../../data-platform/skills/rls-policy-authoring/SKILL.md) — the data-authorization layer
- data-platform: [`../../data-platform/best-practices/enforce-tenant-isolation-closest-to-data.md`](../../data-platform/best-practices/enforce-tenant-isolation-closest-to-data.md) — the foundational data-platform invariant this seam connects to
- Template: [`../templates/auth-architecture-decision-record.md`](../templates/auth-architecture-decision-record.md) — where to document the boundary

## Provenance

Derived from the `data-platform` plugin's §3 house opinion ("the load-bearing tenant control is never at the rendering layer"), the `gate-the-dashboard` skill's two-layer contract, and the principle of defense-in-depth applied to multi-tenant SaaS architectures. The single-tenant exception is documented to prevent silent drift toward multi-tenant without the corresponding RLS layer.

---

_Last reviewed: 2026-06-03 by `claude`_
