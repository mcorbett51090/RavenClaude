---
scenario_id: 2026-06-05-oauth-redirect-uri-and-pkce-misconfig
contributed_at: 2026-06-05
plugin: auth-identity
product: oauth-oidc
product_version: "unknown"
scope: likely-general
tags: [oauth, redirect-uri, pkce, implicit-flow, open-redirect]
confidence: high
reviewed: false
---

## Problem

A "Sign in with Google" integration on a multi-environment app registered a **wildcard-ish** redirect URI (`https://app.example.com/*`) on its OAuth client "so staging and PR-preview subdomains would work too," and the SPA was still on the legacy **Implicit** flow (`response_type=token`) inherited from a 2019 sample. A researcher reported account takeover: an **open redirect** on a marketing path (`/r?to=…`) under the same registered host let them bounce the authorization response — with the access token in the URL fragment — to an attacker-controlled page. Because the flow was Implicit, there was no PKCE `code_verifier` binding the response to the originating client, so the leaked token was immediately usable. The wildcard meant the IdP never rejected the attacker's `redirect_uri`.

## Context

- Surface: a public-client SPA + a Google OAuth client shared across dev/staging/prod, registered with a broad redirect pattern to avoid per-environment client management.
- Constraint: two independent defects compounded — (1) **non-exact redirect-URI matching** (RFC 9700 requires exact string matching, no wildcards/patterns), and (2) **Implicit flow** (removed in OAuth 2.1; token in the fragment is unbindable and lands in history/logs/`Referer`). Either alone is serious; together they are a one-click ATO.
- This is a concrete auth-flow change touching a live OAuth client → **mandatory `ravenclaude-core/security-reviewer`** before it ships (CLAUDE.md §8).

## Attempts

- Tried: "just remove the open redirect on `/r?to=`." Outcome: rejected as the load-bearing fix. The open redirect is the *delivery* vehicle, but the wildcard redirect-URI registration + Implicit flow are the *exposure* — patching one open-redirect path leaves the next one (a new marketing link, an SSO logout `returnTo`, an `og:` preview fetcher) just as exploitable. Kept as defense-in-depth only.
- Tried: register **exact** redirect URIs per environment (`https://app.example.com/auth/callback`, `https://staging.example.com/auth/callback`, …) — separate OAuth clients per environment so prod never trusts a staging/preview origin. Outcome: the IdP now rejects any `redirect_uri` not on the exact allow-list; PR-preview subdomains use their own dev client, not the prod one.
- Tried (completing the fix): migrate the SPA from Implicit to **Authorization Code + PKCE** (what Supabase's `signInWithOAuth` already does), and verify the provider client has any "legacy/implicit/compatibility" mode disabled so PKCE can't be downgraded. Outcome: the authorization response is now a one-time `code` bound to the client's `code_verifier`; a bounced/stolen code can't be exchanged by the attacker, and there is no token in the fragment to leak.

## Resolution

The exposure was **non-exact redirect-URI matching plus the Implicit flow**, not the specific open-redirect path. Exact per-environment redirect URIs (separate clients), Authorization Code + PKCE with legacy mode off, and removing the open redirect as defense-in-depth closed it.

**Action for the next engineer hitting this pattern:** when an OAuth/SSO integration is involved in an account-takeover report, check the **redirect-URI registration first** — any wildcard, path-prefix, or shared-across-environments pattern is the finding (RFC 9700 wants exact matching), and confirm the flow is **Authorization Code + PKCE, not Implicit** (OAuth 2.1 removed Implicit). Traverse the **which-OAuth-flow-by-client-type** tree in [`../knowledge/auth-identity-decision-trees.md`](../knowledge/auth-identity-decision-trees.md), apply the [`validate-redirect-uris-exactly`](../best-practices/validate-redirect-uris-exactly.md) and [`use-authorization-code-pkce-never-implicit`](../best-practices/use-authorization-code-pkce-never-implicit.md) best-practices, and route the change through `security-reviewer`.

**Sources (retrieved 2026-06-05):**
- IETF — OAuth 2.0 Security Best Current Practice (RFC 9700): exact redirect-URI matching; PKCE for all clients — https://datatracker.ietf.org/doc/rfc9700/
- IETF — OAuth 2.1 (`draft-ietf-oauth-v2-1-15`, late-stage draft as of 2026-06): Implicit grant removed, PKCE mandatory for all client types — https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/
- OWASP — Open Redirect attack reference — https://owasp.org/www-community/attacks/open_redirect
- Plugin best-practices: [`../best-practices/validate-redirect-uris-exactly.md`](../best-practices/validate-redirect-uris-exactly.md), [`../best-practices/use-authorization-code-pkce-never-implicit.md`](../best-practices/use-authorization-code-pkce-never-implicit.md), [`../best-practices/pkce-verifier-is-one-use-only.md`](../best-practices/pkce-verifier-is-one-use-only.md)

OAuth 2.1 is still an IETF **draft** (not a final RFC); RFC 9700 is published BCP. `[verify-at-use]` the current OAuth-2.1 draft revision and any provider-specific "legacy mode" naming before quoting.
