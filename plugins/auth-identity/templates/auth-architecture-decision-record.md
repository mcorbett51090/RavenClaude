# Auth Architecture Decision Record — {{Project / Engagement Name}}

> ADR for the authentication and identity architecture. Fill this in **before** implementation choices are locked. Produced by the `auth-identity` team; reviewed by `ravenclaude-core/security-reviewer` before any production deploy.
>
> **Last updated:** {{YYYY-MM-DD}}
> **Status:** Draft | Proposed | Accepted | Superseded

---

## 1. Context

- **Project / engagement name:** {{...}}
- **Targets to protect:**
  - [ ] Web app (React/Next.js)
  - [ ] API / backend
  - [ ] Analytics dashboard / embedded BI
  - [ ] Other: {{...}}
- **User base:**
  - [ ] Internal team only
  - [ ] Single organization (B2B, one tenant)
  - [ ] Multiple organizations (B2B SaaS, multi-tenant)
  - [ ] Consumers (B2C)
- **Estimated user count:** {{1-50 / 50-500 / 500+}}

---

## 2. Decision: identity provider

**Chosen provider:** {{Supabase Auth / Clerk / Auth0 / Firebase Auth / custom}}

**Rationale:** {{1-2 sentences}}

| Option considered | Verdict | Reason |
|---|---|---|
| **Supabase Auth** | {{Selected / Rejected / Not considered}} | {{e.g., already using Supabase for Postgres + RLS; tight integration with auth.uid() for RLS policies}} |
| **Clerk** | {{...}} | {{...}} |
| **Auth0** | {{...}} | {{...}} |
| **Roll your own** | Rejected unless strong reason | Managed auth removes the highest-risk surface — see `prefer-managed-auth-over-rolling-your-own.md` |

---

## 3. Decision: primary login method

**Chosen:** {{Google SSO (primary) / email+password / magic link / other}}

**Fallback (if any):** {{email+password / magic link / none}}

**Rationale:** {{e.g., builder and users are Google Workspace users; single SSO reduces password fatigue and eliminates credential storage}}

---

## 4. Decision: OAuth/OIDC flow

**Chosen flow:** {{Authorization Code + PKCE / Authorization Code (confidential) / Client Credentials (M2M)}}

**Implicit flow used?** No — deprecated per OAuth 2.0 Security BCP. This is an absolute rule.

| Client type | Flow chosen | Rationale |
|---|---|---|
| SPA (Next.js) | Authorization Code + PKCE | Public client; PKCE prevents code interception |
| API / backend | Authorization Code (confidential) | Can hold client_secret securely |
| M2M / CI service accounts | Client Credentials | No user interaction |

---

## 5. Decision: session strategy

**Chosen:** {{Server-side session / JWT session / Supabase Auth managed session}}

| Dimension | Decision | Notes |
|---|---|---|
| Storage | HttpOnly + Secure + SameSite cookies | Never localStorage or sessionStorage |
| Access token lifetime | {{e.g., 1 hour}} | [unverified — Supabase default] |
| Refresh token rotation | Yes — rotate on every use | Immediate revocation on replay detection |
| Remember-me | {{Yes / No}} | If yes: max {{X}} days; require re-auth for sensitive actions |

---

## 6. Decision: token storage

**Access token stored in:** {{HttpOnly cookie (managed by Supabase SSR / Auth.js)}}

**Refresh token stored in:** {{HttpOnly cookie, SameSite=Strict}}

**localStorage / sessionStorage used for tokens?** No — absolute rule per `never-store-tokens-in-localstorage.md`.

---

## 7. Decision: what is protected

| Resource | Protection method | Auth check location |
|---|---|---|
| `/dashboard` and all sub-routes | Next.js middleware redirect | `middleware.ts` using `getUser()` |
| `/api/*` routes | Session verification in handler | `supabase.auth.getUser()` per route |
| Analytics embed | Login gate + server-issued embed JWT | `gate-the-dashboard` skill + `/api/embed-token` route |
| Static / marketing pages | None (public) | — |

---

## 8. Decision: authorization model

**Model:** {{RBAC / ABAC / RBAC + ABAC hybrid}}

**Roles defined:**

| Role | Description | Can access |
|---|---|---|
| `admin` | Full access | All routes, all data, user management |
| `editor` | Can edit content | Protected routes, own tenant's data |
| `viewer` | Read-only | Protected routes, own tenant's data |
| _(add rows as needed)_ | | |

**Role storage:** {{Supabase app_metadata / application database / JWT custom claims}}

**Default role (when none assigned):** `viewer` — least privilege.

---

## 9. Identity → data authorization seam

**Authentication boundary:** this plugin establishes `auth.uid()` and the user's application role.

**Data authorization boundary:** `data-platform` plugin's RLS layer takes over at the database query level.

- `auth.uid()` is automatically present in all Supabase queries via the JWT in the session cookie.
- Postgres RLS policies in the `data-platform` plugin scope rows by `tenant_id` using `auth.uid()`.
- For embedded analytics: a server-issued short-lived JWT (5-15 min, per data-platform's embed-JWT rule) carries `tenant_id` to the embed tool.
- The `auth-identity` plugin does NOT implement RLS policies or Cube `securityContext` rules.

**Reference:** `data-platform/skills/rls-policy-authoring/SKILL.md`, `data-platform/skills/jwt-embed-issuance/SKILL.md`.

---

## 10. Security review requirements

The following changes require `ravenclaude-core/security-reviewer` sign-off before production deploy:

- [ ] OAuth client registration and consent screen
- [ ] Session cookie configuration
- [ ] Token verification code (signature + iss + aud + exp checks)
- [ ] Embed JWT issuance endpoint
- [ ] Any code that reads or writes `app_metadata` (role management)
- [ ] Logout / revocation flow

**Security reviewer sign-off:** {{Pending / Approved on YYYY-MM-DD by {{name}}}}

---

## 11. Risks and open questions

| Risk / question | Owner | Status |
|---|---|---|
| {{e.g., Google OAuth client not yet created}} | {{name}} | Open |
| {{e.g., Need to verify Supabase app_metadata write behavior}} | {{name}} | Open |
| {{...}} | | |

---

## 12. Migration notes

If this ADR supersedes a previous approach:

- **Previous approach:** {{e.g., username/password with custom session table}}
- **Migration required:** {{e.g., existing users need a password-reset or Google-account-link flow}}
- **Consumer impact:** {{e.g., existing sessions invalidated on deploy}}

---

## 13. Acceptance criteria

- [ ] Google SSO flow completes end-to-end (sign-in, callback, session established)
- [ ] Protected routes redirect unauthenticated users to login
- [ ] API routes return 401 without valid session
- [ ] Auth cookies have `HttpOnly`, `Secure`, `SameSite` flags verified in DevTools
- [ ] `auth.uid()` resolves correctly in a test RLS query
- [ ] Embed JWT issued only after session verification; `tenant_id` from session, not URL
- [ ] `ravenclaude-core/security-reviewer` sign-off completed
- [ ] Cross-boundary denial test passing (see data-platform `rls-cross-tenant-test.sql`)

---

**Refresh triggers for this ADR:**
- Identity provider changes
- New protected target added
- Session strategy changes
- Security incident requiring policy revision
- Quarterly review of [unverified] claims against current provider docs

---

_Generated by `auth-identity` plugin. Re-run the skill if any of the above changes._
