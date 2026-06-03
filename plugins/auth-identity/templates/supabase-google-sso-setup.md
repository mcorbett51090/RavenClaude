# Template: Supabase + Google SSO setup

> A copy-paste walkthrough for wiring Google SSO via Supabase Auth into a Next.js App Router project.
> Mark any step you complete with [x]. Steps marked `[unverified]` depend on external service UIs that change — verify against current docs before following.
>
> **Security note:** all code in this template is conceptual. Route to `ravenclaude-core/security-reviewer` before production deploy.

---

## Prerequisites

- [ ] Supabase project created ([app.supabase.com](https://app.supabase.com)) [unverified — URL current as of 2026-06-03]
- [ ] Google Cloud project created ([console.cloud.google.com](https://console.cloud.google.com)) [unverified]
- [ ] Next.js 14+ App Router project

---

## Phase 1 — Google Cloud Console

### 1.1 OAuth consent screen

1. Console → **APIs & Services → OAuth consent screen**
2. User type: `External` (unless internal Google Workspace app)
3. Fill in:
   - App name: `{{your-app-name}}`
   - User support email: `{{your-email}}`
   - Developer contact email: `{{your-email}}`
4. Scopes — add only:
   - `openid`
   - `https://www.googleapis.com/auth/userinfo.email`
   - `https://www.googleapis.com/auth/userinfo.profile`
5. Test users: add your own email for dev testing
6. Publishing status: **Testing** (change to **Production** before launch)

### 1.2 Create OAuth client

1. Console → **APIs & Services → Credentials → Create Credentials → OAuth client ID**
2. Application type: **Web application**
3. Name: `{{your-app-name}} (Supabase)`
4. Authorized JavaScript origins:
   ```
   https://{{your-domain.com}}
   http://localhost:3000
   ```
5. Authorized redirect URIs: _(leave empty for now — add in Phase 2 Step 2.3)_
6. **Create** → copy **Client ID** and **Client secret**

---

## Phase 2 — Supabase Auth

### 2.1 Enable Google provider

1. Supabase dashboard → **Authentication → Providers → Google** [unverified — nav may change]
2. Toggle: **Enable Sign in with Google** → ON
3. Paste **Client ID** from 1.2
4. Paste **Client secret** from 1.2
5. Note the **Callback URL (for OAuth)** — it looks like:
   ```
   https://{{project-ref}}.supabase.co/auth/v1/callback
   ```
6. Save

### 2.2 (Optional) Set redirect allow-list

In Supabase → **Authentication → URL Configuration** [unverified]:

- **Site URL:** `https://{{your-domain.com}}`
- **Additional redirect URLs:**
  ```
  http://localhost:3000/**
  https://{{your-domain.com}}/**
  ```

### 2.3 Add the Supabase callback URI to Google

Back in Google Cloud Console → Credentials → your OAuth client → edit:

- **Authorized redirect URIs** → Add:
  ```
  https://{{project-ref}}.supabase.co/auth/v1/callback
  http://localhost:54321/auth/v1/callback
  ```
  _(second URI is for Supabase local dev emulator — verify your local port)_ [unverified]
- Save

---

## Phase 3 — Next.js application code

### 3.1 Install dependencies

```bash
npm install @supabase/supabase-js @supabase/ssr
```

[unverified — package versions; verify at npmjs.com]

### 3.2 Environment variables

Create `.env.local` (never commit):

```bash
# Public — safe to expose; RLS-bound
NEXT_PUBLIC_SUPABASE_URL=https://{{project-ref}}.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY={{anon-key-from-supabase-api-settings}}

# Server-only — NEVER use NEXT_PUBLIC_ prefix for this
# SUPABASE_SERVICE_ROLE_KEY={{service-role-key}}  # only if needed server-side
```

### 3.3 Supabase client helpers

```ts
// lib/supabase/client.ts  (browser client)
import { createBrowserClient } from "@supabase/ssr";

export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
  );
}
```

```ts
// lib/supabase/server.ts  (server client)
import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";

export function createServerSupabase() {
  const cookieStore = cookies();
  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll: () => cookieStore.getAll(),
        setAll: (cs) =>
          cs.forEach(({ name, value, options }) =>
            cookieStore.set(name, value, options),
          ),
      },
    },
  );
}
```

### 3.4 Sign-in button (client component)

```tsx
// components/GoogleSignInButton.tsx
"use client";
import { createClient } from "@/lib/supabase/client";

export function GoogleSignInButton() {
  const supabase = createClient();

  async function signIn() {
    await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: `${location.origin}/auth/callback`,
      },
    });
  }

  return (
    <button
      onClick={signIn}
      className="btn-google" // style as needed
    >
      Sign in with Google
    </button>
  );
}
```

### 3.5 Auth callback route

```ts
// app/auth/callback/route.ts
import { NextRequest, NextResponse } from "next/server";
import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";

export async function GET(request: NextRequest) {
  const { searchParams, origin } = new URL(request.url);
  const code = searchParams.get("code");
  const next = searchParams.get("next") ?? "/dashboard";

  if (code) {
    const cookieStore = cookies();
    const supabase = createServerClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
      {
        cookies: {
          getAll: () => cookieStore.getAll(),
          setAll: (cs) =>
            cs.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options),
            ),
        },
      },
    );
    const { error } = await supabase.auth.exchangeCodeForSession(code);
    if (!error) {
      // Validate `next` is a relative path — prevent open redirect
      const safePath = next.startsWith("/") ? next : "/dashboard";
      return NextResponse.redirect(new URL(safePath, origin));
    }
  }

  return NextResponse.redirect(new URL("/auth/error", origin));
}
```

### 3.6 Middleware (protect all routes)

```ts
// middleware.ts
import { createServerClient } from "@supabase/ssr";
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

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

  const { data: { user } } = await supabase.auth.getUser();
  const path = request.nextUrl.pathname;
  const isPublic = PUBLIC_PATHS.some((p) => path === p || path.startsWith(p + "/"));

  if (!user && !isPublic) {
    const url = request.nextUrl.clone();
    url.pathname = "/login";
    url.searchParams.set("next", path);
    return NextResponse.redirect(url);
  }

  return response;
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)"],
};
```

### 3.7 Access `auth.uid()` for RLS

```ts
// In any Server Component or API route:
const supabase = createServerSupabase();
const { data: { user } } = await supabase.auth.getUser();

// user.id === auth.uid() in Supabase Postgres RLS policies
// All Supabase queries made with this client automatically include
// the user's JWT — RLS policies fire automatically.
// Data scoping (which rows) is data-platform's rls-policy-authoring skill's job.
```

---

## Phase 4 — Verify it works

| Check | How to verify |
|---|---|
| Sign-in button triggers Google consent screen | Click button; Google redirects to app |
| Callback route exchanges code for session | No error on `/auth/callback`; redirects to `/dashboard` |
| Session cookie is HttpOnly | DevTools → Application → Cookies → sb-* cookies have HttpOnly flag |
| Protected route redirects when logged out | Log out; navigate to `/dashboard` → redirects to `/login` |
| `user.id` non-null after login | `console.log(user.id)` in a Server Component |
| `auth.uid()` resolves in a test RLS query | Run a Supabase query with RLS enabled; verify correct rows returned |

---

## Handoff to data-platform RLS

After authentication is working:

1. User's `auth.uid()` is available in every Supabase query automatically (JWT in cookie).
2. Apply RLS policies using the `data-platform/skills/rls-policy-authoring/SKILL.md`.
3. For embedded analytics, issue a short-lived embed JWT using `data-platform/skills/jwt-embed-issuance/SKILL.md` — see also `gate-the-dashboard` skill.

---

## See also

- Skill: [`../skills/google-sso-setup/SKILL.md`](../skills/google-sso-setup/SKILL.md)
- Skill: [`../skills/session-and-token-management/SKILL.md`](../skills/session-and-token-management/SKILL.md)
- Skill: [`../skills/protect-spa-and-api/SKILL.md`](../skills/protect-spa-and-api/SKILL.md)
- Template: [`./auth-architecture-decision-record.md`](./auth-architecture-decision-record.md)
- Template: [`./oidc-client-config-checklist.md`](./oidc-client-config-checklist.md)
