# Auth-identity Plugin — Team Constitution

> Team constitution for the `auth-identity` Claude Code plugin. Bundles **2** specialist agents for **end-user authentication & identity** across the three surfaces a builder protects: a **web app** (React/Next.js), an **API/backend**, and an **analytics dashboard** (the marketplace's generated dashboard HTML + embedded BI views).
>
> **Orientation:** this file is **domain-specific** to authentication / identity work. For the domain-neutral team constitution inherited by every plugin (architect, coders, reviewers, project-manager, etc.), see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).
>
> **Requires `ravenclaude-core@>=0.7.0`** — inherits the Capability Grounding Protocol, the Structured Output Protocol, the Claim-Grounding discipline, and the mandatory `security-reviewer` escalation for concrete auth/secret/token code.

---

## 0. The load-bearing boundary — AUTHENTICATE the person, not AUTHORIZE the data

**This plugin AUTHENTICATES THE PERSON.** Login, "Sign in with Google", the OAuth/OIDC dance, ID-token validation, session/cookie management, refresh/rotation, logout/revocation, "who is this user." That is the whole lane.

**The `data-platform` plugin AUTHORIZES THE DATA.** Once a person is authenticated *here*, mapping their identity to a tenant/row scope — and enforcing it — is data-platform's lane: its [`rls-policy-authoring`](../data-platform/skills/rls-policy-authoring/SKILL.md), [`jwt-embed-issuance`](../data-platform/skills/jwt-embed-issuance/SKILL.md), and [`embed-csp-and-iframe-sandboxing`](../data-platform/skills/embed-csp-and-iframe-sandboxing/SKILL.md) skills, plus its `issue-short-lived-jwts-for-embeds` and `embed-never-ship-the-service-key` best-practices.

```
  [ auth-identity ]                         [ data-platform ]
  authenticate the PERSON      --seam-->     authorize the DATA
  login · Google SSO · OIDC                  identity → tenant/row scope
  session · cookie · token                   Postgres RLS · auth.uid()
  "who are you?"                             embed-JWT · CSP · "what rows?"
```

**The seam, stated precisely:** auth-identity establishes the authenticated identity and hands off a trustworthy subject claim (e.g. Supabase's `auth.uid()`, or a verified `sub`). data-platform consumes that claim to scope rows. **We never duplicate embed/RLS mechanics here, and data-platform never re-implements the login flow.** When a task needs both — "gate the analytics dashboard behind Google login *and* show each tenant only its rows" — auth-identity owns the gate, data-platform owns the row scope, and the embed-JWT is the contract between them.

---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`auth-architect`](agents/auth-architect.md) | The auth **decisions**: build-vs-buy provider choice (leaning Supabase Auth), which OAuth/OIDC flow, session-vs-JWT strategy, where tokens live; the design for securing a SPA + API + dashboard; and the identity→authorization(RLS) boundary. | "add Sign in with Google to my React/Next app"; "Supabase Auth, Clerk, or roll my own?"; "gate my analytics dashboard behind login"; "which OAuth flow for my SPA?" |
| [`auth-implementation-engineer`](agents/auth-implementation-engineer.md) | Implementing the chosen design: Supabase Auth + Google provider wiring, protected routes, API token-verification middleware, secure cookie/session handling, token refresh/rotation, logout/revocation, CSRF defense. | "wire up Supabase Auth Google provider in Next.js"; "add token-verification middleware to my API"; "set up secure cookie sessions + refresh rotation"; "add logout + CSRF protection" |

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates. If work crosses the design/implementation line, each agent returns its slice and the Team Lead re-dispatches. **Every concrete auth-code / secret / token change routes through `ravenclaude-core/security-reviewer` before it ships** (the marketplace house rule).

---

## 2. Routing rules (Team Lead)

