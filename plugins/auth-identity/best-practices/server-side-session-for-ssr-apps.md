# SSR Apps Set the Session Cookie Server-Side, Not Client-Side

**Status:** Absolute rule
**Domain:** Auth & Identity — SSR session management
**Applies to:** `auth-identity`

---

## Why this exists

A Next.js App Router (or any SSR framework) application that completes the OAuth callback and stores the session in `localStorage` or sets a non-HttpOnly cookie from the client side has re-introduced the XSS exposure that HttpOnly cookies prevent. The server receives the authorization code in the callback route; that route should set the `HttpOnly + Secure + SameSite` session cookie server-side before redirecting the user. Client-side token handling in an SSR app is an architectural regression — the server is already in the loop for the callback, and there is no reason for the access token to touch the browser's JS context.

## How to apply

**Correct server-side session pattern (Next.js App Router example with Supabase):**

```typescript
// app/auth/callback/route.ts
import { createServerClient } from '@supabase/ssr';
import { cookies } from 'next/headers';
import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  const requestUrl = new URL(request.url);
  const code = requestUrl.searchParams.get('code');

  if (code) {
    const cookieStore = cookies();
    const supabase = createServerClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
      {
        cookies: {
          get(name) { return cookieStore.get(name)?.value; },
          set(name, value, options) { cookieStore.set({ name, value, ...options }); },
          remove(name, options) { cookieStore.set({ name, value: '', ...options }); },
        },
      }
    );

    // Exchange the code for a session — sets HttpOnly cookies server-side
    await supabase.auth.exchangeCodeForSession(code);
  }

  return NextResponse.redirect(new URL('/dashboard', request.url));
}
```

**Key points:**
- `exchangeCodeForSession(code)` calls the Supabase token endpoint server-side and sets the `sb-*-auth-token` cookies with `HttpOnly; Secure; SameSite=Lax` via the `set` callback.
- The access token and refresh token **never appear in the browser's JS context** on this flow.
- Server components and API routes read the session via `supabase.auth.getUser()` using the cookie.

**Do:**
- Use the `@supabase/ssr` package (not `@supabase/auth-helpers`) for App Router — it is the current recommended package.
- Read the session in server components with `createServerClient`; in client components use the `createBrowserClient` with no access to the refresh token.
- Refresh the session in middleware (`middleware.ts`) so every server-rendered response has a fresh token.

**Don't:**
- Call `supabase.auth.setSession({ access_token, refresh_token })` from a client component after receiving tokens via URL.
- Use `localStorage.setItem('supabase.auth.token', ...)` in an SSR app.
- Store the auth state only in a React context — SSR renders without React context; the session must be in a cookie the server can read.

## Edge cases / when the rule does NOT apply

- **Pure static SPA behind auth (no SSR)**: there is no server-side callback handler; the browser must handle the callback. Use the provider SDK's PKCE flow with memory-only token storage per the `session-and-token-management` decision tree.
- **Native mobile apps**: cookies are not the right session mechanism; use the platform secure keystore via the SDK.

## See also

- [`../agents/auth-implementation-engineer.md`](../agents/auth-implementation-engineer.md) — implements the SSR callback and middleware refresh
- [`./never-store-tokens-in-localstorage.md`](./never-store-tokens-in-localstorage.md) — the absolute rule this pattern operationalizes in the SSR context

## Provenance

Codifies the Supabase Auth SSR pattern from `auth-identity` house opinion #3 ("Never store tokens in localStorage/sessionStorage") applied to Next.js App Router. Supabase SSR documentation (supabase.com/docs/guides/auth/server-side `[verify-at-build]`). _Last reviewed: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_
