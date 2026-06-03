---
name: authorization-rbac
description: "RBAC and ABAC in the application layer: defining roles and claims, mapping the authenticated identity to roles, enforcing roles in middleware and UI. The critical seam: row-level data scoping hands off to data-platform RLS via auth.uid(). Authentication proves identity; authorization controls access."
---

# Skill: authorization-rbac

> **Invoked by:** any agent designing access-control rules for a web app or API; `ravenclaude-core/security-reviewer` for any role-enforcement change.
>
> **When to invoke:** defining who can access what (roles, permissions); mapping Google-authenticated users to application roles; implementing admin-only sections; designing the handoff between this plugin's identity layer and data-platform's RLS layer.
>
> **Output:** role model documented + roles stored/retrieved + enforcement in middleware + UI conditional rendering + data-row seam to data-platform RLS documented.

---

## Boundary: authentication ≠ authorization ≠ data row access

Three distinct layers — keep them separate:

| Layer | What it answers | Owned by |
|---|---|---|
| **Authentication** | "Who is this person?" — verifies Google identity, establishes `auth.uid()` | This plugin (`auth-identity`) |
| **Application authorization** | "What is this person allowed to do?" — roles, permissions, feature flags | This skill |
| **Data authorization** | "Which rows can this person read?" — row-level scoping by tenant/org | `data-platform` plugin (`rls-policy-authoring` skill) |

A logged-in user is not automatically entitled to every row in the database. A user with the `admin` role in the app is not automatically entitled to another tenant's data. These are separate controls enforced at separate layers.

The best-practice `authenticate-the-person-authorize-the-data-separately.md` is an absolute rule in this plugin.

---

## RBAC vs ABAC

| Model | Structure | When to use |
|---|---|---|
| **RBAC** (Role-Based Access Control) | User → Role → Permissions. Roles are pre-defined (admin, editor, viewer). | Most web apps. Simple, auditable, easy to reason about. |
| **ABAC** (Attribute-Based Access Control) | Access based on attributes of the user, resource, and environment. More flexible, more complex. | When roles are insufficient — e.g., "can edit documents they own" or "can access based on department + resource tag". |
| **ReBAC** (Relationship-Based) | Access based on graph relationships (user owns resource, is member of group). | Very fine-grained access (Google Zanzibar pattern). Complex; usually overkill for SMB apps. |

**Default to RBAC.** Add ABAC rules only when a concrete access requirement cannot be expressed as a role.

---

## Storing roles

### Option A — Supabase custom claims / user metadata (recommended)

Store roles in Supabase Auth's `user_metadata` or `app_metadata`. `app_metadata` is server-editable only (not alterable by the user):

```sql
-- Set role server-side (admin action only — never let the user set their own app_metadata)
-- Supabase Admin API or a server-side function:
UPDATE auth.users
SET raw_app_meta_data = raw_app_meta_data || '{"role": "admin"}'::jsonb
WHERE id = '<user_id>';
```

Read in a Server Component or API route:

```ts
const { data: { user } } = await supabase.auth.getUser();
const role = user?.app_metadata?.role ?? "viewer"; // default to lowest privilege
```

[unverified — confirm `app_metadata` write behavior in current Supabase Auth API]

### Option B — Roles table in the application database

For complex role models (multiple roles per user, org-scoped roles):

```sql
-- Roles table — created once per environment
CREATE TABLE user_roles (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  role        text NOT NULL CHECK (role IN ('admin', 'editor', 'viewer')),
  created_at  timestamptz DEFAULT now(),
  UNIQUE(user_id, role)
);

-- RLS: users can read their own roles; only admins can write
ALTER TABLE user_roles ENABLE ROW LEVEL SECURITY;
CREATE POLICY "users can read own roles" ON user_roles
  FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "admins can manage roles" ON user_roles
  USING (EXISTS (
    SELECT 1 FROM user_roles r2
    WHERE r2.user_id = auth.uid() AND r2.role = 'admin'
  ));
```

### Option C — Roles in the JWT (custom claims)

Embed roles in the Supabase JWT via a custom claims function [unverified — Supabase custom JWT claims feature; verify in current docs]:

```sql
-- Supabase SQL editor: custom claim function
CREATE OR REPLACE FUNCTION public.custom_access_token_hook(event jsonb)
RETURNS jsonb AS $$
DECLARE
  claims jsonb;
  user_role text;
BEGIN
  SELECT role INTO user_role FROM public.user_roles WHERE user_id = (event->>'userId')::uuid LIMIT 1;
  claims := event->'claims';
  claims := jsonb_set(claims, '{app_role}', to_jsonb(coalesce(user_role, 'viewer')));
  RETURN jsonb_set(event, '{claims}', claims);
END;
$$ LANGUAGE plpgsql;
```

