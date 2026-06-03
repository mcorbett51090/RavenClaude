---
name: google-sso-setup
description: "Wire Sign in with Google end-to-end: Google Cloud OAuth client + consent screen + redirect URIs + scopes, then via Supabase Auth's Google provider (and a note on the Auth.js / direct path). Step-by-step with verification checkpoints."
---

# Skill: google-sso-setup

> **Invoked by:** the `auth-identity` team's identity-setup agent. Also consulted by `ravenclaude-core/security-reviewer` when reviewing any OAuth client registration change.
>
> **When to invoke:** new project needs Google SSO; switching from password auth to Google-first; adding Google as a second provider to an existing Supabase project; debugging a redirect-URI mismatch or consent-screen error.
>
> **Output:** working Google SSO flow (OAuth client registered, Supabase provider enabled, redirect URIs set, scopes justified, test login passes) + security checklist signed off.

---

## Boundary

This skill **authenticates the person** (verifies their Google identity). It does not scope data access. Once the user is authenticated and `auth.uid()` is available, data-row scoping hands off to the `data-platform` plugin's RLS skills (`rls-policy-authoring`, `jwt-embed-issuance`). Do not duplicate RLS or embed-JWT mechanics here.

---

## Overview: two paths

| Path | When to use |
|---|---|
| **Supabase Auth → Google provider** (recommended) | You are already using Supabase (Postgres + RLS). One config screen, managed token storage, `auth.uid()` available directly in RLS policies. |
| **Auth.js (formerly NextAuth) + Google provider** | You need framework-level flexibility (multiple providers, custom session shape, non-Supabase backend). More code, more config. |
| **Google Identity Services SDK (direct)** | Rare. Only when you want maximum control and are not using any managed auth layer. Avoid unless there is a strong reason. |

For this stack (Next.js + Supabase), default to the **Supabase Auth** path.

---

## Step 1 — Google Cloud: create the OAuth client