- **"Should I use Supabase Auth / Clerk / Auth0 / roll my own?"** → `auth-architect` (build-vs-buy, reads [`knowledge/auth-provider-landscape-2026.md`](knowledge/auth-provider-landscape-2026.md)).
- **"Which OAuth flow for my SPA / API / mobile app?"** → `auth-architect` (reads [`knowledge/oauth-oidc-and-google-sso.md`](knowledge/oauth-oidc-and-google-sso.md) + the flow decision tree).
- **"Add Sign in with Google to my React/Next app"** → `auth-architect` designs (provider + flow + session strategy), `auth-implementation-engineer` wires the Supabase Google provider + callback route.
- **"Gate my analytics dashboard behind login"** → `auth-architect` chooses the gate pattern (static-host auth vs reverse-proxy vs app-shell + embed-JWT); **the row-scope of what they see after the gate seams to `data-platform`**.
- **"Verify tokens in my API / add middleware / refresh rotation / logout"** → `auth-implementation-engineer`.
- **Any concrete auth code, secret handling, token signing/verification, cookie flags, or session change** → **mandatory `ravenclaude-core/security-reviewer`** before merge.
- **Microsoft Entra ID / Azure AD specifics** (enterprise SSO, conditional access, app registrations) → seam to `azure-cloud/entra-identity-engineer`.
- **Login/sign-up UI, consent screens, account-settings pages** → seam to `web-design` (this plugin owns the auth flow, not the pixels).
- **What rows/tenant a user sees after login (RLS, embed-JWT, CSP)** → seam to `data-platform`.

---

## 3. Cross-cutting house opinions (every agent enforces)

1. **Prefer managed auth over rolling your own crypto.** Password hashing, token signing, key rotation, breach monitoring, and OAuth edge cases are a deep, adversarial surface. A managed provider (lean: **Supabase Auth**) is the default; "roll your own" is justified only by a hard constraint (data-residency, air-gap, no-third-party mandate) documented in the decision record. Even then, build on a vetted library — never hand-roll the crypto.
2. **Authorization Code + PKCE, never Implicit.** The Implicit grant is **removed in OAuth 2.1** — the access token in the URL fragment lands in browser history, logs, and the `Referer` header, can't be sender-constrained, and can't use PKCE. Authorization Code + PKCE is the current recommendation for SPAs and native/mobile; PKCE is mandatory for *every* client type in OAuth 2.1, including confidential server clients. _(Verified 2026-06-03 — see [`knowledge/oauth-oidc-and-google-sso.md`](knowledge/oauth-oidc-and-google-sso.md).)_
3. **Never store tokens in `localStorage`/`sessionStorage`.** Both are readable by any JS in the origin, so a single XSS discloses every token. The 2026 default: short-lived access token in **memory**, refresh token in an **HttpOnly + Secure + SameSite** cookie the browser sends automatically and JS cannot read. _(OWASP — verified 2026-06-03.)_
4. **Cookie sessions imply CSRF defense.** `SameSite=Lax`/`Strict` blocks most cross-site cookie sends; add an anti-CSRF token on state-changing requests as defense-in-depth for high-value operations.
5. **Validate ID tokens server-side — never trust client claims.** An ID token presented by the browser must be verified on the server: signature against the issuer's rotating JWKS, `iss` ∈ {`accounts.google.com`, `https://accounts.google.com`}, `aud` == your client ID, `exp` not passed (and `nonce` when you set one). A claim the client could have forged is not an identity. _(Google Identity — verified 2026-06-03.)_
6. **Least-privilege scopes.** Request only the OAuth scopes the feature needs (`openid email profile` for plain SSO). Don't request Gmail/Drive/Calendar scopes "just in case" — broad scopes trigger Google verification, scare users on the consent screen, and widen the blast radius of a token leak.
7. **AUTHENTICATE-the-person vs AUTHORIZE-the-data is a hard boundary** (§0). Identity is ours; row/tenant scope seams to data-platform RLS. We never make app-code tenant filters the load-bearing control — that is data-platform's closest-to-data invariant.
8. **Security-sensitive changes escalate.** Every concrete auth-code/secret/token change routes through `ravenclaude-core/security-reviewer`. Design freely; ship through review.
9. **Volatile claims carry a retrieval date.** Provider pricing (per-MAU), flow-deprecation status, and Google/Supabase mechanics change; every such claim in this plugin's knowledge bank has a `Last verified` / retrieval date and is re-verified before quoting.

