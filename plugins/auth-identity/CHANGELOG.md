# Changelog — auth-identity

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.2.0] — 2026-06-05

Value-add build-out against the full value-add menu. Every menu item was dispositioned (built or recorded N-A with reason); see [`CLAUDE.md`](CLAUDE.md) §12 "Value-add completeness (build-out 2026-06-05)".

### Added

- **scenarios/ bank completed (4 field notes).** The `scenarios/README.md` index listed four scenarios but only one file existed; added the missing three — `oauth-redirect-uri-and-pkce-misconfig` (wildcard redirect + Implicit flow → open-redirect ATO; RFC 9700 exact matching + Auth-Code/PKCE), `passkey-rollout-no-fallback-lockout` (passkey as the only method → lockout; conditional-UI + always-available fallback), and `app-authz-filter-vs-rls-tenant-leak` (app-code tenant filter → IDOR; move row scope to data-platform RLS on `auth.uid()`). All match the 9-field schema.
- **New decision-tree knowledge — `knowledge/mfa-and-auth-method-selection-trees.md`.** Two Mermaid trees complementing PR #315's first-factor trees: (a) which MFA factor to require (FIDO2/hardware → passkey → TOTP → SMS-recovery-only, mapped to NIST SP 800-63B AAL levels), and (b) when to demand step-up (re-)authentication for a sensitive action (freshness window × factor strength × auth-surface-mutation, with out-of-band notify for recovery-surface changes). MFA + step-up were the gaps the existing tree file left open.
- **Runnable analyzer — `scripts/auth_analyze.py`.** Stdlib-only (Python 3.9+), `ruff check`-clean read-only static inspector with three modes: `jwt` (decode-UNVERIFIED + claim lint), `scopes` (least-privilege OAuth scope check), `cookie` (Set-Cookie session-flag lint). Never verifies a signature, calls a provider, or makes a network request — a clean report is not a security sign-off.
- **Advisory anti-pattern hook — `hooks/check-auth-identity-anti-patterns.sh` + `hooks/hooks.json`.** `PreToolUse` (Edit/Write/MultiEdit) flagging six mechanically-detectable auth anti-patterns (token-in-localStorage, OAuth Implicit flow, wildcard `redirect_uri`, unverified JWT decode, hardcoded secret, cookie without HttpOnly). Advisory by default; `AUTH_STRICT=1` makes it blocking. This was the plugin's clear hook gap — it shipped none.
- **CLAUDE.md** §10 (scenarios bank & runnable tooling), §11 (runtime-tier disposition), §12 (value-add completeness table), §13 (milestones); knowledge-bank table updated with the new tree file.

### Decisions (recorded, not built)

- **No bundled MCP server.** Every auth-provider Admin/Management MCP (Supabase, Auth0, Clerk, WorkOS) is per-tenant + authenticated + credentialed (and often write-capable) — the bundled-MCP doctrine sends "per-consumer config OR secret-handling" to **recommend-not-bundle** with a `security-reviewer` gate and the secret as a reference, not an `mcpServers` entry. No invented servers.
- **No LSP `.lsp.json`.** The plugin owns no single-language example codebase (unlike `backend-engineering`); a config would claim a language surface it doesn't have. Revisit if a worked-example codebase ships here.
- **No new skill/command/template.** The existing 7 skills + 4 templates already cover provider-add, Google-SSO, flow design, session/token management, SPA+API protection, RBAC, and dashboard-gating; the genuine gap was the hook (now built). A new skill would gold-plate.

### Verify-at-use

- OAuth 2.1 is still an IETF **draft** (`draft-ietf-oauth-v2-1-15`, late-stage as of 2026-06), not a final RFC — Implicit removed, PKCE mandatory all clients. RFC 9700 (OAuth 2.0 Security BCP) is the published source for exact redirect-URI matching.
- Supabase Passkeys was **beta/experimental** (opt-in, API may change) as of 2026-06; Supabase TOTP MFA is free/default.
- NIST SP 800-63B (rev 4, published 2025-07-31) AAL definitions; FIDO2/WebAuthn capability and provider scope names are volatile — re-confirm against the vendor before quoting.
- The analyzer's `ACCESS_TOKEN_MAX_TTL_SECONDS` (15 min) and the sensitive-scope name list are conventions/heuristics — confirm the provider's recommended TTL and exact scope strings at use.

## [0.1.x] — earlier

2-agent end-user-auth team (auth-architect, auth-implementation-engineer): 7 skills, 4 templates, ~20 best-practices, a 4-doc web-verified knowledge bank; PR #315 added consolidated knowledge decision-trees, the `best-practices/` index, and the first scenario. The authenticate-the-person vs authorize-the-data boundary seams to data-platform; Microsoft/enterprise Entra to azure-cloud; concrete auth code to security-reviewer.
