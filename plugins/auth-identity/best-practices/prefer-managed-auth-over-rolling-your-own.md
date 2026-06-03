# Prefer a managed auth provider over rolling your own

**Status:** Pattern — strong default for every project; deviate only when a specific, documented constraint makes a managed provider genuinely unworkable.

**Domain:** Authentication architecture

**Applies to:** `auth-identity`

---

## Why this exists

Authentication is one of the highest-risk surfaces in any application. The attack surface includes:

- Password storage (hashing, salting, breach detection)
- Session token generation and storage
- OAuth/OIDC flow mechanics (PKCE, state, nonce, token validation)
- Refresh token rotation and revocation
- Brute-force and credential-stuffing protection
- MFA / second-factor handling
- Account enumeration defenses
- Token signing key management and rotation

A managed provider (Supabase Auth, Clerk, Auth0, Firebase Auth) has already solved each of these with dedicated security engineering and ongoing patching. Rolling your own means owning all of it, and one mistake in any of these areas can be catastrophic.

The cost of a managed provider (typically $0-$25/month at SMB scale) is orders of magnitude less than the cost of a single auth-related breach or compliance failure.

---

## How to apply

**Default stance:** reach for a managed provider first. For this stack (Next.js + Supabase), Supabase Auth is the natural choice — it is already present, integrates with Postgres RLS via `auth.uid()`, and handles the entire OAuth dance including session management and cookie flags.

| Provider | Best when |
|---|---|
| **Supabase Auth** | Already using Supabase for the database; want tight RLS integration via `auth.uid()`; Next.js stack |
| **Clerk** | Need advanced UI components, organization management, or multi-factor flows out of the box; willing to pay for polish [unverified — pricing as of 2026-06-03] |
| **Auth0** | Enterprise compliance requirements (SOC 2, FedRAMP); complex social provider catalog; existing Auth0 investment |
| **Firebase Auth** | GCP / Firebase stack; Google-first user base; generous free tier [unverified] |
| **Auth.js (NextAuth)** | Need framework-level flexibility without a hosted service; can manage your own session database; cost-sensitive |

**Do:**
- Configure the managed provider's security settings (PKCE on, password strength, MFA optional/required per risk level).
- Let the provider handle token storage — use `@supabase/ssr`, Auth.js adapters, or the SDK's session helpers. Do not extract tokens and re-store them.
- Keep the provider SDK up to date — security patches ship frequently.
- Document the provider choice and rationale in the `auth-architecture-decision-record.md`.

**Don't:**
- Roll your own password hashing (bcrypt/argon2 misconfiguration is a recurring breach cause).
- Implement your own PKCE, state, or nonce mechanics unless a library is not available.
- Build a custom session table without reviewing a managed provider first.
- Use a managed provider but bypass its session management by extracting tokens to localStorage.

---

## When the rule does NOT apply (legitimate deviations)

Document any deviation in the ADR with a specific constraint:

- **Extreme compliance/data-residency requirement** — provider does not offer the required data-residency region and self-hosting is required.
- **Air-gapped / offline environment** — no external auth service connectivity.
- **Existing investment** — a large enterprise already has an IdP (Okta, Azure AD / Entra ID, Ping) and the cost/complexity of adding another provider outweighs the Supabase Auth path. In this case, integrate with the existing IdP via SAML/OIDC federation rather than rolling from scratch.
- **Academic or learning context** — rolling your own in a sandboxed environment to understand the mechanics is fine; do not ship it.

In all cases, any deviation is security-critical — escalate to `ravenclaude-core/security-reviewer`.

---

## Edge cases

- **Supabase Auth + external IdP (Okta/Entra ID):** you can still use Supabase Auth as the front-end layer while federating sign-in to an existing enterprise IdP. Supabase Auth supports SAML 2.0 and generic OIDC providers [unverified — verify in current Supabase Auth docs]. The managed-provider principle still applies.
- **Auth.js without a hosted service:** Auth.js requires you to manage the session database (Postgres, Redis, etc.) and the signing secret. This is closer to "rolling your own" on the session layer — treat it accordingly and route to `ravenclaude-core/security-reviewer`.

---

## See also

- Template: [`../templates/auth-architecture-decision-record.md`](../templates/auth-architecture-decision-record.md) — document the provider choice and rationale
- Skill: [`../skills/google-sso-setup/SKILL.md`](../skills/google-sso-setup/SKILL.md) — implementing the Supabase Auth path
- Security escalation: [`../../ravenclaude-core/agents/security-reviewer.md`](../../ravenclaude-core/agents/security-reviewer.md)

## Provenance

Distilled from this plugin's scope rationale (Supabase Auth as the default managed provider for this stack), OWASP Authentication Cheat Sheet [unverified — verify at owasp.org], and industry consensus that custom authentication implementation is consistently the highest-risk path for application security.

---

_Last reviewed: 2026-06-03 by `claude`_