---

## 4. Anti-patterns every agent flags

- Rolling a custom password store / token-signer when a managed provider fits the constraints (reinventing adversarial crypto).
- **Implicit flow** (`response_type=token`) on any new build — deprecated/removed; migrate to Authorization Code + PKCE.
- Tokens in `localStorage`/`sessionStorage` (one XSS = total token theft).
- Trusting an ID token's claims **client-side** without server-side signature + `iss`/`aud`/`exp` validation.
- Over-broad OAuth scopes requested "just in case" (consent-screen friction + verification + blast radius).
- A cookie-session app with no CSRF defense (no `SameSite`, no anti-CSRF token on writes).
- Long-lived, non-rotating refresh tokens with no revocation path on logout.
- **App-code tenant filtering treated as the auth boundary** — that conflates authentication with authorization; row scope belongs to data-platform RLS.
- Hard-coding a client secret / signing key / service key in source (must live in env / a secret store; the service key never reaches the browser).
- Shipping concrete auth/token code without routing it through `security-reviewer`.

---

## 5. Capability Grounding Protocol (Anti-Hallucination)

This plugin inherits the Capability Grounding Protocol from `ravenclaude-core`. Before any auth-identity agent says "I can't do X" or asserts a volatile platform fact, it must:

1. **Check the knowledge bank + decision trees first** — [`auth-provider-landscape-2026.md`](knowledge/auth-provider-landscape-2026.md), [`oauth-oidc-and-google-sso.md`](knowledge/oauth-oidc-and-google-sso.md), [`auth-identity-decision-trees.md`](knowledge/auth-identity-decision-trees.md) — and **traverse the relevant decision tree top-to-bottom** before selecting a method (provider, flow, token-storage, dashboard-gate). Don't keyword-match; resolve the first clean branch.
2. **Check for partial capability** — can part complete (e.g. the design, or a reviewable scaffold) even if a live provider key isn't available?
3. **Try alternative paths easiest-first before declaring blocked** — provider (Supabase → Clerk → Auth0 → OSS); flow (Auth-Code+PKCE → confidential server → device code for input-constrained); dashboard gate (static-host auth → reverse-proxy → app-shell + embed-JWT).
4. **Consider team composition** — could `ravenclaude-core/architect`/`security-reviewer`, `data-platform`, `azure-cloud/entra-identity-engineer`, or `web-design` own part?
5. **Escalate uncertainty** with the mandatory phrasing: *"After trying [A — outcome] and [B — outcome], I cannot fully complete this because [specific reason]. Remaining options I considered but did not attempt are [X (ruled out because Y)]. I can help with [partial scope]. I recommend [escalation / next-best path]."*

Volatile facts (provider pricing, flow-deprecation status, Google/Supabase mechanics) carry inline `[verify-at-build]` / `[unverified — training knowledge]` markers per the Claim-Grounding discipline. See [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md).

---

## 6. Output Contract (every auth-identity agent)

Every report from every auth-identity agent **must** include:

```
Status: ✅  |  ⚠️ partial  |  ❌ blocked
Files changed: <relative paths or "none">
Surface(s): <web-app | API | dashboard | mixed>
Auth decision: <provider · flow · session/token strategy · token storage>
Identity↔authorization boundary: <how the verified identity hands off to data-platform RLS, or "n/a — single-user / no row scope">
Security-review status: <required-and-routed | n/a (design-only, no concrete secret/token code)>
Volatile claims with retrieval dates: <pricing / flow-status / provider-mechanics referenced; "Vendor X $Y/MAU as of YYYY-MM-DD" or "n/a">
Grounding checks performed: <decision trees traversed / knowledge files read before stating any limitation>
```

