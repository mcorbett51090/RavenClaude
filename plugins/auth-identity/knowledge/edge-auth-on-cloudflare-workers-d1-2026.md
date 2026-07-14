# Authing customers on the Cloudflare edge — Workers + D1 (2026)

> A build-derived companion to [`auth-provider-landscape-2026.md`](auth-provider-landscape-2026.md). That doc leans **Supabase Auth** because its JWT → `auth.uid()` → RLS synergy with `data-platform` is nearly free on Postgres. _This_ doc is the field guide for the case where the data layer is **not** Postgres but **Cloudflare D1**, and the app runs on **Cloudflare Workers** (e.g. an Astro app on Workers/Pages) — a genuinely viable edge-auth substrate with four traps that bit a real build this session.
>
> **The boundary still holds:** everything here only **authenticates the person** on the edge. Row/tenant scope after login is `data-platform`'s lane (see [`../CLAUDE.md`](../CLAUDE.md) §0). D1 has no `auth.uid()`/RLS engine, so the identity→authorization seam is *more* your responsibility here than on Supabase — scope rows in your Worker/query layer against the verified session subject, and route that authz design through `data-platform` + `security-reviewer`.
>
> **Volatility note.** Better Auth / Auth.js adapter status, an open GitHub bug's fix state, and Cloudflare's Zero-Trust pricing + terms all move. Every claim below carries an inline retrieval date; re-verify anything `[verify-at-build]` before quoting or shipping.

**Last verified: 2026-07-14** (from a real customer-SSO build: Google/Apple/Microsoft on Cloudflare Workers + D1 for an Astro app).

---

## TL;DR — the four learnings

