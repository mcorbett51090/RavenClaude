# auth-identity

End-user **authentication & identity** for the three surfaces you actually protect: a **web app** (React/Next.js), an **API/backend**, and an **analytics dashboard** (the marketplace's generated dashboard HTML + embedded BI views). A **variety of login methods** — **Google, Apple, Microsoft, GitHub** social SSO plus **magic link**, **passkeys/WebAuthn**, and email+password — wired through **managed auth (leaning Supabase Auth)**, so adding a provider is config, not architecture. The plugin teaches the full build-vs-buy decision and the per-provider gotchas (especially Apple's).

> **The one boundary to remember:** this plugin **authenticates the person** (login, Google SSO, session, "who are you"). The [`data-platform`](../data-platform/) plugin **authorizes the data** (identity → tenant/row scope, Postgres RLS, embed-JWT). Once you're authenticated here, what rows you see is data-platform's lane. See [`CLAUDE.md`](CLAUDE.md) §0.

## What you get

**2 agents**

| Agent | Role |
|---|---|
| [`auth-architect`](agents/auth-architect.md) | Chooses the auth approach — build-vs-buy provider (leaning Supabase Auth), which OAuth/OIDC flow, session-vs-JWT + token storage — designs how to secure a SPA + API + dashboard, and defines the identity→authorization(RLS) boundary. |
| [`auth-implementation-engineer`](agents/auth-implementation-engineer.md) | Implements the chosen design — Supabase Auth + Google provider wiring, protected routes, API token-verification middleware, secure cookie/session handling, token refresh/rotation, logout/revocation, CSRF. Routes concrete secret/token code to `security-reviewer`. |

**7 skills**

| Skill | What it does |
|---|---|
| `google-sso-setup` | Google Cloud OAuth client + consent screen + redirect URIs, wired through Supabase Auth's Google provider (the worked example the others generalize from). |
| `add-an-auth-provider` | Add **Apple / Microsoft / GitHub** social SSO, **magic link**, **passkeys**, or email+password to an existing Supabase app — the generic enable-provider procedure with each provider's gotchas (Apple's expiring ES256 secret-JWT + first-login name capture front-and-center). |
| `oauth-oidc-flow-design` | Pick the right flow by client type — Authorization Code + PKCE for SPA/native, confidential for server, device code for input-constrained. Never Implicit. |
| `session-and-token-management` | Sessions vs JWTs; where tokens live (memory + HttpOnly/Secure/SameSite cookie, never localStorage); refresh rotation; logout/revocation. |
| `protect-spa-and-api` | Protected routes in the SPA + token-verification middleware on the API; CSRF defense. |
| `authorization-rbac` | Roles/permissions on top of authenticated identity — and the hand-off line to data-platform RLS for *row* scope. |
| `gate-the-dashboard` | Put the analytics dashboard behind login — static-host auth vs reverse-proxy vs app-shell + embed-JWT (the seam to data-platform). |

**4 knowledge docs** — [`auth-provider-landscape-2026.md`](knowledge/auth-provider-landscape-2026.md) (build-vs-buy + per-MAU pricing), [`oauth-oidc-and-google-sso.md`](knowledge/oauth-oidc-and-google-sso.md) (protocol + Google specifics), [`social-and-passwordless-providers-2026.md`](knowledge/social-and-passwordless-providers-2026.md) (the variety pack — Apple/Microsoft/GitHub + magic-link/passkeys, web-verified), [`auth-identity-decision-trees.md`](knowledge/auth-identity-decision-trees.md) (5 Mermaid trees incl. "which providers should you offer?").

## The build-vs-buy stance (Supabase-Auth lean)

Prefer **managed auth over rolling your own crypto.** Password hashing, token signing, key rotation, breach monitoring and OAuth edge cases are a deep adversarial surface — a managed provider owns them so you don't. The lean here is **Supabase Auth**, because it does Google SSO + session management out of the box *and* its JWT maps cleanly to Postgres `auth.uid()` for Row-Level Security — which is exactly the synergy the `data-platform` plugin (already Supabase/Postgres-leaning) needs for the authorization handoff. The plugin still teaches when **Clerk** (best DX), **Auth0/WorkOS** (enterprise SSO), **Firebase/Cognito** (in-cloud), or **OSS self-host** (Keycloak / Authentik / Auth.js / Better Auth — for data-residency / no-third-party constraints) is the right call instead.

## The data-platform seam

Authentication establishes *who* the user is and hands off a trustworthy subject claim (Supabase `auth.uid()` or a verified `sub`). **`data-platform` consumes that claim to scope rows** via its `rls-policy-authoring`, `jwt-embed-issuance`, and `embed-csp-and-iframe-sandboxing` skills. This plugin does **not** duplicate RLS/embed mechanics; for "show each tenant only its rows," the auth gate is ours and the row scope is theirs, with the embed-JWT as the contract between them.

## When to use

- "Add **Sign in with Google** to my React/Next app."
- "Should I use **Supabase Auth, Clerk, Auth0, or roll my own**?"
- "Which **OAuth flow** for my SPA / API / mobile app?"
- "**Gate my analytics dashboard** behind login."
- "Verify tokens in my API / add middleware / secure cookies / refresh rotation / logout + CSRF."

**Seams:** `azure-cloud/entra-identity-engineer` (Microsoft Entra), `web-design` (login UI), `data-platform` (RLS / embed-JWT / data authorization), `ravenclaude-core/security-reviewer` (mandatory review of concrete auth code).

> **Requires `ravenclaude-core@>=0.7.0`.** Install via `/plugin marketplace add ./` then `/plugin install auth-identity@ravenclaude`.
