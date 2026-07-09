# Auth provider landscape 2026 — build vs buy

> **Last reviewed:** 2026-06-03; **Clerk row + scale checkpoint refreshed 2026-07-09** (Clerk moved to a 50K-MRU free tier + per-MRU billing on 2026-02-05 — clerk.com/pricing retrieved 2026-07-09, secondary saasprices.net; MRU ≠ MAU). Sources: vendor pricing pages + procurement-benchmark write-ups (Zuplo "Auth Pricing Wars", MojoAuth 2026 pricing math, DesignRevision auth comparison — all retrieved 2026-06-03; secondary where the vendor doesn't publish list prices). Refresh when: (a) a provider restructures per-MAU pricing (Cognito did this — see below), (b) Supabase/Clerk/Auth0 changes free-tier limits, (c) a new entrant takes meaningful share, or (d) OAuth 2.1 finalizes (would touch the flow-mechanics doc, not this one).
>
> **Volatility warning:** every price below is per-MAU and changes often. Re-verify against the vendor's live pricing page before quoting a client. Each figure carries a retrieval date inline.

## The house position (opinionated)

**Prefer managed auth over rolling your own crypto, and lean Supabase Auth.** For a builder protecting a web app + API + analytics dashboard with Google SSO as the primary login, the default is **Supabase Auth** — not because it's the cheapest at every scale, but because of one structural fit: **its session JWT maps directly to Postgres `auth.uid()`**, which is exactly the subject claim the `data-platform` plugin's Row-Level Security needs. When the data layer is already Supabase/Postgres (it usually is in this marketplace), the authentication↔authorization seam is nearly free, instead of a custom claim-mapping you have to build and secure yourself.

**Roll-your-own is the last resort.** Password hashing, token signing, key rotation, JWKS rotation, breach monitoring, account-recovery flows, and OAuth edge cases are a deep adversarial surface. Justify a custom build only with a hard constraint (data-residency, air-gap, strict no-third-party mandate) recorded in the decision memo — and even then, build on a vetted library (Auth.js, Better Auth, a Keycloak deployment), never hand-rolled crypto.

## Default recommendation by situation

| Situation | Pick | Why |
|---|---|---|
| Web app + API + dashboard on Supabase/Postgres, Google SSO primary (**the house case**) | **Supabase Auth** | Google SSO + sessions built in; JWT → `auth.uid()` → RLS synergy with data-platform; lowest per-MAU overage rate |
| Best-in-class DX, drop-in React components, fast | **Clerk** | Pre-built UI, organizations, strong DX; per-MAU after a free tier |
| Enterprise B2B SSO (SAML/SCIM) is the core requirement | **WorkOS** (or Auth0) | WorkOS prices **per SSO connection**, not per-MAU — fits B2B with few large tenants |
| Already all-in on Firebase / AWS | **Firebase Auth** / **Cognito** | In-ecosystem; but watch Cognito's 2026 pricing change (below) |
| Hard data-residency / no-third-party / air-gap mandate | **OSS self-host** (Keycloak / Authentik / Auth.js / Better Auth) | Full control; you own the ops + the security surface |

## Managed providers — per-MAU pricing shape

> **MAU = monthly active users:** a unique user who authenticated at least once in a rolling 30-day window. This model **rewards small, highly-engaged user bases and punishes a long tail of low-frequency users.** Providers define "active" differently — Auth0 has historically defined it liberally (surprise bills); Cognito's definition is narrower. Confirm the definition, not just the rate.

| Provider | Free tier | Overage rate | Notes (retrieved 2026-06-03) |
|---|---|---|---|
| **Supabase Auth** | Pro plan ($25/mo) includes a large MAU allotment | **~$0.00325/MAU** beyond the allotment | **Lowest per-user overage of the compared set**; Google OAuth + sessions + RLS-friendly JWT built in. `[verified 2026-06-03]` |
| **Firebase Auth** | Free up to a threshold | **~$0.0055/MAU** standard auth | In-Google-Cloud; enterprise SSO is a separate paid tier. `[secondary, 2026-06-03]` |
| **AWS Cognito** | Free up to 10K MAU for **new** user pools | **~$0.0055/MAU** | **Amazon raised Cognito pricing for large bases (60K+ MAU) and cut the new-pool free tier from 50K→10K MAU.** Historically cheapest; less so now. `[secondary, 2026-06-03]` |
| **Clerk** | **50K MRU free** (raised from ~10K users on **2026-02-05**) | **~$0.02/MRU** above 50K; Pro $25/mo | Best-in-class DX + pre-built UI/orgs. **Bills per MRU (Monthly Retained User) — only users returning ≥24h after signup count, so MRU ≠ MAU** and is typically *lower* than MAU. `[verify-at-use — pricing tier, subject to change; MRU≠MAU]` clerk.com/pricing `[retrieved 2026-07-09]` (secondary: saasprices.net) |
| **Auth0 (Okta)** | Free dev tier | **~$0.07/MAU** | Most feature-complete + most expensive at scale; liberal "active" definition → bill surprises. `[secondary, 2026-06-03]` |
| **Stytch** | Free up to ~25 MAU (very low) | **~$0.05/MAU** | Passwordless/embedded-auth focus. `[secondary, 2026-06-03]` |
| **WorkOS** | Free for a generous user count | **~$125–$250 per SAML/SSO connection / month** | **Per-connection, not per-MAU** — built for B2B enterprise SSO with few large tenants. `[secondary, 2026-06-03]` |

**Rough scale checkpoints (compiled secondary — verify before quoting):** at **50K users**, Firebase/Cognito ≈ $0 (free tier), Auth0 ≈ $1,200/mo. **Clerk is now ≈ $0 at 50K — its free tier is 50K MRU (not the old ~$800/mo estimate, which assumed the retired ~10K free tier + per-MAU billing; corrected 2026-07-09).** At **100K users**, Firebase/Cognito ≈ $275/mo, Auth0 ≈ $2,400/mo. **Clerk at 100K depends on how many are MRU (returning ≥24h post-signup, ≠ MAU): only the MRU above 50K bill at ~$0.02 each — e.g. 100K users of whom 70K are MRU ≈ (70K−50K)×$0.02 ≈ $400/mo + $25 Pro; recompute against the actual MRU count** `[verify-at-use — pricing tier, subject to change; MRU≠MAU]` (clerk.com/pricing, retrieved 2026-07-09). Supabase's overage rate is the lowest per-user of the set. **Treat these as shape, not quotes.**

## OSS / self-host options

| Option | License / shape | Use when |
|---|---|---|
| **Keycloak** | Apache 2.0, Java, full IdP (OIDC + SAML, federation, admin console) | Enterprise-grade self-host; you want a real IdP and can run the JVM ops |
| **Authentik** | OSS (Python), modern IdP (OIDC/SAML/LDAP/proxy outpost) | Self-host with a lighter, modern feel than Keycloak; built-in reverse-proxy outpost for gating apps |
| **Auth.js (NextAuth)** | OSS (MIT), library not a service | Next.js/JS apps wanting auth *in the app* with many OAuth providers; you own session/DB |
| **Better Auth** | OSS, TypeScript framework-agnostic library | Modern TS-first alternative to Auth.js; plugins for orgs/2FA/passkeys; you own the storage |

**Library vs service:** Auth.js and Better Auth are **libraries** — they handle the OAuth dance but you own the session store, the DB, and the security posture. Keycloak/Authentik are **services** (a real IdP you operate). Supabase Auth and the managed vendors are **hosted services** — they own the ops *and* the security surface. The further left you go (roll-your-own → library → self-host → managed), the more control and the more security burden you carry.

## Why Supabase Auth is the lean here (the structural argument)

1. **Google SSO out of the box** — enable the Google provider, set the OAuth client ID/secret, and `signInWithOAuth` handles the Authorization Code + PKCE dance and session creation. `[verified 2026-06-03]`
2. **Session management included** — access + refresh tokens, refresh rotation, server-side code-exchange (`exchangeCodeForSession`), cookie-based sessions for SSR. `[verified 2026-06-03]`
3. **The JWT → `auth.uid()` → RLS synergy** — this is the decisive one. Supabase's session JWT carries the user's `sub`, exposed in Postgres as `auth.uid()`. The `data-platform` plugin's RLS policies key off exactly that, so the authentication→authorization handoff is a built-in claim, not a custom integration you must build and secure. `[verified 2026-06-03]`
4. **Lowest per-MAU overage** of the compared managed set (above).

**The override condition:** if the data layer is *not* Postgres/Supabase, or a hard enterprise-SSO (SAML/SCIM) requirement dominates, the lean shifts — WorkOS/Auth0 for enterprise SSO, Clerk for pure DX, OSS self-host for data-residency. Name the constraint in the decision memo.

## The boundary this doc respects

This is an **authentication** provider landscape — login, SSO, sessions, identity. **What rows a user sees after login is authorization**, which lives in the `data-platform` plugin's RLS / embed-JWT lane (see [`../CLAUDE.md`](../CLAUDE.md) §0). A provider choice here sets *who the user is*; data-platform decides *what data that identity may read*.

## Refresh triggers

- Any provider restructures per-MAU pricing or free-tier limits (Cognito did in 2026; Microsoft/Auth0 do this periodically).
- A new managed entrant takes meaningful share.
- Supabase Auth changes its Google-provider or session mechanics (would also touch [`oauth-oidc-and-google-sso.md`](oauth-oidc-and-google-sso.md)).
- OAuth 2.1 finalizes (touches the flow doc, not pricing).

---

_Last reviewed: 2026-06-03 by `claude`. Pricing figures are per-MAU and volatile — re-verify against vendor pages before quoting._
