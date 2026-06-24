---
name: add-an-auth-provider
description: "Add a login method to an existing Supabase Auth app — Apple, Microsoft, GitHub social SSO, plus magic link, passkeys (WebAuthn), or email+password. The generic enable-provider procedure with each provider's gotchas (especially Apple's expiring ES256 secret + first-login name capture). Generalizes google-sso-setup to the variety pack."
---

# Skill: add-an-auth-provider

> **Invoked by:** the `auth-identity` team when the user wants a *variety* of login options, or to add a second/third provider to an app that already has one. Also consulted by `ravenclaude-core/security-reviewer` on any provider-credential change.
>
> **When to invoke:** "add Apple too", "let users sign in with Microsoft/GitHub", "add a magic-link fallback", "turn on passkeys". For the *first* Google setup, use [`../google-sso-setup/SKILL.md`](../google-sso-setup/SKILL.md) — this skill generalizes from it.
>
> **Output:** the new method enabled in Supabase, the provider's console configured, redirect URIs registered, a test login passing, and the per-provider gotchas handled — with a security checklist signed off.

---

## Boundary

This skill **authenticates the person** — it adds *how* they prove identity. It never scopes data; whichever method they use, the same verified `auth.uid()` hands off to `data-platform` RLS. Don't duplicate RLS/embed mechanics. The method is interchangeable; the seam is not.

---

## The generic procedure (every OAuth/social provider)

Adding a managed-provider social login is the **same three moves** regardless of provider — this is the payoff of the Supabase lean:

1. **Register an OAuth app in the provider's console** → get a **client ID + secret**. (The per-provider walkthroughs below say *how to get there* and *who can do it*.)
2. **Register Supabase's callback** `https://<project-ref>.supabase.co/auth/v1/callback` in that console's allowed redirect URIs (plus your own `…/auth/callback`).
3. **Enable the provider in Supabase** (Authentication → Providers), paste client ID + secret, save. App code is one line: `supabase.auth.signInWithOAuth({ provider })`. `[verify-at-build — Supabase dashboard UI]`

Then handle the **per-provider gotchas** below. Keep scopes minimal (`openid email profile` equivalent) and route the concrete credential change through `security-reviewer`.

> **Before you start — do you have the access to register the app?** Step 1 happens in *the provider's* developer portal, and each one gates app creation behind a role. If you don't hold it, the registration is an **admin's** task, not yours — surface that early rather than getting stuck mid-setup. The required role per provider is the first line of each walkthrough below (all `[verify-at-build]` — portal roles + UIs move). Google's full worked example is [`../google-sso-setup/SKILL.md`](../google-sso-setup/SKILL.md); the others are below.

---

## Per-provider notes

### Apple — the one most likely to fail first (all verified 2026-06-03)

Apple is *not* like Google. Budget extra time:

#### Registering the app — portal walkthrough

