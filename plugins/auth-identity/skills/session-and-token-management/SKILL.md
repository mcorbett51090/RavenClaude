---
name: session-and-token-management
description: "Session vs JWT trade-offs; HttpOnly+Secure+SameSite cookie storage; refresh-token rotation; logout and revocation; storage anti-patterns (no tokens in localStorage or sessionStorage). The post-sign-in half of the auth lifecycle."
---

# Skill: session-and-token-management

> **Invoked by:** any agent building or reviewing authentication flows; `ravenclaude-core/security-reviewer` for any session-management or token-storage change.
>
> **When to invoke:** after sign-in is working (see `google-sso-setup`) and you need to decide how to store the session; implementing refresh; implementing logout; hardening an existing session implementation.
>
> **Output:** storage strategy decision documented + cookie configuration verified + refresh rotation implemented + logout/revocation flow working + anti-patterns cleared.

---

## Boundary

This skill manages the authenticated session **after** the user has proven their identity via OAuth/OIDC (see `oauth-oidc-flow-design` and `google-sso-setup`). It does not scope data access — that is the `data-platform` plugin's RLS layer. Security-sensitive code (token signing/verification, secret handling) routes to `ravenclaude-core/security-reviewer`.

---

## Session vs JWT sessions

| Approach | How it works | When to prefer |
|---|---|---|
| **Server-side session** | Auth state stored on the server (database, Redis); client holds an opaque session ID in an HttpOnly cookie. | Default for most web apps. Immediate revocation possible (delete the session record). More operational overhead. |
| **JWT session** | Auth state encoded in a signed JWT stored in an HttpOnly cookie; server validates signature on each request. | Stateless / horizontally scaled systems. Revocation is harder (requires a denylist or short expiry + refresh token rotation). |
| **Supabase Auth sessions** | Supabase uses a JWT + refresh token stored in HttpOnly cookies by `@supabase/ssr`. The JWT is short-lived (≈1 hour [unverified]); the refresh token is rotated on use. | The default for this stack; handled automatically. |

**Do not store session state in `localStorage` or `sessionStorage`** — both are accessible to JavaScript and therefore to any XSS payload. The `never-store-tokens-in-localstorage.md` best-practice is an absolute rule.

---

## Cookie configuration

Every auth cookie must have all three flags:

| Flag | Why |
|---|---|
| `HttpOnly` | JavaScript cannot read the cookie — XSS cannot exfiltrate the token |
| `Secure` | Cookie only sent over HTTPS — prevents token leakage on HTTP |
| `SameSite=Lax` (minimum) or `SameSite=Strict` | Mitigates CSRF attacks; `Strict` is strongest but breaks some cross-site navigation flows |

`@supabase/ssr` sets these flags automatically when using `createServerClient`. [unverified — confirm in current @supabase/ssr docs] Verify in browser DevTools → Application → Cookies before shipping.

```
Set-Cookie: sb-access-token=...; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=3600
Set-Cookie: sb-refresh-token=...; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=...
```

For non-Supabase implementations, set these flags explicitly in your session middleware:

```ts
// Express / Node example — conceptual; security-review before production
res.cookie("session_token", token, {
  httpOnly: true,
  secure: process.env.NODE_ENV === "production",
  sameSite: "lax",   // or "strict" — see note above
  maxAge: 60 * 60 * 1000, // 1 hour in milliseconds
  path: "/",
});
```

---

## Refresh token rotation

Supabase Auth rotates the refresh token on every use — each call to `supabase.auth.getSession()` or `supabase.auth.refreshSession()` returns a new refresh token and invalidates the previous one. [unverified — confirm rotation behavior in current Supabase Auth version]

**Replay detection:** if a client presents an already-used refresh token, Supabase detects the reuse and revokes the entire session (treats it as a possible token theft). Your app should handle this gracefully:

```ts
// Next.js middleware — refresh session on every request
import { createServerClient } from "@supabase/ssr";
import { NextResponse } from "next/server";

export async function middleware(request) {
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
          cs.forEach(({ name, value, options }) => response.cookies.set(name, value, options));
        },
      },
    },
  );

  // This refreshes the session if expired — propagates updated cookies to response
  await supabase.auth.getUser();
  return response;
}
```

---

## Session duration guidelines

| Token type | Recommended lifetime | Notes |
|---|---|---|
| Access token / Supabase JWT | 1 hour [unverified — Supabase default] | Short enough to limit exposure if stolen |
| Refresh token | Days to weeks depending on app risk tolerance | Rotate on every use; revoke on logout |
| Embed JWT (issued to dashboard) | 5-15 minutes | See data-platform `issue-short-lived-jwts-for-embeds` best-practice |
| Remember-me / long-lived session | Up to 30 days — require re-auth for sensitive actions | Explicit user opt-in; revocable |

