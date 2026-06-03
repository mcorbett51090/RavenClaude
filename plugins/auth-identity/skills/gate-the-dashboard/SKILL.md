---
name: gate-the-dashboard
description: "Put the analytics dashboard and embedded BI behind login: app-shell login gate + session check + the handoff to data-platform's embed-JWT and RLS for per-user data isolation. The clearest expression of the auth-identity → data-platform seam."
---

# Skill: gate-the-dashboard

> **Invoked by:** any agent building or securing an analytics dashboard or embedded BI feature; `ravenclaude-core/security-reviewer` for any embed-auth or dashboard-access change.
>
> **When to invoke:** adding authentication to the analytics dashboard or any embedded BI component; designing the access-control handoff between the identity layer and the data isolation layer; auditing an existing dashboard that may be accessible without authentication.
>
> **Output:** dashboard login gate implemented + server-side session check + embed JWT issuance endpoint created + data-platform RLS seam documented + cross-boundary isolation verified.

---

## Two-layer contract (this skill's core job)

```
[User] -- Google SSO --> [auth-identity: authenticated session + auth.uid()]
                                    |
                           Dashboard access gate
                           (this skill: is user logged in? do they have dashboard role?)
                                    |
                           [App shell renders dashboard page]
                                    |
                           [Server issues short-lived embed JWT]
                           (tenant_id from authenticated session — NOT from URL)
                                    |
                           [data-platform: embed verifies JWT, RLS scopes rows]
                           (rls-policy-authoring + jwt-embed-issuance skills)
```

**Layer 1 (this skill):** prove who the person is and whether they can see the dashboard at all.
**Layer 2 (data-platform):** prove which data rows that person is allowed to see.

Do not duplicate the Layer 2 mechanics here. Reference them. They are owned by:
- `data-platform/skills/jwt-embed-issuance/SKILL.md` — short-lived embed JWT with `tenant_id`
- `data-platform/skills/rls-policy-authoring/SKILL.md` — Postgres RLS scoping
- `data-platform/best-practices/issue-short-lived-jwts-for-embeds.md` — embed JWT absolute rule
- `data-platform/best-practices/embed-never-ship-the-service-key.md` — secret handling rule

---

## Step 1 — Protect the dashboard route

The dashboard page must check authentication server-side before rendering any content or loading any embed:

```ts
// app/dashboard/page.tsx (Next.js App Router server component)
import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";

export default async function DashboardPage() {
  const cookieStore = cookies();
  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    { cookies: { getAll: () => cookieStore.getAll(), setAll: () => {} } },
  );

  // Server-side validation — not trusting the cookie without verification
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect("/login?next=/dashboard");

  // Optional: role check for dashboard-specific access
  const role = user.app_metadata?.role ?? "viewer";
  if (!["viewer", "editor", "admin"].includes(role)) {
    redirect("/unauthorized");
  }

  // Pass user identity to the dashboard shell — no raw tokens
  return <DashboardShell userId={user.id} userEmail={user.email} />;
}
```

If using Next.js middleware (recommended), the middleware already redirects unauthenticated users before the page renders. The Server Component check is defense-in-depth.

---

## Step 2 — Issue the embed JWT server-side

The dashboard embed requires a short-lived JWT with the user's `tenant_id` to scope data. This token is issued by a server-side API route **after** authentication is verified. The signing secret never leaves the server.

```ts
// app/api/embed-token/route.ts — conceptual; security-review before production
import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { SignJWT } from "jose";

export async function POST(request: Request) {
  const cookieStore = cookies();
  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    { cookies: { getAll: () => cookieStore.getAll(), setAll: () => {} } },
  );

  const { data: { user }, error } = await supabase.auth.getUser();
  if (!user || error) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  // Resolve tenant_id from the authenticated session — NOT from the request body
  const { data: membership } = await supabase
    .from("tenant_memberships")
    .select("tenant_id")
    .eq("user_id", user.id)
    .single();

  if (!membership?.tenant_id) {
    return NextResponse.json({ error: "No tenant" }, { status: 403 });
  }

  // Issue short-lived JWT — 10 min, server-signed, tenant-scoped
  // signing secret from env var — never hard-coded, never NEXT_PUBLIC_
  const secret = new TextEncoder().encode(process.env.EMBED_JWT_SECRET!);
  const token = await new SignJWT({
    sub: user.id,
    tenant_id: membership.tenant_id,
    iss: "app.example.com",
    aud: "cube", // or "superset" / "metabase" — the embed tool
  })
    .setProtectedHeader({ alg: "HS256" })
    .setIssuedAt()
    .setExpirationTime("10m") // 5-15 min per data-platform embed JWT rule
    .sign(secret);

  return NextResponse.json({ token });
}
```

> **Mandatory:** route this code to `ravenclaude-core/security-reviewer` before production. The `data-platform/skills/jwt-embed-issuance/SKILL.md` owns the full claim-shape specification (required: `sub`, `tenant_id`, `iat`, `exp`, `iss`, `aud`; recommended: `nonce`, `allowed_dashboards`).