**Plus the cross-plugin Structured Output Protocol JSON block** appended after the Markdown report. See [`../ravenclaude-core/skills/structured-output/SKILL.md`](../ravenclaude-core/skills/structured-output/SKILL.md) for the canonical schema; extend with `surfaces`, `auth_decision`, and `security_review_status` fields.

---

## 7. Knowledge bank

| File | Read when |
|---|---|
| [`knowledge/auth-provider-landscape-2026.md`](knowledge/auth-provider-landscape-2026.md) | Build-vs-buy; choosing a managed provider (Supabase Auth / Clerk / Auth0 / WorkOS / Firebase / Cognito / Stytch) vs OSS/self-host (Keycloak / Authentik / Auth.js / Better Auth); per-MAU pricing caution; **why Supabase Auth is the lean here.** |
| [`knowledge/oauth-oidc-and-google-sso.md`](knowledge/oauth-oidc-and-google-sso.md) | The protocol reference — OAuth 2.0 vs OIDC, the flows (Auth-Code+PKCE / confidential / device; Implicit deprecated), ID/access/refresh tokens, **Google SSO specifics** (Cloud OAuth client, consent screen, redirect URIs, scopes, ID-token validation), and how Supabase Auth wraps Google → Postgres `auth.uid()`. |
| [`knowledge/social-and-passwordless-providers-2026.md`](knowledge/social-and-passwordless-providers-2026.md) | The **variety pack** — which login methods to offer: Google / **Apple** (its secret-JWT-expiry + first-login-name gotchas) / Microsoft / GitHub social SSO, plus **magic link** and **passkeys/WebAuthn** (Supabase beta) and email+password. "Adding a provider is config, not architecture" via Supabase. Read when choosing or adding login methods. |
| [`knowledge/auth-identity-decision-trees.md`](knowledge/auth-identity-decision-trees.md) | Mermaid **first-factor** trees: build-vs-buy, which providers, which OAuth flow by client type, session-vs-JWT + token storage, gate-the-dashboard (the seam to data-platform), logout-revocation, refresh-reuse detection. Traverse before selecting a method. |
| [`knowledge/mfa-and-auth-method-selection-trees.md`](knowledge/mfa-and-auth-method-selection-trees.md) | Mermaid **second-factor / re-auth** trees: which MFA factor to require (FIDO2/passkey/TOTP/SMS by NIST AAL), and when to demand step-up authentication for a sensitive action (freshness window × factor strength × auth-surface-mutation). Traverse before choosing a factor or gating a sensitive action. |

The plugin's 7 skills (`add-an-auth-provider`, `google-sso-setup`, `oauth-oidc-flow-design`, `session-and-token-management`, `protect-spa-and-api`, `authorization-rbac`, `gate-the-dashboard`), 4 templates, and 5 best-practices operationalize these docs. The knowledge bank is the source of truth; inline priors on the agents point back here. `add-an-auth-provider` + the `social-and-passwordless-providers-2026` doc cover the **variety pack** (Apple/Microsoft/GitHub/magic-link/passkeys) beyond the Google worked example.

---

## 8. Escalating out of the auth-identity team

- **`ravenclaude-core/security-reviewer`** — **mandatory** for any concrete auth code, secret handling, token signing/verification, cookie flags, or session change.
- **`ravenclaude-core/architect`** — broader system/identity architecture beyond the auth surface.
- **`data-platform`** — **the authorization lane.** Identity→tenant/row scope, Postgres RLS (`auth.uid()`), embed-JWT issuance, embed CSP/iframe-sandboxing. The seam in §0.
- **`azure-cloud/entra-identity-engineer`** — Microsoft Entra ID / Azure AD: enterprise SSO, app registrations, conditional access, B2B/B2C.
- **`web-design`** — login/sign-up/consent/account-settings UI (this plugin owns the flow, not the pixels).
- **`ravenclaude-core/deep-researcher`** — re-verifying provider pricing or post-cutoff flow/spec status (per-MAU pricing is volatile; quarterly refresh discipline).
- **`ravenclaude-core/documentarian`** / **`project-manager`** — stakeholder-facing auth-design deliverables / engagement RAID.