> **Platform:** [console.cloud.google.com](https://console.cloud.google.com) [unverified — verify against current console UI]

1. Select or create a Google Cloud project.
2. Navigate to **APIs & Services → OAuth consent screen**.
3. Fill in the consent screen:
   - **App name, user support email, developer contact email** — required.
   - **Scopes:** add only what you need. For "Sign in with Google" you need `openid`, `email`, `profile` — nothing more. Adding extra scopes (Drive, Calendar, etc.) triggers extended verification and delays publishing.
   - **Authorized domains:** add your app's root domain (e.g., `example.com`). This controls what redirect URIs are allowed.
   - **Publishing status:** leave as **Testing** during development. Move to **Production** before launch (required for users outside your test-user list).
4. Navigate to **Credentials → Create Credentials → OAuth 2.0 Client ID**.
5. Application type: **Web application**.
6. **Authorized JavaScript origins:** your app's origin(s), e.g. `https://app.example.com` (and `http://localhost:3000` for local dev).
7. **Authorized redirect URIs:** this is the most common source of errors — see Step 3 for the exact values.
8. Save. Copy **Client ID** and **Client Secret** — you will need them in Step 2.

> **Verification checkpoint:** the consent screen shows no "needs verification" banner for the three scopes above (`openid`, `email`, `profile`). If it does, you added a sensitive scope by mistake.

---

## Step 2 — Supabase: enable the Google provider

> [unverified — verify against current Supabase dashboard UI at supabase.com/docs/guides/auth/social-login/auth-google]

1. Open the Supabase dashboard for your project.
2. Go to **Authentication → Providers → Google**.
3. Toggle **Enable Sign in with Google**.
4. Paste the **Client ID** and **Client Secret** from Step 1.
5. The Supabase dashboard will show you the **callback URL** you must add to Google Cloud. It looks like:
   `https://<project-ref>.supabase.co/auth/v1/callback`
   Copy it for Step 3.
6. Save.

---

## Step 3 — Google Cloud: set the redirect URI

Back in Google Cloud Console → Credentials → your OAuth client:

- Add the Supabase callback URL from Step 2 to **Authorized redirect URIs**:
  `https://<project-ref>.supabase.co/auth/v1/callback`
- For local development also add:
  `http://localhost:54321/auth/v1/callback` (Supabase local emulator default) [unverified — confirm your local port]
- Save.

> **Common error:** `redirect_uri_mismatch` — the URI in the OAuth flow does not exactly match one in the authorized list. Trailing slashes, `http` vs `https`, and port numbers all matter. Copy-paste exactly.

---

## Step 4 — Next.js: wire the sign-in call

The following is a conceptual sketch. **Security-review before shipping any auth code to production.**

```tsx
// lib/supabase/client.ts
import { createBrowserClient } from "@supabase/ssr";

export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
  );
}
```

```tsx
// components/GoogleSignInButton.tsx
"use client";
import { createClient } from "@/lib/supabase/client";

export function GoogleSignInButton() {
  const supabase = createClient();

  async function signInWithGoogle() {
    await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: `${location.origin}/auth/callback`,
        // scopes default to openid, email, profile — do not expand unless required
      },
    });
  }

  return <button onClick={signInWithGoogle}>Sign in with Google</button>;
}
```

```tsx
// app/auth/callback/route.ts  (Next.js App Router)
import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  const requestUrl = new URL(request.url);
  const code = requestUrl.searchParams.get("code");
  const next = requestUrl.searchParams.get("next") ?? "/dashboard";

  if (code) {
    const cookieStore = cookies();
    const supabase = createServerClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
      { cookies: { getAll: () => cookieStore.getAll(), setAll: (c) => c.forEach(({ name, value, options }) => cookieStore.set(name, value, options)) } },
    );
    await supabase.auth.exchangeCodeForSession(code);
  }

  return NextResponse.redirect(new URL(next, requestUrl.origin));
}
```

> **Security note:** tokens are stored in HttpOnly cookies by `@supabase/ssr` — do not extract them to localStorage. See `session-and-token-management` skill and the `never-store-tokens-in-localstorage` best-practice.

---

## Step 5 — Retrieve the session and `auth.uid()`

```tsx
// app/dashboard/page.tsx (server component)
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
  if (!user) redirect("/login");

  // user.id == auth.uid() in Postgres RLS policies
  // Pass to data-platform RLS via the Supabase client — the JWT in the cookie
  // carries auth.uid() automatically.
  return <div>Welcome, {user.email}</div>;
}
```

The authenticated user's `user.id` maps to `auth.uid()` in Postgres RLS policies. Data scoping (which rows this user can read) is governed by the `data-platform` plugin's `rls-policy-authoring` skill — not by this plugin.

---

## Scope discipline

| Scope | When to include |
|---|---|
| `openid` | Always — required for OIDC / ID token issuance |
| `email` | Always — your app needs the user's email |
| `profile` | Usually — name + avatar |
| `https://www.googleapis.com/auth/drive` | Only if your app genuinely reads/writes Google Drive. Triggers Google's extended verification. |
| Any other Google API scope | Only if you have a concrete feature requirement. Minimise scope. |

---

## Auth.js path (alternative)

If you are not using Supabase or need framework flexibility:

1. `npm install next-auth` [unverified — confirm current package name; may be `next-auth@beta` for v5]
2. Configure `[...nextauth]/route.ts` with `GoogleProvider({ clientId, clientSecret })`.
3. The redirect URI registered in Google Cloud is: `https://app.example.com/api/auth/callback/google`.
4. Use `getServerSession` / `auth()` (v5) in server components.
5. For cookie storage of the session, use the `cookies` option with HttpOnly flags.

The token-storage and PKCE mechanics in `oauth-oidc-flow-design` and `session-and-token-management` skills apply regardless of which path you take.

---

## Anti-patterns this skill flags

- Redirect URI contains a trailing slash when Google expects none (or vice versa) — causes `redirect_uri_mismatch`
- Consent screen left in **Testing** mode at launch — external users cannot sign in (blocked after 100 test-user invitations)
- Client Secret exposed in front-end code or checked into git — must live in a server-side env var
- Scopes wider than `openid email profile` without a documented feature requirement
- Token stored in `localStorage` after the OAuth callback — use HttpOnly cookies (Supabase SSR handles this automatically)
- `signInWithOAuth` called server-side — it triggers a browser redirect; call it from a client component or a route handler
- PKCE disabled — Supabase Auth enables it by default; do not disable it [unverified — confirm PKCE default in current Supabase Auth version]

---

## Verification checklist

- [ ] OAuth client created in the correct Google Cloud project
- [ ] Redirect URIs match exactly (no trailing slash, correct scheme)
- [ ] Consent screen in **Production** mode before external users onboard
- [ ] Scopes limited to `openid email profile`
- [ ] `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY` in `.env.local` (never committed)
- [ ] `SUPABASE_SERVICE_ROLE_KEY` (if used) only in server-side env, never `NEXT_PUBLIC_`
- [ ] Test sign-in completes; session returned; `user.id` non-null
- [ ] `auth.uid()` resolves correctly in a test RLS query
- [ ] Security review completed before production deploy (see `ravenclaude-core/security-reviewer`)

---

## See also

- Skill: [`../oauth-oidc-flow-design/SKILL.md`](../oauth-oidc-flow-design/SKILL.md) — why Authorization Code + PKCE, not Implicit; flow selection by client type
- Skill: [`../session-and-token-management/SKILL.md`](../session-and-token-management/SKILL.md) — HttpOnly cookie storage, refresh rotation, logout
- Skill: [`../protect-spa-and-api/SKILL.md`](../protect-spa-and-api/SKILL.md) — route guards, API token verification, CORS + CSRF
- Template: [`../../templates/supabase-google-sso-setup.md`](../../templates/supabase-google-sso-setup.md) — copy-paste walkthrough
- Best-practice: [`../../best-practices/prefer-managed-auth-over-rolling-your-own.md`](../../best-practices/prefer-managed-auth-over-rolling-your-own.md)
- data-platform: [`../../../data-platform/skills/rls-policy-authoring/SKILL.md`](../../../data-platform/skills/rls-policy-authoring/SKILL.md) — how `auth.uid()` drives data scoping (data authorization, not auth-identity's concern)
- Security escalation: [`../../../ravenclaude-core/agents/security-reviewer.md`](../../../ravenclaude-core/agents/security-reviewer.md) — mandatory review for any auth code going to production