---

## Step 3 — Client fetches the embed token and passes it to the embed

```tsx
// components/DashboardEmbed.tsx — client component
"use client";
import { useEffect, useState } from "react";

export function DashboardEmbed() {
  const [embedToken, setEmbedToken] = useState<string | null>(null);

  useEffect(() => {
    // Fetch the embed token from our server — it does NOT leave in the HTML
    fetch("/api/embed-token", { method: "POST" })
      .then((r) => r.json())
      .then(({ token }) => setEmbedToken(token));
  }, []);

  if (!embedToken) return <div>Loading dashboard…</div>;

  // Pass to your embed component (Cube SDK, Superset SDK, iframe URL param, etc.)
  // The token is short-lived and tenant-scoped — safe to pass to the embed
  return <YourEmbedComponent apiToken={embedToken} />;
  // ❌ NEVER: pass process.env.EMBED_JWT_SECRET or any signing secret here
}
```

---

## Step 4 — Data isolation (data-platform's responsibility)

Once the embed token is in the embed component, data isolation is enforced by the `data-platform` plugin:

- The embed tool (Cube, Superset, Metabase) verifies the JWT signature.
- It extracts `tenant_id` from the verified JWT.
- Postgres RLS policies or Cube `securityContext` rules scope all queries to that `tenant_id`.

The `auth-identity` plugin's job ends at Step 3. Do not implement RLS policies or Cube `securityContext` rules here. Refer to:
- `data-platform/skills/rls-policy-authoring/SKILL.md`
- `data-platform/skills/jwt-embed-issuance/SKILL.md`
- `data-platform/skills/cube-schema-scaffolding/SKILL.md`

---

## The generated `dashboard.html` (marketplace analytics dashboard)

For the RavenClaude marketplace's own analytics dashboard (`dashboard.html`), the same two-layer pattern applies:

1. The dashboard shell is only rendered after a successful Supabase Auth session check.
2. Any BI embed within `dashboard.html` receives a short-lived server-issued JWT scoped to the authenticated user's context.
3. The embed's data queries are gated by Postgres RLS — the user only sees their own data.

---

## Anti-patterns this skill flags

- Dashboard page renders without server-side authentication check (relying only on client-side redirect)
- Embed JWT issued without verifying the user's session first
- `tenant_id` in the embed JWT derived from the URL or request body (not from the authenticated session)
- Signing secret for embed JWT in a `NEXT_PUBLIC_` env var or in the client bundle
- Embed JWT with `exp` > 30 minutes (absolute rule — see data-platform embed JWT best-practice)
- Skipping the `data-platform` RLS layer and relying on app-code row filtering as the data isolation control
- Dashboard accessible without authentication in any environment (including staging and preview)
- No cross-boundary denial test — required before shipping (see data-platform's `rls-cross-tenant-test.sql` template)

---

## Verification checklist

- [ ] Dashboard route redirects to login when session is absent (server-side check)
- [ ] Embed token API route verifies session before issuing token
- [ ] `tenant_id` in embed JWT comes from server-side session, not from URL/request body
- [ ] `EMBED_JWT_SECRET` is in a server-side env var, not `NEXT_PUBLIC_`
- [ ] Embed JWT `exp` is 5-15 minutes
- [ ] data-platform's `rls-policy-authoring` skill has been applied (denial test passing)
- [ ] Cross-boundary denial test: user A cannot see user B's data
- [ ] Security review completed for embed token issuance code

---

## See also

- Skill: [`../protect-spa-and-api/SKILL.md`](../protect-spa-and-api/SKILL.md) — the underlying route-guard mechanics
- Skill: [`../authorization-rbac/SKILL.md`](../authorization-rbac/SKILL.md) — dashboard role check
- Best-practice: [`../../best-practices/authenticate-the-person-authorize-the-data-separately.md`](../../best-practices/authenticate-the-person-authorize-the-data-separately.md)
- data-platform: [`../../../data-platform/skills/jwt-embed-issuance/SKILL.md`](../../../data-platform/skills/jwt-embed-issuance/SKILL.md) — the canonical JWT claim shape and verification pattern for embeds
- data-platform: [`../../../data-platform/skills/rls-policy-authoring/SKILL.md`](../../../data-platform/skills/rls-policy-authoring/SKILL.md) — data-row scoping after the embed JWT is validated
- data-platform: [`../../../data-platform/best-practices/issue-short-lived-jwts-for-embeds.md`](../../../data-platform/best-practices/issue-short-lived-jwts-for-embeds.md) — the absolute rule this skill enforces
- data-platform: [`../../../data-platform/best-practices/embed-never-ship-the-service-key.md`](../../../data-platform/best-practices/embed-never-ship-the-service-key.md) — secret handling
- Security escalation: [`../../../ravenclaude-core/agents/security-reviewer.md`](../../../ravenclaude-core/agents/security-reviewer.md)