1. **Workers + D1 is a viable customer-auth substrate.** Use a library that has **native D1 support** — **Better Auth** does (pass the D1 binding directly); **Auth.js** ships a D1 adapter but is not Astro-first.
2. **Better Auth trap — do NOT combine `cookieCache` with a KV `secondaryStorage`.** Open bug [#4203](https://github.com/better-auth/better-auth/issues/4203) (reopened Jan 2026) logs users out after **exactly 5 minutes**. Use server-side DB sessions; add a config assertion.
3. **Cloudflare Access is WORKFORCE (Zero Trust) auth, not customer auth.** 50-user free cap, then $7/user/mo, Cloudflare-branded login, and Service-Specific Terms restrict reselling. Use Access for your **operator/admin** surface; use a real customer auth (Better Auth / Auth.js on D1) for **end customers**.
4. **Apple private-relay email breaks email-based account binding.** A `@privaterelay.appleid.com` alias won't match the billing/CRM email on file, so auto-binding by email silently misses. Fall back to a **signed, single-use, short-TTL claim link emailed to the ON-FILE address**, account-scoped.

---

## 1. The substrate — libraries with native D1 support

Cloudflare D1 is SQLite-at-the-edge with a Worker **binding** (not a connection string). An auth library therefore has to speak the D1 binding, not a generic SQL driver over TCP. Two libraries do, with very different Astro ergonomics:

| Library | D1 support | Astro fit | Session model to prefer here | Source (retrieved 2026-07-14) |
|---|---|---|---|---|
| **Better Auth** | **Native** — pass the D1 binding directly to the adapter | **Astro-first-friendly** (framework-agnostic TS; the recommended path for this build) | **Server-side DB sessions in D1** (see trap #2) | [hono.dev — Better Auth on Cloudflare](https://hono.dev/examples/better-auth-on-cloudflare), [github: zpg6/better-auth-cloudflare](https://github.com/zpg6/better-auth-cloudflare) |
| **Auth.js** | **D1 adapter** ships (`@auth/d1-adapter`) | **Not Astro-first** — the docs/DX center on Next.js; workable but more friction on Astro/Workers | DB sessions via the D1 adapter | [authjs.dev — D1 adapter](https://authjs.dev/getting-started/adapters/d1) |

**House lean for the Workers+D1+Astro case: Better Auth**, on the strength of native D1 + framework-agnostic TS that sits cleanly in an Astro app on Workers. This does **not** override [`auth-provider-landscape-2026.md`](auth-provider-landscape-2026.md)'s Supabase-Auth default — it's the branch you take *once the data layer is committed to D1, not Postgres*, so the Supabase RLS synergy isn't on the table. If the stack can be Postgres/Supabase, the landscape doc's default still wins.

> **Library, not a hosted service.** Both Better Auth and Auth.js are **libraries** — you own the session store (here: D1), the schema, and the security posture (the landscape doc's "further left → more control + more burden" point). On Workers+D1 that burden includes the identity→row-scope seam that Supabase would have handed you via `auth.uid()`. House opinion #1 (prefer managed / vetted libraries over hand-rolled crypto) is satisfied — these are vetted libraries — but house opinion #5 (validate server-side) and the §0 boundary are now more on you.

---

## 2. Better Auth trap — `cookieCache` + `secondaryStorage` (KV) = logout after 5 minutes

**Bug [#4203](https://github.com/better-auth/better-auth/issues/4203) (reopened Jan 2026) `[verify-at-build — track fix state]`:** enabling Better Auth's **`cookieCache`** *together with* a **`secondaryStorage`** (e.g. Cloudflare KV) causes users to be logged out after **exactly 5 minutes** — the default cookie-cache TTL. The mechanism: when the cached session cookie expires, Better Auth treats the expired cache as a **logout signal** instead of **falling back to `secondaryStorage`** to re-hydrate the session. The two features are individually reasonable; the interaction is the bug.

**Mitigation (what shipped this build):**

- **Use server-side DB sessions in D1** as the source of truth — do not lean on a KV `secondaryStorage` for session state on Workers.
- **Do NOT combine `cookieCache` with `secondaryStorage`.** Pick one session-read path.
- **Add a config assertion** at startup that fails the build/boot if both are set together, so a future well-meaning "add KV to speed up session reads" change can't silently reintroduce the 5-minute logout:

```ts
// Guard against Better Auth #4203 (reopened Jan 2026): cookieCache + secondaryStorage
// silently logs users out after ~5 min. Fail fast instead of shipping the trap.
if (authConfig.session?.cookieCache?.enabled && authConfig.secondaryStorage) {
  throw new Error(
    "auth misconfig: cookieCache + secondaryStorage together trip Better Auth #4203 " +
    "(5-minute logout). Use server-side D1 DB sessions; drop one of the two.",
  );
}
```

**Why this is easy to hit:** both flags read like pure performance wins (fewer DB reads), so a reviewer without the bug context would wave them through. The assertion turns tribal knowledge into an enforced invariant. This is the same "make the invariant mechanical, not behavioral" posture as the plugin's anti-pattern hook (see [`../CLAUDE.md`](../CLAUDE.md) §11).

> Complements the session decision trees in [`auth-identity-decision-trees.md`](auth-identity-decision-trees.md) ("Session vs JWT" / "Which session storage strategy") — those pick *server-set HttpOnly session* as the SSR default; this note is the D1-specific landmine within the "server-side DB session" leaf.

---

## 3. Cloudflare Access is WORKFORCE auth, not customer auth

A tempting-but-wrong shortcut on a Cloudflare stack is to gate the *product's* end-customer login with **Cloudflare Access** (Zero Trust). Access is **workforce / employee (Zero Trust) auth** — for putting *your team* in front of internal apps — not consumer/customer (CIAM) auth. Three concrete reasons it's a mismatch for end customers `[verify-at-build — Zero Trust pricing/terms change]`:

| Dimension | Cloudflare Access reality (retrieved 2026-07-14) | Why it fails as customer auth |
|---|---|---|
| **Cost/scale** | Free tier caps at **50 users**; beyond that **$7/user/mo** | Customer bases blow past 50 instantly; $7/customer/mo is absurd CIAM economics |
| **Branding** | Login is **Cloudflare-branded** (Zero Trust org login), not your product | Customers should log into *your* brand, not a Cloudflare gate |
| **Terms** | Zero Trust **Service-Specific Terms restrict reselling Zero Trust to third parties** | Fronting your product's customers with it risks a terms violation |

Sources: [cloudflare.com/plans/zero-trust-services](https://www.cloudflare.com/plans/zero-trust-services/), [Zero Trust Service-Specific Terms](https://www.cloudflare.com/service-specific-terms-zero-trust-services/).

**The correct split (what shipped this build):**

```
  Cloudflare Access (Zero Trust)          Better Auth / Auth.js on D1
  = WORKFORCE auth                        = CUSTOMER auth (CIAM)
  operator / admin / internal surface     end-customer login surface
  ≤ small team, CF-branded login OK        your brand, your scale, your terms
```

- **Operator/admin surface** (the internal dashboard, ops tooling, staging) → **Cloudflare Access** is a great, near-zero-effort gate. This maps to the *reverse-proxy / static-host access-control* leaf of the "Gate the dashboard" tree in [`auth-identity-decision-trees.md`](auth-identity-decision-trees.md) — Access is exactly a platform access layer in front of an app, for a *small internal audience*.
- **End-customer surface** → a real customer auth (Better Auth / Auth.js on D1) per §1.

> This refines the decision-trees' "Gate the dashboard" tree: **the static-host/platform-access leaf (Cloudflare Access, Vercel/Netlify auth) is a WORKFORCE gate — sound for an internal/admin audience, wrong for end customers** on cost, branding, and terms. When the gated audience is customers, take the app-shell + real-CIAM path, not the platform-access leaf.

---

## 4. Apple private-relay email breaks email-based account binding

The providers doc already covers Apple's *first-login* gotchas (ES256 secret ≤180 days, name/email only on first consent) — see [`social-and-passwordless-providers-2026.md`](social-and-passwordless-providers-2026.md) and the absolute rule [`../best-practices/apple-signin-secret-must-rotate.md`](../best-practices/apple-signin-secret-must-rotate.md). This build surfaced a distinct, **account-binding** failure not covered there:

**The failure.** With Apple's **"Hide My Email"**, Apple returns a `@privaterelay.appleid.com` **alias**, not the user's real address. If your onboarding **auto-binds a new login to an existing customer record by matching email** (against billing / CRM / an invite list), the relay alias **will not match** the on-file address — so the binding **silently misses**. The customer signs in "successfully" but lands as a brand-new, unlinked account, detached from their subscription/entitlements. `[verified 2026-07-14; developer.apple.com — Sign in with Apple / private email relay]`

**The fix (what shipped this build): a signed claim link to the ON-FILE address.** When email-based auto-binding misses (Apple relay, or any typed email that doesn't match a record), fall back to an explicit, verifiable binding step:

- Email a **signed, single-use, short-TTL claim link** to the **address already on file** in billing/CRM — **never** the typed or Apple-relayed address (mailing the unverified/relayed address would let an attacker bind to a record that isn't theirs).
- **Account-scope the link** so a leaked link can only bind *that* account to the session that requested it — bind the token to the requesting session/account, not just to the email, so a leaked link can't be redeemed to attach a *different* session.
- Single-use + short TTL + one-account-scope are the same properties the plugin already requires of magic links — reuse them here: [`../best-practices/magic-link-expiry-and-single-use.md`](../best-practices/magic-link-expiry-and-single-use.md).

This is deliberately **account binding**, not authentication: Apple already authenticated the person (house opinion #5 — validate the ID token server-side still applies to the Apple `id_token`). The claim link answers a *different* question — "is this authenticated person the same human as this on-file customer record?" — which email alone can no longer answer once Apple relays it.

> **Design note — don't key identity on email at all where you can avoid it.** The relay alias is a reminder that email is a mutable, provider-controlled attribute, not a stable subject. Prefer the provider's stable `sub` as the account key and treat email as a *claimable, verifiable* attribute layered on top. Account-linking (the same human via Google *and* Apple) is called out as a first-class decision in [`social-and-passwordless-providers-2026.md`](social-and-passwordless-providers-2026.md) — the relay-vs-on-file mismatch is the concrete mechanism that forces the explicit claim-link path.

---

## How this maps to the build

- **Substrate first:** committed to D1 (not Postgres) → Better Auth (native D1, Astro-friendly). Had it been Postgres/Supabase, the landscape doc's Supabase-Auth default would still win.
- **Sessions:** server-side DB sessions in D1; **no** `cookieCache` + `secondaryStorage` combo (#4203); a startup assertion enforces it.
- **Two audiences, two gates:** Cloudflare Access for the operator/admin surface; Better Auth/D1 for end customers. Never front customers with Access.
- **Apple binding:** stable `sub` as the account key; a signed single-use short-TTL claim link to the on-file address whenever email-based binding misses (Apple relay being the common trigger).
- **The seam is still not ours:** D1 has no RLS engine, so scope rows against the verified subject in your query layer and route that authz through `data-platform` + `security-reviewer` (§0). Every concrete auth/token/cookie change here still escalates to `ravenclaude-core/security-reviewer`.

---

## See also

- Knowledge: [`auth-provider-landscape-2026.md`](auth-provider-landscape-2026.md) — the build-vs-buy default (Supabase Auth); this doc is the D1/Workers branch off it.
- Knowledge: [`social-and-passwordless-providers-2026.md`](social-and-passwordless-providers-2026.md) — Apple's first-login gotchas + account-linking; §4 here adds the private-relay binding failure.
- Knowledge: [`auth-identity-decision-trees.md`](auth-identity-decision-trees.md) — session-storage + gate-the-dashboard trees that §2 and §3 refine.
- Best-practice: [`../best-practices/apple-signin-secret-must-rotate.md`](../best-practices/apple-signin-secret-must-rotate.md) — the Apple secret-rotation rule (referenced, not repeated).
- Best-practice: [`../best-practices/magic-link-expiry-and-single-use.md`](../best-practices/magic-link-expiry-and-single-use.md) — the single-use/short-TTL properties the §4 claim link reuses.
- Boundary: [`../CLAUDE.md`](../CLAUDE.md) §0 — authenticate-the-person vs authorize-the-data (sharper here: D1 has no `auth.uid()`/RLS).

## Refresh triggers

- Better Auth **#4203** changes state (fixed/closed) — update §2's "do not combine" from a hard rule to a version-gated one.
- Better Auth or Auth.js changes D1-adapter support or Astro ergonomics (§1).
- Cloudflare restructures Zero-Trust pricing, the 50-user free cap, or the reselling terms (§3).
- Apple changes private-relay behavior or the first-login email contract (§4).

## Sources

All retrieved 2026-07-14: [hono.dev — Better Auth on Cloudflare](https://hono.dev/examples/better-auth-on-cloudflare) · [github: zpg6/better-auth-cloudflare](https://github.com/zpg6/better-auth-cloudflare) · [Better Auth #4203 — cookieCache + secondaryStorage 5-min logout](https://github.com/better-auth/better-auth/issues/4203) · [authjs.dev — D1 adapter](https://authjs.dev/getting-started/adapters/d1) · [cloudflare.com/plans/zero-trust-services](https://www.cloudflare.com/plans/zero-trust-services/) · [Cloudflare Zero Trust Service-Specific Terms](https://www.cloudflare.com/service-specific-terms-zero-trust-services/) · [developer.apple.com — Sign in with Apple (private email relay)](https://developer.apple.com/documentation/sign_in_with_apple).

---

_Last reviewed: 2026-07-14 by `claude`. Adapter status, the #4203 fix state, Cloudflare Zero-Trust pricing/terms, and Apple's relay behavior are volatile — re-verify before quoting or shipping._
