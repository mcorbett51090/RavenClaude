# Changelog — auth-identity

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.3.2] — 2026-07-09

Knowledge refresh (finding F5) — **Clerk pricing correction** in [`knowledge/auth-provider-landscape-2026.md`](knowledge/auth-provider-landscape-2026.md). Two prior claims were wrong and are corrected.

### Changed

- **Clerk free tier: ~10K MAU → 50K MRU.** On **2026-02-05** Clerk replaced its old ~10,000-user free tier with **50,000 MRU** (Monthly Retained Users — only users who return ≥24h after signup count, so **MRU ≠ MAU** and is typically lower). Overage above 50K is **~$0.02/MRU**; Pro is $25/mo. The provider table row now states 50K MRU, the MRU≠MAU distinction explicitly, and carries a `[verify-at-use — pricing tier, subject to change; MRU≠MAU]` marker + clerk.com/pricing citation (retrieved 2026-07-09, secondary saasprices.net).
- **Scale checkpoint corrected.** The old "at 50K MAU, Clerk ≈ $800/mo" was wrong (it assumed the retired ~10K free tier + per-MAU billing) — **Clerk is now ≈ $0 at 50K MRU**. The 100K figure is recomputed on the MRU model (only MRU above 50K bill) and marked verify-at-use.

### Notes

- Correction only touches the Clerk row + the scale-checkpoint line + the doc header review-date/sources; all other providers unchanged. Per-MAU/MRU pricing remains volatile — re-verify against the vendor page before quoting.

## [0.3.0] — 2026-06-24

OAuth-app **registration walkthroughs** per social provider — closing the "someone has to register the app, but nothing tells them how to get there or whether they're allowed to" gap. Previously only Google had a full portal walkthrough; Apple/Microsoft/GitHub had a pointer + gotchas but no steps.

### Added

- **`skills/add-an-auth-provider/SKILL.md`** — a "Registering the app — portal walkthrough" subsection for **Apple**, **Microsoft (Entra)**, and **GitHub**, each leading with the **portal URL + nav path**, the **role/permission required to register it** ("if you don't hold it, it's an admin's task"), and numbered steps → client ID/secret + the Supabase callback. Added an upfront "do you have the access to register the app?" note to the generic procedure; Google cross-links to `google-sso-setup` rather than being restated.
- **`knowledge/social-and-passwordless-providers-2026.md`** — a new **"Who can register it"** column on the providers table + a **"Registering the OAuth app — per-provider portal walkthrough"** section (Apple/Microsoft/GitHub short form; Google cross-linked). Every step marked `[verify-at-build]`; the `Last verified: 2026-06-03` discipline preserved.

### Notes

- Reuses, doesn't restate: Apple's ES256-JWT-secret / 180-day-rotation / Services-ID-vs-bundle-ID gotchas stay in their existing section and are linked from the new steps; enterprise Entra (admin consent, conditional access) still seams to `azure-cloud/entra-identity-engineer`.
- Secrets remain a **reference** (env-var name / vault URI), never a literal — consistent with the plugin's anti-pattern hook.

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
