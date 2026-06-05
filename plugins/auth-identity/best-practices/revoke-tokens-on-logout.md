# Revoke All Session Tokens on Logout

**Status:** Absolute rule
**Domain:** Auth & Identity — Session lifecycle
**Applies to:** `auth-identity`

---

## Why this exists

A logout that only clears the client-side cookie or wipes the in-memory access token leaves the refresh token alive on the authorization server. An attacker who captured the refresh token before logout can continue to mint new access tokens indefinitely — the user's session "ended" client-side but not server-side. Logout is not complete until the refresh token is invalidated at the server. The anti-pattern "Long-lived, non-rotating refresh tokens with no revocation path on logout" is in `CLAUDE.md` §4.

## How to apply

**Complete logout sequence:**

```
1. Client calls the logout endpoint (POST /auth/signout or provider equivalent).
2. Server revokes the refresh token (marks it as invalid in the token store).
3. Server revokes the access token if the token store supports it (or set access token TTL ≤ 15 min to limit the window).
4. Server clears the session cookie (Set-Cookie: ... Max-Age=0; or Expires=past date).
5. Client clears all in-memory tokens.
6. Client redirects to the sign-in page or home.
```

**Supabase:**
```javascript
// Signs out and revokes the Supabase session server-side
const { error } = await supabase.auth.signOut();
// Optionally: 'local' (clears only this tab), 'global' (revokes all sessions for this user), 'others'
const { error } = await supabase.auth.signOut({ scope: 'global' });
```

**"Sign out everywhere" (all devices):**
- Provide a "sign out all devices" option for high-security contexts.
- This revokes all token families for the user — implemented by deleting all refresh token records for the user ID.
- Supabase: `scope: 'global'` achieves this.

**Do:**
- Call the server-side logout endpoint before clearing client-side tokens — if the server call fails, the user is not fully logged out.
- Set access token TTL to ≤ 15 minutes so even an unrevoked access token expires quickly.
- Audit logout implementations for scenarios where a logout page can be loaded from browser cache and appears to log out without calling the server.

**Don't:**
- Implement logout as only a client-side cookie clear (`document.cookie = 'session=; Max-Age=0'`).
- Treat a 401 response on an expired access token as equivalent to logout — it is not; the refresh token is still alive.
- Skip revocation for "Remember me" tokens — these are the highest-value target and most important to revoke.

## Edge cases / when the rule does NOT apply

- **Stateless JWT access tokens with no refresh token and no server-side session store**: these cannot be revoked (no server state to update). Mitigate by keeping TTL very short (≤ 5 min) and treating access as self-expiring. Document this architectural limitation in the security review.
- **Single-page apps where the access token is memory-only with no refresh token**: clearing memory is sufficient — there is no server-side token to revoke.

## See also

- [`../agents/auth-implementation-engineer.md`](../agents/auth-implementation-engineer.md) — implements the logout endpoint and revocation
- [`./rotate-refresh-tokens-on-use.md`](./rotate-refresh-tokens-on-use.md) — companion rule: tokens that rotate on use are also revoked on logout

## Provenance

Codifies the anti-pattern "Long-lived, non-rotating refresh tokens with no revocation path on logout" from `CLAUDE.md` §4. OAuth 2.0 Token Revocation: RFC 7009. OWASP Session Management Cheat Sheet (verified 2026-06-05). _Last reviewed: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_