---

## 9. References

- Domain-neutral team constitution: [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md)
- Capability Grounding Protocol (upstream): [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md)
- Structured Output Protocol (upstream): [`../ravenclaude-core/skills/structured-output/SKILL.md`](../ravenclaude-core/skills/structured-output/SKILL.md)
- The authorization seam: [`../data-platform/CLAUDE.md`](../data-platform/CLAUDE.md) §3 (tenant-isolation invariant), its `rls-policy-authoring` + `jwt-embed-issuance` + `embed-csp-and-iframe-sandboxing` skills.

---

## 10. Scenarios bank & runnable tooling (added v0.2.0)

- **Scenarios bank** — [`scenarios/`](scenarios/) holds dated, scope-tagged, **unverified** field notes (the marketplace scenarios pattern; see [`../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../ravenclaude-core/skills/scenario-retrieval/SKILL.md)). Surface a matching scenario only as a **secondary** source, behind the mandatory unverified-scenario preamble ("Based on N unverified scenarios from YYYY-MM tagged [scope] — verify in your environment"), never overriding the cited knowledge bank or best-practices. The four current notes: token-in-localStorage XSS exfil (session-fixation + non-revocable refresh), OAuth redirect-URI + PKCE/Implicit misconfig (open-redirect ATO), passkey rollout with no fallback (lockout), and app-authz-filter-vs-RLS tenant leak (IDOR). Both agents should check the bank when a situation matches. Every concrete auth/secret/token change still routes through `ravenclaude-core/security-reviewer` (§8).
- **Runnable analyzer** — [`scripts/auth_analyze.py`](scripts/auth_analyze.py) (stdlib only, Python 3.9+) is a **read-only static inspector** with three modes: `jwt` (decode-UNVERIFIED + claim lint — alg=none, HS256-on-public-client, missing/over-long `exp`, missing iss/aud/sub), `scopes` (least-privilege check of requested OAuth scopes vs a feature floor + sensitive-scope flags), and `cookie` (Set-Cookie HttpOnly/Secure/SameSite + token-in-JS-readable-cookie lint). It **never verifies a signature, calls a provider, or makes a network request** — it lints only what the user pastes. A clean report is **not** a security sign-off; concrete changes still route through `security-reviewer` (§8). Owned by both agents; `auth-architect` uses `scopes`, `auth-implementation-engineer` uses `jwt` + `cookie`.

## 11. Technical-runtime tier — disposition

End-user auth/identity work is mostly **design + provider configuration + small client/server code changes**, not a single-language codebase, so the heavier runtime tiers are dispositioned honestly:

- **LSP code intelligence — N-A.** This plugin does not ship example code in one language the way `backend-engineering` does (Node/Python/Go); auth work spans whatever stack the consumer brings, and the plugin's value is design + provider config + targeted snippets. A bundled `.lsp.json` would claim a language surface the plugin doesn't own. If a future worked-example codebase ships here, revisit with backend-engineering's `.lsp.json` as the model.
- **Bundled MCP server — N-A (recommend-not-bundle).** Per [`../../docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md), a bundled server must be **zero-config and read-only**. Every auth-useful server fails that bar: a provider Admin/Management server (Supabase, Auth0, Clerk, WorkOS) is **per-tenant + authenticated + credentialed** (an admin/service key = a secret) → the rule sends "per-consumer config OR secret-handling" to **recommend, don't bundle**, and a write-capable admin server is an Absolute-rule `security-reviewer` gate besides. **No invented servers.** When a consumer genuinely needs live provider context, document the recommended `claude mcp add …` path with the secret as a **reference** (env-var name / vault URI, never a literal), least-privilege scope, and a mandatory `security-reviewer` sign-off before adoption — exactly the recommend-not-bundle posture, not an `mcpServers` entry.
- **Advisory anti-pattern hook — BUILT.** [`hooks/check-auth-identity-anti-patterns.sh`](hooks/check-auth-identity-anti-patterns.sh) (`PreToolUse` on Edit/Write/MultiEdit, registered in [`hooks/hooks.json`](hooks/hooks.json)) flags six mechanically-detectable auth anti-patterns: token in localStorage/sessionStorage, OAuth Implicit flow, wildcard/non-exact `redirect_uri`, JWT decoded-without-verify, hardcoded secret/signing/service key, and a cookie set without HttpOnly. **Advisory by default** (exit 0 + a notice); `AUTH_STRICT=1` makes it blocking. Heuristic, not a security review — a clean run is not a sign-off, and concrete changes still escalate to `security-reviewer` (§8). This was the plugin's clear hook gap (it shipped none).

## 12. Value-add completeness (build-out 2026-06-05)

Disposition of every value-add menu item (built vs. recorded N-A with reason):

| # | Item | Disposition |
|---|---|---|
| 1 | **scenarios/ bank** | **BUILT** — 4 scenarios (token-in-localStorage XSS, OAuth redirect/PKCE misconfig, passkey-no-fallback lockout, app-authz-vs-RLS tenant leak) matching the existing `scenarios/README.md` index + the 9-field schema. (1 pre-existed; this build-out added the 3 the README indexed but were missing.) |
| 2 | **Decision-tree knowledge** | **BUILT** — `knowledge/mfa-and-auth-method-selection-trees.md`: two NEW Mermaid trees (MFA-factor selection by NIST AAL; step-up auth for sensitive actions) complementing PR #315's first-factor trees, which already covered build-vs-buy / providers / OAuth-flow / session-token / dashboard-gate / logout / refresh-reuse. MFA + step-up were the genuine gaps. |
| 3 | **Bundled MCP server** | **N-A (recommend-not-bundle)** — §11. Every auth-provider Admin/Management MCP is per-tenant + credentialed + (often) write-capable → recommend-not-bundle + `security-reviewer` gate, secret as a reference not a literal. No invented servers. |
| 4 | **LSP server** | **N-A** — §11. The plugin owns no single-language example codebase; a `.lsp.json` would claim a surface it doesn't have. Revisit if a worked-example codebase ever ships. |
| 5 | **Runnable script** | **BUILT** — `scripts/auth_analyze.py` (`jwt` / `scopes` / `cookie`), stdlib-only, ruff-clean, read-only inspector (never verifies signatures or calls a provider). Real value: turns three recurring review checks into one command. |
| 6 | **bin/ · monitors · output-styles · settings defaults · themes** | **N-A** — no groundable, broadly-valuable instance. Auth deliverables are design docs + provider config + targeted code, governed by the §6 Output Contract; nothing to watch, no compiled binary, no styling surface specific to this domain. |
| 7 | **skills / hooks / commands / templates** | **Hook BUILT** (the clear gap — the plugin shipped none): `hooks/check-auth-identity-anti-patterns.sh` (6 advisory anti-pattern checks). The existing **7 skills + 4 templates** already cover provider-add, Google-SSO, flow design, session/token management, SPA+API protection, RBAC, and dashboard-gating; a new skill/command would gold-plate. |
| 8 | **CHANGELOG.md** | **BUILT** — added with a top `0.2.0` entry. No `NOTICE.md` (nothing third-party is bundled; the script is original stdlib-only; all sources cited inline). |

## 13. Milestones

- **v0.1.x** — initial release: 2 agents (auth-architect, auth-implementation-engineer), 7 skills, 4 templates, ~20 best-practices, a 4-doc web-verified knowledge bank, and (PR #315) consolidated knowledge decision-trees + `best-practices/` index + the first scenario.
- **v0.2.0** — value-add build-out: scenarios bank completed (4 scenarios), `mfa-and-auth-method-selection-trees.md` (MFA-factor + step-up trees), `scripts/auth_analyze.py` (jwt/scopes/cookie analyzer), `hooks/check-auth-identity-anti-patterns.sh` (advisory anti-pattern hook + `hooks.json`), CHANGELOG. LSP + bundled-MCP dispositioned N-A with reasons (§11–§12).
