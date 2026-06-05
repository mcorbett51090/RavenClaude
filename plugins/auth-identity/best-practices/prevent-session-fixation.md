# Regenerate the Session ID on Every Login

**Status:** Absolute rule
**Domain:** Auth & Identity — Session security
**Applies to:** `auth-identity`

---

## Why this exists

Session fixation is an attack where an adversary plants a known session identifier in the victim's browser before they authenticate. If the server reuses that pre-authentication session ID after login, the attacker — who already knows the ID — immediately has an authenticated session. The fix is a single, mandatory step: **issue a fresh session ID at the moment authentication succeeds**, invalidating any pre-auth session. Managed providers (Supabase Auth, Clerk, Auth0) handle this correctly by design — they always issue a new session on login. The risk is highest in custom session middleware or frameworks where session handling is implemented manually. This rule exists because the fix is trivially easy and the consequences of forgetting it are severe.

## How to apply

**Managed provider (Supabase Auth / Clerk / Auth0):**

The provider's `signIn` / `signInWithOAuth` / `signInWithPassword` methods create a new session object and new tokens. Verify in your implementation that you are not preserving any pre-auth session state into the post-auth context. Do not copy an anonymous session cookie value to an authenticated context.

**Custom session middleware (Express, Hapi, custom Next.js):**

```typescript
// Express example using express-session
app.post("/login", async (req, res) => {
  const user = await authenticate(req.body.email, req.body.password);
  if (!user) return res.status(401).json({ error: "Invalid credentials" });

  // CRITICAL: regenerate the session before writing auth state
  req.session.regenerate((err) => {
    if (err) return next(err);
    req.session.userId = user.id;         // write auth state AFTER regenerate
    req.session.authenticatedAt = Date.now();
    res.json({ ok: true });
  });
});
```

**What "regenerate" does:** the session store creates a new session record with a new cryptographically random ID, copies no data from the old session into it (unless you explicitly do so), and instructs the browser to replace its cookie with the new ID. The old ID is invalidated in the store.

**Do:**
- Call `session.regenerate()` (or the equivalent) immediately after verifying credentials, before writing any auth state to the session.
- Also regenerate on privilege escalation (e.g., a user elevates to an admin role mid-session).
- Clear the old session from the store immediately — do not leave it as a dangling record.
- Use a cryptographically random session ID (≥128 bits of entropy) — never an incrementing integer, user ID, or other predictable value.

**Don't:**
- Copy the pre-auth session's shopping cart or other state into the new session by default — evaluate what is safe to carry forward.
- Regenerate only on the next request after login — regenerate before the `200` response that confirms login succeeds.
- Reuse the same session ID across logout and re-login (same bug, different direction).

## Edge cases / when the rule does NOT apply

- **Stateless JWT sessions (no server-side session store):** there is no session record to regenerate. The equivalent protection is that the access token is short-lived and the refresh token is issued fresh at login (which all managed providers do). Ensure the pre-login state (e.g., anonymous cart) is transferred at the application layer, not by reusing a token.
- **Anonymous / guest sessions promoted to authenticated:** session fixation is the specific risk here — this is the highest-priority case for regeneration. Always regenerate when promoting a guest session to an authenticated one.

## See also

- [`../agents/auth-implementation-engineer.md`](../agents/auth-implementation-engineer.md) — implements the session middleware where this control lives
- [`./revoke-tokens-on-logout.md`](./revoke-tokens-on-logout.md) — the logout-direction complement: also invalidate the session at the server on logout

## Provenance

Codifies the OWASP Session Management Cheat Sheet requirement for session ID regeneration on privilege level change. Session fixation is OWASP Top 10 (A07:2021 Identification and Authentication Failures) and a recurring finding in penetration tests of custom session implementations.

---

_Last reviewed: 2026-06-05 by `claude`_