This embeds the role in the JWT so API routes can read it without a database round-trip. Route to `ravenclaude-core/security-reviewer` — custom claim functions are security-critical.

---

## Enforcing roles in Next.js middleware

```ts
// middleware.ts — role-based route protection
// Assumes role is in user.app_metadata.role (Option A)
import { createServerClient } from "@supabase/ssr";
import { NextResponse } from "next/server";

const ADMIN_PATHS = ["/admin", "/admin/:path*"];
const EDITOR_PATHS = ["/edit/:path*"];

export async function middleware(request) {
  // ... (session setup from protect-spa-and-api skill)
  const { data: { user } } = await supabase.auth.getUser();
  const role = user?.app_metadata?.role ?? "viewer";

  const path = request.nextUrl.pathname;

  if (ADMIN_PATHS.some((p) => path.startsWith(p.replace("/:path*", ""))) && role !== "admin") {
    return NextResponse.redirect(new URL("/unauthorized", request.url));
  }

  if (EDITOR_PATHS.some((p) => path.startsWith(p.replace("/:path*", ""))) && !["admin", "editor"].includes(role)) {
    return NextResponse.redirect(new URL("/unauthorized", request.url));
  }

  return NextResponse.next();
}
```

---

## Enforcing roles in API routes

Never rely on UI-only gating — API routes must check roles independently:

```ts
// app/api/admin/route.ts
export async function DELETE(request: Request) {
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return new Response("Unauthorized", { status: 401 });

  const role = user.app_metadata?.role;
  if (role !== "admin") return new Response("Forbidden", { status: 403 });

  // proceed with admin action
}
```

---

## Conditional rendering in the UI

```tsx
// components/AdminPanel.tsx
"use client";
import { useEffect, useState } from "react";
import { createClient } from "@/lib/supabase/client";

export function AdminPanel() {
  const [isAdmin, setIsAdmin] = useState(false);
  const supabase = createClient();

  useEffect(() => {
    supabase.auth.getUser().then(({ data: { user } }) => {
      setIsAdmin(user?.app_metadata?.role === "admin");
    });
  }, [supabase]);

  if (!isAdmin) return null; // UI gating only — API must enforce independently
  return <div>Admin controls</div>;
}
```

**UI gating alone is not a security control.** API routes must enforce roles regardless of what the UI renders.

---

## The identity → RLS seam (data authorization handoff)

Once the user's identity and application role are established, data-row scoping is the `data-platform` plugin's responsibility:

1. `auth.uid()` from the Supabase JWT is available in Postgres RLS policies automatically — the Supabase client passes the JWT in every query.
2. The `data-platform/rls-policy-authoring` skill defines policies like:
   ```sql
   -- Users can only read rows belonging to their tenant
   CREATE POLICY "tenant_isolation" ON orders
     FOR SELECT USING (tenant_id = (
       SELECT tenant_id FROM tenant_memberships WHERE user_id = auth.uid()
     ));
   ```
3. The `auth-identity` plugin's job ends at establishing `auth.uid()`. The RLS policy determines which rows that user can read.

**Never duplicate RLS logic in application code** as the load-bearing control. App-code row filters are acceptable as redundant defense-in-depth layers, but the authoritative control is the database RLS policy. See `data-platform/best-practices/enforce-tenant-isolation-closest-to-data.md`.

---

## Anti-patterns this skill flags

- Checking roles only in UI components and not in API routes — API routes must enforce independently
- Storing roles in `user_metadata` (user-editable) instead of `app_metadata` (server-only) [unverified — confirm Supabase metadata editability]
- Admin-role check that accepts any truthy `role` value instead of explicitly checking `role === 'admin'`
- Using UI-rendered role gating as the sole data-access control — RLS must be the load-bearing layer
- No default role — always assign the least-privilege role (`viewer`) if none is set
- Roles stored in localStorage or client-side state — read from server-side session only
- Hard-coding `user.id` in a URL parameter to determine which data to show — derive tenant from the authenticated session, not the URL

---

## See also

- Skill: [`../protect-spa-and-api/SKILL.md`](../protect-spa-and-api/SKILL.md) — route guards that this skill extends with role checks
- Skill: [`../gate-the-dashboard/SKILL.md`](../gate-the-dashboard/SKILL.md) — dashboard-specific role gate + RLS handoff
- Best-practice: [`../../best-practices/authenticate-the-person-authorize-the-data-separately.md`](../../best-practices/authenticate-the-person-authorize-the-data-separately.md)
- data-platform: [`../../../data-platform/skills/rls-policy-authoring/SKILL.md`](../../../data-platform/skills/rls-policy-authoring/SKILL.md) — the data-row authorization layer that follows this skill
- Security escalation: [`../../../ravenclaude-core/agents/security-reviewer.md`](../../../ravenclaude-core/agents/security-reviewer.md)
