---
name: protect-spa-and-api
description: "Protect a React/Next.js SPA with route guards and middleware, and protect an API with token-verification middleware (signature + iss + aud + exp). Covers CORS configuration and CSRF defense. Applies to both the web-app and the API/backend targets."
---

# Skill: protect-spa-and-api

> **Invoked by:** any agent implementing route protection for a Next.js app or API token verification; `ravenclaude-core/security-reviewer` for any auth middleware change.
>
> **When to invoke:** adding protected routes to a Next.js app; implementing API token verification; hardening an existing app against CORS or CSRF vulnerabilities; onboarding a new service to require authentication.
>
> **Output:** Next.js middleware route guard + API token-verification middleware + CORS config + CSRF defense + verification checklist.

---

## Boundary

This skill protects routes and APIs using the authenticated identity established by `google-sso-setup` and `session-and-token-management`. Authorization (which authenticated user can access which resource) is handled by the `authorization-rbac` skill and, for data rows, by the `data-platform` plugin's `rls-policy-authoring` skill. Security-sensitive code routes to `ravenclaude-core/security-reviewer` before production deploy.

---

## Protecting the Next.js web app

### Approach A — Next.js Middleware (recommended for App Router)

`middleware.ts` at the project root runs on every matched request, before rendering. The best place to enforce authentication globally.

```ts
// middleware.ts — conceptual; security-review before production
import { createServerClient } from "@supabase/ssr";
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// Routes that don't require authentication
const PUBLIC_PATHS = ["/", "/login", "/auth/callback", "/auth/error"];

export async function middleware(request: NextRequest) {
  let response = NextResponse.next({ request: { headers: request.headers } });

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll: () => request.cookies.getAll(),
        setAll: (cs) => {
          cs.forEach(({ name, value }) => request.cookies.set(name, value));
          response = NextResponse.next({ request: { headers: request.headers } });
          cs.forEach(({ name, value, options }) =>
            response.cookies.set(name, value, options),
          );
        },
      },
    },
  );

  // getUser() validates the session token server-side — do not use getSession() here
  // getSession() trusts the cookie without server-side validation
  const { data: { user } } = await supabase.auth.getUser();

  const path = request.nextUrl.pathname;
  const isPublic = PUBLIC_PATHS.some((p) => path === p || path.startsWith(p + "/"));

  if (!user && !isPublic) {
    const redirectUrl = request.nextUrl.clone();
    redirectUrl.pathname = "/login";
    redirectUrl.searchParams.set("next", path);
    return NextResponse.redirect(redirectUrl);
  }

  return response;
}

export const config = {
  matcher: [
    // Run on all paths except static files and _next internals
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
```

> **Important:** use `supabase.auth.getUser()` (makes a network call to validate the JWT server-side), not `supabase.auth.getSession()` (trusts the cookie without validation). [unverified — confirm this distinction in current Supabase Auth docs]

### Approach B — Server Component redirect

For per-page protection in App Router Server Components:

```ts
// app/dashboard/page.tsx
import { redirect } from "next/navigation";
import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";

export default async function DashboardPage() {
  const cookieStore = cookies();
  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    { cookies: { getAll: () => cookieStore.getAll(), setAll: () => {} } },
  );

  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect("/login?next=/dashboard");

  return <div>Dashboard for {user.email}</div>;
}
```

Use Middleware (Approach A) for broad protection + Server Component checks for fine-grained page-level control.

---

## Protecting the API

Every protected API route must verify the caller's identity server-side. Never trust client-supplied identity claims without verification.

### Supabase-backed API routes

```ts
// app/api/data/route.ts — protected API route
import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";
import { NextResponse } from "next/server";

export async function GET(request: Request) {
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

  // user.id is auth.uid() — data scoping is handled by Supabase RLS automatically
  // when using the anon client with the user's session cookie
  const { data } = await supabase.from("my_table").select("*");
  return NextResponse.json(data);
}
```

### External / standalone API (Bearer token)

For APIs not behind Supabase's client, verify the JWT from the `Authorization: Bearer <token>` header:

```ts
// lib/auth/verify-token.ts — conceptual; security-review before production
// Uses 'jose' library for JWKS-based verification
// npm install jose
import { createRemoteJWKSet, jwtVerify } from "jose";

// Google's JWKS endpoint [unverified — confirm current URL]
const GOOGLE_JWKS = createRemoteJWKSet(
  new URL("https://www.googleapis.com/oauth2/v3/certs"),
);

export async function verifyGoogleIdToken(token: string) {
  const { payload } = await jwtVerify(token, GOOGLE_JWKS, {
    issuer: "https://accounts.google.com",         // or accounts.google.com
    audience: process.env.GOOGLE_CLIENT_ID!,        // your OAuth client ID
    // algorithms: ['RS256'] — jose infers from JWKS
  });

  // payload.sub, payload.email, payload.exp already validated
  return payload;
}

// In your API handler:
export async function GET(request: Request) {
  const authHeader = request.headers.get("Authorization");
  if (!authHeader?.startsWith("Bearer ")) {
    return new Response("Unauthorized", { status: 401 });
  }

  const token = authHeader.slice(7);
  try {
    const claims = await verifyGoogleIdToken(token);
    // Proceed with claims.sub as the verified user ID
  } catch {
    return new Response("Unauthorized — invalid token", { status: 401 });
  }
}
```

