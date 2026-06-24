# Social & passwordless auth providers — the variety pack (2026)

> The companion to [`auth-provider-landscape-2026.md`](auth-provider-landscape-2026.md). That doc chooses the **product** that runs auth (Supabase Auth / Clerk / Auth0 / OSS). _This_ doc covers the **methods you offer the end user** — which social logins (Google, Apple, Microsoft, GitHub…), plus passwordless (magic link, passkeys) and classic email+password. With a managed provider, adding a method is mostly configuration, not architecture — which is the whole reason the plugin leans managed.
>
> **Volatility note.** Per-provider console UIs, scopes, and Supabase's beta features move. Every `Last verified` below is a re-verification deadline. Mark anything `[verify-at-build]` before quoting.
>
> **The boundary still holds:** every method here only **authenticates the person**. Row/tenant scope after login is `data-platform` RLS (see [`../CLAUDE.md`](../CLAUDE.md) §0).

**Last verified: 2026-06-03.**

---

## TL;DR — what to offer

For a typical web app/dashboard where the builder "uses Google for everything," a strong default mix is:

1. **Google** (primary — highest coverage, lowest friction).
2. **Apple** (required if you ship an iOS app with third-party login per App Store policy; nice for privacy-conscious users — but it has the most setup gotchas, see below).
3. **Microsoft** (if any of your users are on Microsoft 365 / Entra — common for B2B).
4. **GitHub** (if your audience is developers).
5. **Magic link** or **passkeys** as the no-social-account fallback (so you never *force* a third-party account).

Offer **2–4 methods, not 8.** Every extra button is a "which one did I use last time?" tax and another integration to maintain. Lead with the one your audience already has.

---

## The social/SSO providers

All of the below are wired through **Supabase Auth** the same way — enable the provider in **Authentication → Providers**, paste the provider's client ID/secret, and register Supabase's callback `https://<project-ref>.supabase.co/auth/v1/callback` (plus your own redirect) in the provider's console. `signInWithOAuth({ provider })` is the only app-code change per provider. `[verify-at-build]`

| Provider | Offer it when | Setup home | Who can register it `[verify-at-build]` | Notable gotcha |
|---|---|---|---|---|
| **Google** | Almost always — broadest reach | Google Cloud Console → OAuth client + consent screen | Google Cloud project **Owner/Editor** | Static client secret; verification review if you request sensitive scopes. Keep scopes to `openid email profile`. |
| **Apple** | iOS app (App Store policy), privacy-focused users | Apple Developer → App ID + **Services ID** + key | Apple Developer team **Account Holder/Admin** (paid membership) | **The hard one — see the dedicated section below.** |
| **Microsoft** | Any M365/Entra users (B2B common) | Entra ID → App registration | **Application Developer** role, or any user if the tenant allows app registration | Choose the right account-type audience (work/school vs personal); deep Entra work seams to `azure-cloud/entra-identity-engineer`. |
| **GitHub** | Developer audience | GitHub → Settings → Developer settings → OAuth App | Any user (personal app); **org owner** (org-owned app) | Email can be private — request `user:email` scope to get a verified email. GitHub itself now supports Apple/Google social login (2025-10). |
| **Facebook / X (Twitter)** | Consumer/social apps only | Meta / X developer portals | Meta/X developer-account admin | Higher review friction + churn; usually skip for B2B/internal tools. |

> **"Someone has to register the app" — and it might not be you.** Every provider gates app creation behind a role in *its* portal (the column above). If you don't hold it, registration is an admin's task — surface that before you start, not mid-build. The step-by-step walkthroughs are in [`../skills/add-an-auth-provider/SKILL.md`](../skills/add-an-auth-provider/SKILL.md) (Apple/Microsoft/GitHub) and [`../skills/google-sso-setup/SKILL.md`](../skills/google-sso-setup/SKILL.md) (the full Google worked example). The short form of each is below.

### Registering the OAuth app — per-provider portal walkthrough

The shared shape is always *how to get there* → *register* → *set the callback* → *copy client ID + secret* → *minimal scopes*. Treat every step as `[verify-at-build]` — provider console UIs move constantly.