> **Portal:** [developer.apple.com/account](https://developer.apple.com/account) → **Certificates, Identifiers & Profiles**. `[verify-at-build — Apple Developer UI moves]`
>
> **Who can do it:** an **Account Holder or Admin** role in the Apple Developer team (and the team needs a paid Apple Developer Program membership). A team member without that role must ask the Account Holder. `[verify-at-build]`

1. **Identifiers → App IDs → register an App ID** (the parent identity), enabling the **Sign in with Apple** capability.
2. **Identifiers → Services IDs → register a Services ID** — this becomes your **web `client_id`**. Enable Sign in with Apple on it and configure its domains + return URLs.
3. **Return URLs:** add Supabase's callback `https://<project-ref>.supabase.co/auth/v1/callback` (Apple rejects `localhost`/plain-HTTP — use an HTTPS dev domain/tunnel).
4. **Keys → register a Sign in with Apple key** → download the **`.p8`** private key (one-time download — store it as a secret reference, never commit it). Note the **Key ID** and your **Team ID**.
5. **Generate the client secret** — a **JWT signed ES256** from the `.p8` (see the gotchas below); paste the **Services ID** + that JWT into Supabase's Apple provider.

- **Console:** Apple Developer → register an **App ID**, a **Services ID** (this is your web `client_id`), and a **Sign in with Apple key** (`.p8`).
- **The client secret is a JWT you generate** — signed **ES256** (ECDSA P-256 + SHA-256) from the `.p8` key — **not** a static string. ([Apple — creating a client secret](https://developer.apple.com/documentation/accountorganizationaldatasharing/creating-a-client-secret))
- **That JWT expires — max 180 days.** Automate regeneration or logins silently break. ([bannister.me](https://bannister.me/blog/generating-a-client-secret-for-sign-in-with-apple-on-each-request))
- **Web vs native `client_id` differ:** web uses the **Services ID**, native iOS uses the **bundle ID** — a mismatch throws `JWTClaimValidationFailed: unexpected "aud"`. ([Better Auth — Apple](https://better-auth.com/docs/authentication/apple))
- **Name + email return ONLY on first authorization** — no userinfo endpoint to re-fetch. **Persist them on first login or lose them forever.**
- **"Hide My Email"** yields a `@privaterelay.appleid.com` address; register your sending domain with Apple to email it. Treat it as the real email.
- **No `localhost`/HTTP** — use an HTTPS dev domain/tunnel.

> With Supabase you paste the Services ID + the generated JWT secret into the Apple provider — but the **180-day rotation** and **first-login name capture** remain your responsibility.

### Microsoft

#### Registering the app — portal walkthrough

> **Portal:** [entra.microsoft.com](https://entra.microsoft.com) (or **portal.azure.com → Microsoft Entra ID**) → **App registrations → New registration**. `[verify-at-build — Entra portal UI moves]`
>
> **Who can do it:** the **Application Developer** Entra role (or any user, if the tenant leaves "users can register applications" on). Restrictive tenants disable that — then a **Global Administrator / Cloud Application Administrator** registers it for you. `[verify-at-build]`

1. **New registration** → name the app and pick the **supported account types** (the *account-type audience*): single-tenant (work/school in this org), multi-tenant, or include personal Microsoft accounts. Choose deliberately — it's the most common Microsoft mistake.
2. **Redirect URI:** platform **Web**, value = Supabase's callback `https://<project-ref>.supabase.co/auth/v1/callback`.
3. **Certificates & secrets → New client secret** → copy the **Value** immediately (shown once; store as a secret reference). The **Application (client) ID** is on the Overview page.
4. Paste the client ID + secret into Supabase's Azure provider. Keep scopes minimal (`openid email profile`).

- Console: Entra ID → **App registration**; pick the right **account-type audience** (work/school only, or include personal Microsoft accounts).
- The generic OAuth button covers consumer + basic-work login. **Enterprise Entra** (conditional access, SCIM provisioning, app-role mapping, B2B federation, admin consent for org-wide scopes) → seam to [`../../../azure-cloud/agents/entra-identity-engineer.md`](../../../azure-cloud/agents/entra-identity-engineer.md), don't force it through the generic path.

### GitHub

#### Registering the app — portal walkthrough

> **Portal:** [github.com/settings/developers](https://github.com/settings/developers) → **OAuth Apps → New OAuth App** (personal); for an org-owned app: **Org → Settings → Developer settings → OAuth Apps**. `[verify-at-build — GitHub settings UI moves]`
>
> **Who can do it:** **any GitHub user** can create a personal OAuth App; an **organization owner** is required to create (or transfer) an **org-owned** app. `[verify-at-build]`

1. **New OAuth App** → set the **Homepage URL** and the **Authorization callback URL** = Supabase's callback `https://<project-ref>.supabase.co/auth/v1/callback`.
2. **Register**, then **Generate a new client secret** → copy it once (store as a secret reference). The **Client ID** is on the app page.
3. Paste client ID + secret into Supabase's GitHub provider.

- Console: GitHub → Settings → Developer settings → **OAuth App**.
- **Request the `user:email` scope** — GitHub emails can be private, and without it you may get no verified email back.

### Facebook / X (Twitter)

- Available, but higher review friction + consumer churn. Usually **skip for B2B / internal tools**; add only for consumer apps that need them.

---

## Passwordless methods

### Magic link (email OTP link)
- Supabase: `signInWithOtp({ email })`. No console app needed — it's email delivery.
- Make links **single-use, short-TTL, rate-limited**; deliverability is now your login funnel (verify SPF/DKIM on your sending domain).
- Great as the **no-third-party-account fallback** so you never *force* a social login.

### Passkeys / WebAuthn (modern, phishing-resistant)
- Supabase **Passkeys is beta** (WebAuthn): Authentication → Passkeys → enable; set **Relying Party Display Name**, **Relying Party ID** (bare domain), and **Relying Party Origins** (allow-list). **HTTPS required except loopback.** ([Supabase passkeys docs](https://supabase.com/docs/guides/auth/passkeys))
- Because it's **beta** and only ~15–20% of users have created a passkey, **gate it behind a flag and keep a fallback** (social or magic link). Offer passkeys; don't *only* offer them.

### Email + password
- Offer only if explicitly required. The provider must own hashing, breach-check, verification, and rate-limiting — **never hand-roll** (best-practice `prefer-managed-auth-over-rolling-your-own`). Require email verification; consider skipping standalone passwords entirely in favor of social + magic-link + passkeys.

---

## Account-linking decision (do this early)

If the same person can sign in with Google *and* Apple (or social *and* magic link), decide whether that's **one account or two**. Keying on verified email usually works — but Apple's "Hide My Email" relay can fork an identity. If unified accounts matter, implement explicit account-linking and test it. Defer the deep version to `auth-architect`.

---

## Anti-patterns this skill flags

- Adding Apple without automating the **180-day secret-JWT rotation** (logins die silently when it expires).
- Not capturing Apple's **name/email on first login** (gone forever after).
- Using the **Services ID where the bundle ID is expected** (or vice versa) → `aud` mismatch.
- Forcing **only** social logins with no email/passwordless fallback.
- Making **passkeys the only method** while adoption is ~15–20%.
- Offering **8 providers** — decision fatigue + maintenance; lead with 2–4 the audience already has.
- Forcing enterprise Entra through the generic Microsoft button instead of seaming to `azure-cloud`.
- Shipping any provider-credential change without `security-reviewer`.

---

## Verification checklist

- [ ] Provider OAuth app registered; client ID + secret obtained (Apple: Services ID + `.p8` key + generated ES256 JWT)
- [ ] Supabase callback URL registered in the provider console; your `…/auth/callback` too
- [ ] Provider enabled in Supabase; scopes minimal
- [ ] Apple only: secret-JWT rotation automated (≤180d); first-login name/email persisted
- [ ] Passkeys only: RP ID/Origins set; HTTPS; behind a flag with a fallback
- [ ] Secrets in server-side env, never `NEXT_PUBLIC_`, never committed
- [ ] Test login passes; `auth.uid()` resolves; account-linking behavior intended
- [ ] Security review completed before production (`ravenclaude-core/security-reviewer`)

---

## See also

- Skill: [`../google-sso-setup/SKILL.md`](../google-sso-setup/SKILL.md) — the worked example this generalizes from
- Knowledge: [`../../knowledge/social-and-passwordless-providers-2026.md`](../../knowledge/social-and-passwordless-providers-2026.md) — the full variety-pack reference (Apple gotchas, passkeys, magic link)
- Decision tree: [`../../knowledge/auth-identity-decision-trees.md`](../../knowledge/auth-identity-decision-trees.md) — "Which auth providers should you offer?"
- Skill: [`../session-and-token-management/SKILL.md`](../session-and-token-management/SKILL.md) — token storage applies to every method
- data-platform: [`../../../data-platform/skills/rls-policy-authoring/SKILL.md`](../../../data-platform/skills/rls-policy-authoring/SKILL.md) — `auth.uid()` → data scoping
- Security escalation: [`../../../ravenclaude-core/agents/security-reviewer.md`](../../../ravenclaude-core/agents/security-reviewer.md)