**Checklist for token verification:**
- [ ] Signature verified against JWKS (not hardcoded public key)
- [ ] `iss` matches expected issuer
- [ ] `aud` matches your application's client ID
- [ ] `exp` checked (library handles automatically if configured)
- [ ] Algorithm explicitly pinned (do not accept `alg: none`)
- [ ] Security review completed before production

---

## CORS configuration

CORS controls which origins can make cross-origin requests to your API.

```ts
// next.config.ts — CORS headers for API routes
const nextConfig = {
  async headers() {
    return [
      {
        source: "/api/:path*",
        headers: [
          // Allow only your own app's origin and any known dashboard embed origins
          { key: "Access-Control-Allow-Origin", value: "https://app.example.com" },
          { key: "Access-Control-Allow-Methods", value: "GET, POST, PUT, DELETE, OPTIONS" },
          { key: "Access-Control-Allow-Headers", value: "Content-Type, Authorization" },
          { key: "Access-Control-Allow-Credentials", value: "true" },
        ],
      },
    ];
  },
};
```

**CORS rules:**
- Do not use `Access-Control-Allow-Origin: *` for authenticated APIs.
- Specify an explicit allowlist of origins.
- `Access-Control-Allow-Credentials: true` requires a non-wildcard origin.
- CORS is not a security boundary for server-to-server calls (it only applies in browsers).

---

## CSRF defense

Cookies are sent automatically by the browser on cross-site requests. Mitigations:

1. **`SameSite=Lax` or `Strict` cookie flag** — primary defense; see `session-and-token-management` skill.
2. **CSRF token for state-mutating routes** — double-submit cookie or synchronizer token pattern for POST/PUT/DELETE routes that cannot rely on `SameSite=Strict` alone.
3. **`Content-Type: application/json` check** — simple APIs can reject requests that don't send the correct Content-Type header (pre-flight required for non-simple CORS requests).
4. **Origin/Referer header validation** — secondary check; referer can be stripped by privacy settings.

Supabase API routes benefit from the built-in cookie `SameSite` protection when using `@supabase/ssr`. [unverified — confirm in current Supabase SSR docs]

---

## Anti-patterns this skill flags

- Using `supabase.auth.getSession()` in middleware instead of `getUser()` — getSession trusts the unverified cookie
- Returning sensitive data from an API route without verifying the session first
- `Access-Control-Allow-Origin: *` on authenticated API routes
- No `SameSite` flag on auth cookies — CSRF-vulnerable
- Skipping `iss` or `aud` validation in manual token verification — replay across issuers/apps
- Accepting `alg: none` in JWT verification — allows unsigned tokens
- Protecting only page routes but not API routes (API must enforce auth independently)
- Redirect-after-auth using an unvalidated `next` query parameter — open redirect vulnerability; validate `next` is a relative path on your own domain

---

## Verification checklist

- [ ] All protected routes redirect to login when session is absent
- [ ] Middleware uses `getUser()` not `getSession()` for validation
- [ ] API routes return 401 when session/token is absent or invalid
- [ ] Token verification checks signature + iss + aud + exp
- [ ] CORS headers explicitly list allowed origins (no wildcard)
- [ ] Auth cookies have `HttpOnly`, `Secure`, `SameSite` flags
- [ ] `next` redirect parameter validated as relative path
- [ ] Security review completed before production deploy

---

## See also

- Skill: [`../session-and-token-management/SKILL.md`](../session-and-token-management/SKILL.md) — the session that this skill reads to protect routes
- Skill: [`../authorization-rbac/SKILL.md`](../authorization-rbac/SKILL.md) — what to do once identity is verified (role checks)
- Skill: [`../gate-the-dashboard/SKILL.md`](../gate-the-dashboard/SKILL.md) — protecting the analytics dashboard specifically
- Best-practice: [`../../best-practices/validate-id-tokens-server-side.md`](../../best-practices/validate-id-tokens-server-side.md)
- data-platform: [`../../../data-platform/skills/rls-policy-authoring/SKILL.md`](../../../data-platform/skills/rls-policy-authoring/SKILL.md) — data-row authorization that follows identity verification
- Security escalation: [`../../../ravenclaude-core/agents/security-reviewer.md`](../../../ravenclaude-core/agents/security-reviewer.md)