- **Google** — Google Cloud Console → **APIs & Services → OAuth consent screen** (fill app name + scopes `openid email profile`), then **Credentials → Create Credentials → OAuth 2.0 Client ID** (type *Web application*); add the Supabase callback to **Authorized redirect URIs**. Full version: [`../skills/google-sso-setup/SKILL.md`](../skills/google-sso-setup/SKILL.md).
- **Apple** — [developer.apple.com/account](https://developer.apple.com/account) → **Certificates, Identifiers & Profiles**: register an **App ID** (enable Sign in with Apple), a **Services ID** (your web `client_id`, set return URL = Supabase callback), and a **Sign in with Apple key** → download the **`.p8`**. The client secret is a **generated ES256 JWT**, not a static string (see the Apple section below).
- **Microsoft** — [entra.microsoft.com](https://entra.microsoft.com) → **App registrations → New registration**: pick the **account-type audience**, add platform **Web** redirect URI = Supabase callback, then **Certificates & secrets → New client secret** (copy the *Value* once). Client ID is on the Overview page. Enterprise/admin-consent steps seam to `azure-cloud/entra-identity-engineer`.
- **GitHub** — [github.com/settings/developers](https://github.com/settings/developers) → **OAuth Apps → New OAuth App** (org-owned: the org's Developer settings): set **Authorization callback URL** = Supabase callback, **Generate a new client secret** (copy once), request the `user:email` scope.

In every case the callback to register is Supabase's `https://<project-ref>.supabase.co/auth/v1/callback` (plus your own `…/auth/callback`); store the secret as a **reference** (env-var name / vault URI), never a literal.

> **Microsoft note:** "Sign in with Microsoft" via Supabase's Azure provider covers *consumer + basic work* login. Full enterprise Entra (conditional access, SCIM provisioning, app-role mapping, B2B federation) is `azure-cloud/entra-identity-engineer`'s lane — seam to it rather than forcing it through the generic OAuth path.

---

## Apple Sign In — the gotchas that break first builds

Apple is the provider most likely to fail on the first attempt. The differences from Google, all **verified 2026-06-03**:

- **The client secret is a JWT you generate, not a static string.** You create a key in the Apple Developer portal, then sign a JWT (alg **ES256** — ECDSA P-256 + SHA-256) as the client secret. ([Apple Developer — Creating a client secret](https://developer.apple.com/documentation/accountorganizationaldatasharing/creating-a-client-secret))
- **That JWT expires — max 6 months (180 days).** You must regenerate it before expiry or logins silently start failing. Automate the rotation. ([bannister.me](https://bannister.me/blog/generating-a-client-secret-for-sign-in-with-apple-on-each-request))
- **`client_id` differs web vs native.** Web uses the **Services ID**; a native iOS app uses the **App/bundle ID**. Mismatched `aud` throws `JWTClaimValidationFailed: unexpected "aud" claim value`. ([Better Auth — Apple](https://better-auth.com/docs/authentication/apple))
- **Name + email come back ONLY on the first authorization.** Apple sends the user's name once, on first consent, and never again — there's no userinfo endpoint to fetch it later. **Capture and persist it on first login or lose it.** ([Better Auth — Apple](https://better-auth.com/docs/authentication/apple))
- **"Hide My Email"** gives you a private relay address (`...@privaterelay.appleid.com`); to send mail to it you must register your sending domain with Apple. Treat the relay as the user's real email.
- **No `localhost` / non-HTTPS.** Apple rejects loopback and plain-HTTP redirect URIs — use a tunnel (e.g. a named HTTPS dev domain) for local testing.

With Supabase, most of this is handled by pasting the Services ID + the generated secret into the Apple provider config — but **the 6-month secret rotation and the first-login name capture are still on you.** `[verify-at-build]`

---

## Passwordless

### Magic link (email link)
A one-time, signed link emailed to the user; clicking it creates the session. No password to store, phish, or reset. Supabase supports it natively (`signInWithOtp`). Trade-offs: deliverability and inbox latency become your login funnel; links must be single-use, short-TTL, and rate-limited. Great as the **no-social fallback** so you never force a Google/Apple account.

### Passkeys / WebAuthn (the modern default)
Passkeys are FIDO2/WebAuthn credentials — the user authenticates with Face ID / Touch ID / Windows Hello / a device PIN / a hardware key; the **private key never leaves the authenticator**, the server stores only the public key. They are **phishing-resistant** (bound to the origin) and are the direction the whole industry is moving.

Verified 2026-06-03:
- **Apple, Google, and Microsoft all ship passkeys** across their platforms (joint FIDO commitment); ~50–60% of the top-100 sites support them; the [HID/FIDO 2025 State of Authentication] reports ~**87% of enterprises deploying or piloting** FIDO2 passkeys. ([Security Boulevard](https://securityboulevard.com/2026/04/8-reasons-87-of-enterprises-are-deploying-passkeys-in-2026/), [PanicVault](https://www.panicvault.org/passkeys/adoption-statistics/))
- **Supabase Auth has Passkeys in beta** (built on WebAuthn): enable under **Authentication → Passkeys**, set the Relying Party Display Name, **Relying Party ID** (your bare domain), and **Relying Party Origins** (allow-list); **HTTPS required except loopback**. Because it's **beta**, gate it behind a flag and keep a fallback method. ([Supabase changelog](https://supabase.com/changelog/46458-passkeys-for-supabase-auth-beta), [Supabase docs](https://supabase.com/docs/guides/auth/passkeys))
- Adoption caveat: even where available, only ~15–20% of users have created a passkey — so **offer passkeys, don't *only* offer them.** Pair with a social login or magic link.

### Classic email + password
Still fine, but it's the most work to do *safely* — and a managed provider should own the hashing, breach-check, verification, and rate-limiting; never hand-roll it. If you offer it: require email verification, check against known-breached passwords, rate-limit + lockout on attempts, and never store anything but a strong slow hash (the provider's job). Many 2026 builds **skip standalone passwords entirely** in favor of social + magic-link + passkeys.

---

## How this maps to the build

- **Adding a provider is config, not architecture** (the managed-auth dividend): enable in Supabase → register the callback in the provider console → add one `signInWithOAuth({ provider })` button. The exception is Apple's secret-JWT rotation + first-login name capture.
- **Authentication method ≠ authorization.** Whether the user logs in with Google, Apple, a magic link, or a passkey, the *same* verified `auth.uid()` flows to `data-platform` RLS for row scope. The login method is interchangeable; the seam is not.
- **Account linking:** decide early whether the same person signing in with Google *and* Apple is one account or two. If you key accounts on verified email, Apple's "Hide My Email" relay can fork an identity — plan for explicit account-linking if that matters.

## See also

- Skill: [`../skills/add-an-auth-provider/SKILL.md`](../skills/add-an-auth-provider/SKILL.md) — the generic "add provider X" procedure (with Apple's extra steps)
- Skill: [`../skills/google-sso-setup/SKILL.md`](../skills/google-sso-setup/SKILL.md) — the worked example the others generalize from
- Knowledge: [`oauth-oidc-and-google-sso.md`](oauth-oidc-and-google-sso.md) — the protocol mechanics every provider shares
- Decision tree: [`auth-identity-decision-trees.md`](auth-identity-decision-trees.md) — "Which auth providers should you offer?"

## Sources

All retrieved 2026-06-03: [Apple — Creating a client secret](https://developer.apple.com/documentation/accountorganizationaldatasharing/creating-a-client-secret) · [bannister.me — Apple client secret per request](https://bannister.me/blog/generating-a-client-secret-for-sign-in-with-apple-on-each-request) · [Better Auth — Apple](https://better-auth.com/docs/authentication/apple) · [GitHub Changelog — social login with Apple](https://github.blog/changelog/2025-10-07-github-now-supports-social-login-with-apple/) · [Supabase — Passkeys (beta) changelog](https://supabase.com/changelog/46458-passkeys-for-supabase-auth-beta) · [Supabase — Passkeys docs](https://supabase.com/docs/guides/auth/passkeys) · [Security Boulevard — enterprise passkey adoption 2026](https://securityboulevard.com/2026/04/8-reasons-87-of-enterprises-are-deploying-passkeys-in-2026/) · [PanicVault — passkey adoption stats](https://www.panicvault.org/passkeys/adoption-statistics/)
