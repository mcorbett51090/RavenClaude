# Rotate Refresh Tokens on Every Use

**Status:** Absolute rule
**Domain:** Auth & Identity — Token management
**Applies to:** `auth-identity`

---

## Why this exists

A refresh token that does not rotate is a long-lived credential that can be stolen once and used indefinitely. If the token is exfiltrated from a device, a backup, or a compromised session, the attacker silently refreshes access tokens forever — without any re-authentication signal. Refresh token rotation (issue a new refresh token on every use, immediately invalidate the old one) limits the window of a stolen token to the time between the legitimate user's next refresh and discovery. Combined with token-family revocation (invalidating all tokens in the family when a reuse is detected), rotation provides a detectable signal that a token may have been stolen.

## How to apply

**Rotation sequence:**

```
1. Client sends refresh_token_A to the token endpoint.
2. Server verifies refresh_token_A is valid and not revoked.
3. Server issues:
   - New access_token (short-lived: 1 h or less)
   - New refresh_token_B
4. Server marks refresh_token_A as used/revoked (it cannot be reused).
5. Client stores refresh_token_B; discards refresh_token_A.
```

**Token reuse detection (token family):**

```
If refresh_token_A is presented after step 4:
  - It was previously rotated — this is anomalous.
  - Revoke the ENTIRE token family (all refresh tokens issued to this session).
  - Force the user to re-authenticate.
  - Log the event for security audit.
```

**Supabase implementation:** Supabase Auth performs refresh token rotation and reuse detection automatically — `auth.refreshSession()` rotates the token. The behavior is controlled by the `REFRESH_TOKEN_REUSE_INTERVAL` setting (default: 10 seconds, to handle race conditions between concurrent requests).

**Do:**
- Set refresh token lifetime to a value appropriate for the user population (7–30 days for consumer apps; shorter for high-security contexts).
- Implement reuse detection (token family invalidation) on the token endpoint — it converts a single "token was stolen" event into a detectable anomaly.
- Log all refresh token reuse events as security-audit events with the timestamp, IP, and user ID.

**Don't:**
- Issue a static, non-rotating refresh token.
- Share the same refresh token across multiple devices — each device session should have its own token family.
- Set the refresh token lifetime to "never expires" — that is equivalent to a password that cannot be reset.

## Edge cases / when the rule does NOT apply

- **Managed auth providers (Supabase Auth, Clerk, Auth0)**: they handle rotation automatically. Do not reimplement rotation in application code for tokens managed by the provider — configure it in the provider's settings.
- **Short-lived access tokens with no refresh** (rare — user re-authenticates each session): no refresh token to rotate; the rule does not apply.

## See also

- [`../agents/auth-implementation-engineer.md`](../agents/auth-implementation-engineer.md) — implements refresh token rotation in the session middleware
- [`./never-store-tokens-in-localstorage.md`](./never-store-tokens-in-localstorage.md) — the companion rule: refresh tokens live in an HttpOnly cookie, not localStorage

## Provenance

Codifies the anti-pattern "Long-lived, non-rotating refresh tokens with no revocation path on logout" from `CLAUDE.md` §4. Refresh token rotation from OWASP Session Management Cheat Sheet and OAuth 2.0 Security Best Current Practice (RFC 9700, 2025) `[verify-at-build — RFC 9700 status]`. _Last reviewed: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_
