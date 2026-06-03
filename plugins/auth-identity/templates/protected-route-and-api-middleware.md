# Template: Protected route and API middleware patterns

> Conceptual code patterns for protecting Next.js routes and API handlers with session-based authentication.
> All snippets are illustrative — **route to `ravenclaude-core/security-reviewer` before production deploy.**
>
> Prerequisites: Google SSO configured (see `supabase-google-sso-setup.md`), Supabase client helpers in `lib/supabase/`.

---

## Pattern 1 — Next.js Middleware (global route guard)

Runs before every matched request. The recommended primary protection layer.

```ts
// middleware.ts (project root)
import { createServerClient } from "@supabase/ssr";
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// Public paths that do not require authentication
const PUBLIC_PATHS = [
  "/",
  "/login",
  "/auth/callback",
  "/auth/error",
  "/api/health",    // public health check endpoint
];

export async function middleware(request: NextRequest) {
  let response = NextResponse.next({ request: { headers: request.headers } });

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll: () => request.cookies.getAll(),
        setAll: (cookiesToSet) => {
          cookiesToSet.forEach(({ name, value }) =>
            request.cookies.set(name, value),
          );
          response = NextResponse.next({ request: { headers: request.headers } });
          cookiesToSet.forEach(({ name, value, options }) =>
            response.cookies.set(name, value, options),
          );
        },
      },
    },
  );

  // IMPORTANT: use getUser(), not getSession().
  // getUser() validates the JWT server-side; getSession() trusts the cookie without verification.
  const {
    data: { user },
  } = await supabase.auth.getUser();

  const path = request.nextUrl.pathname;
  const isPublic = PUBLIC_PATHS.some(
    (p) => path === p || path.startsWith(p + "/"),
  );

  if (!user && !isPublic) {
    const redirectUrl = request.nextUrl.clone();
    redirectUrl.pathname = "/login";
    // Validate next is a relative path — prevent open redirect
    if (path.startsWith("/") && !path.startsWith("//")) {
      redirectUrl.searchParams.set("next", path);
    }
    return NextResponse.redirect(redirectUrl);
  }

  return response;
}

export const config = {
  // Skip static assets and Next.js internals
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
```

---

## Pattern 2 — Role-based middleware extension

Extend Pattern 1 with role checks for specific path prefixes.

```ts
// middleware.ts — extended with role gating
// Assumes role is in user.app_metadata.role (server-editable only)
// See authorization-rbac skill for role storage options.

const ADMIN_PREFIX = "/admin";
const EDITOR_PREFIX = "/edit";

// Inside the middleware function, after user check:
if (user) {
  const role = (user.app_metadata?.role as string) ?? "viewer";

  if (path.startsWith(ADMIN_PREFIX) && role !== "admin") {
    return NextResponse.redirect(new URL("/unauthorized", request.url));
  }

  if (
    path.startsWith(EDITOR_PREFIX) &&
    role !== "admin" &&
    role !== "editor"
  ) {
    return NextResponse.redirect(new URL("/unauthorized", request.url));
  }
}
```

---

## Pattern 3 — Server Component page guard (defense-in-depth)

Per-page protection for App Router Server Components. Middleware is the primary layer; this is defense-in-depth.

```tsx
// app/dashboard/page.tsx
import { redirect } from "next/navigation";
import { createServerSupabase } from "@/lib/supabase/server";

export default async function DashboardPage() {
  const supabase = createServerSupabase();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    redirect("/login?next=/dashboard");
  }

  return <DashboardContent userId={user.id} />;
}
```

---

## Pattern 4 — Protected API route (session cookie)

For API routes called from the same origin (browser sends session cookie automatically).

```ts
// app/api/protected/route.ts
import { createServerSupabase } from "@/lib/supabase/server";
import { NextResponse } from "next/server";

export async function GET() {
  const supabase = createServerSupabase();
  const {
    data: { user },
    error,
  } = await supabase.auth.getUser();

  if (!user || error) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  // Role check for admin-only endpoints
  const role = user.app_metadata?.role ?? "viewer";
  if (role !== "admin") {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 });
  }

  // user.id == auth.uid() — Supabase RLS applies automatically to all queries
  const { data } = await supabase.from("sensitive_data").select("*");
  return NextResponse.json(data);
}
```

---

## Pattern 5 — Protected API route (Bearer token, external callers)

For API routes called from other services (M2M) or a mobile app that sends the Supabase JWT as a Bearer token.

```ts
// app/api/external/route.ts
import { createClient } from "@supabase/supabase-js";
import { NextResponse } from "next/server";

export async function GET(request: Request) {
  const authHeader = request.headers.get("Authorization");
  if (!authHeader?.startsWith("Bearer ")) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const jwt = authHeader.slice(7);

  // Validate the Supabase JWT by creating an anon client with the user's token
  // Supabase will validate signature + exp + iss server-side
  // [unverified — confirm this pattern in current Supabase docs]
  const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    { global: { headers: { Authorization: `Bearer ${jwt}` } } },
  );

  const {
    data: { user },
    error,
  } = await supabase.auth.getUser();

  if (!user || error) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  // Proceed — user is verified
  return NextResponse.json({ userId: user.id });
}
```

> **Security note:** for non-Supabase JWT verification (e.g., a Google ID token), use the `jose` library with JWKS validation. See `protect-spa-and-api` skill for the full pattern. Always route to `ravenclaude-core/security-reviewer` before production.

---

## Pattern 6 — Login page with post-login redirect

```tsx
// app/login/page.tsx
import { GoogleSignInButton } from "@/components/GoogleSignInButton";
import { createServerSupabase } from "@/lib/supabase/server";
import { redirect } from "next/navigation";

export default async function LoginPage({
  searchParams,
}: {
  searchParams: { next?: string };
}) {
  const supabase = createServerSupabase();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  // Already logged in — send to dashboard
  if (user) redirect(searchParams.next ?? "/dashboard");

  return (
    <main>
      <h1>Sign in</h1>
      <GoogleSignInButton next={searchParams.next} />
    </main>
  );
}
```

---

## Security notes

- Use `supabase.auth.getUser()` (server-side JWT validation), not `supabase.auth.getSession()` (trusts unverified cookie).
- API routes must enforce auth independently of middleware — middleware can be bypassed by direct API calls.
- Validate `next` redirect parameters are relative paths on your own domain — prevent open redirect.
- `app_metadata` is server-editable only (not modifiable by the user). Use it for roles, not `user_metadata`. [unverified — confirm in current Supabase Auth docs]
- 401 for missing/invalid authentication; 403 for authenticated but insufficient authorization.
- All patterns above use the `anon` key (RLS-bound, safe for client use), not the `service_role` key.

---

## See also

- Skill: [`../skills/protect-spa-and-api/SKILL.md`](../skills/protect-spa-and-api/SKILL.md)
- Skill: [`../skills/authorization-rbac/SKILL.md`](../skills/authorization-rbac/SKILL.md)
- Template: [`./supabase-google-sso-setup.md`](./supabase-google-sso-setup.md)
- Template: [`./oidc-client-config-checklist.md`](./oidc-client-config-checklist.md)