---

## Logout and revocation

A complete logout must do all of the following:

1. **Revoke the session server-side** — call `supabase.auth.signOut()` or equivalent to invalidate the refresh token on the auth server.
2. **Clear all auth cookies** — both access and refresh token cookies.
3. **Redirect to a public page** — prevent back-navigation to an authenticated page with stale cookies.
4. **Revoke downstream tokens** — if your app issued embed JWTs or other downstream tokens, add them to a short-lived denylist or wait for them to expire naturally (5-15 min).

```ts
// app/auth/logout/route.ts
import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";
import { NextResponse } from "next/server";

export async function POST(request: Request) {
  const cookieStore = cookies();
  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    { cookies: { getAll: () => cookieStore.getAll(), setAll: (cs) => cs.forEach(({ name, value, options }) => cookieStore.set(name, value, options)) } },
  );

  await supabase.auth.signOut(); // invalidates the refresh token server-side
  return NextResponse.redirect(new URL("/", request.url));
}
```

> **Security note:** `signOut()` must be called server-side (POST route, not a client-side fetch with arbitrary URL). Route to `ravenclaude-core/security-reviewer` before shipping.

---

## Token storage anti-patterns

| Anti-pattern | Risk | Correct alternative |
|---|---|---|
| Tokens in `localStorage` | XSS exfiltration — any injected JS can read and exfiltrate | HttpOnly cookie |
| Tokens in `sessionStorage` | Same as localStorage for XSS; additionally lost on tab close causing UX friction | HttpOnly cookie |
| Tokens in a non-HttpOnly cookie | Readable by JS — XSS exfiltration | Add `HttpOnly` flag |
| Tokens in cookie without `Secure` | Sent over HTTP — interceptable on unencrypted networks | Add `Secure` flag |
| Tokens in cookie without `SameSite` | CSRF-vulnerable | Add `SameSite=Lax` minimum |
| Tokens in React state / Zustand / Redux | Persisted to localStorage if using persist middleware; in-memory state lost on reload causing auth loops | HttpOnly cookie |
| Long-lived access tokens (hours/days) | Larger exposure window if stolen | Short-lived access token + refresh token rotation |
| Same refresh token reused indefinitely | No revocation capability | Rotate on every use |

---

## CSRF considerations when using cookies

HttpOnly cookies are not readable by JavaScript, but they are sent automatically by the browser on cross-site requests — this is the CSRF attack surface.

**Mitigations:**
- `SameSite=Strict` — cookie not sent on cross-site requests at all (strongest; may break OAuth redirects from Google back to your app — test carefully)
- `SameSite=Lax` — cookie sent on top-level navigation, not on sub-resource requests — mitigates most CSRF while allowing OAuth redirects (recommended default)
- For state-mutating API routes: add a CSRF token (double-submit cookie or synchronizer token pattern) in addition to `SameSite`

See also: the `protect-spa-and-api` skill for CSRF protection on API routes.

---

## Anti-patterns this skill flags

- Any token in `localStorage` or `sessionStorage`
- Auth cookie without all three flags: `HttpOnly`, `Secure`, `SameSite`
- Logout that only clears client-side state without calling `signOut()` server-side
- Access token lifetime > 1 hour without a documented justification
- No refresh token rotation (same refresh token reused forever)
- Returning refresh token in a JSON response body (instead of setting it via Set-Cookie header)
- Using `NEXT_PUBLIC_` env var for any secret or signing key

---

## See also

- Skill: [`../oauth-oidc-flow-design/SKILL.md`](../oauth-oidc-flow-design/SKILL.md) — how the tokens were obtained
- Skill: [`../protect-spa-and-api/SKILL.md`](../protect-spa-and-api/SKILL.md) — using the session to protect routes and APIs
- Best-practice: [`../../best-practices/never-store-tokens-in-localstorage.md`](../../best-practices/never-store-tokens-in-localstorage.md) — absolute rule
- data-platform: [`../../../data-platform/best-practices/issue-short-lived-jwts-for-embeds.md`](../../../data-platform/best-practices/issue-short-lived-jwts-for-embeds.md) — short-lived embed tokens issued after authentication
- Security escalation: [`../../../ravenclaude-core/agents/security-reviewer.md`](../../../ravenclaude-core/agents/security-reviewer.md)
