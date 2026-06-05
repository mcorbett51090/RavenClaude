# Cookie Sessions Require CSRF Defense

**Status:** Absolute rule
**Domain:** Auth & Identity — Session security
**Applies to:** `auth-identity`

---

## Why this exists

A cookie-based session is automatically sent by the browser on every matching-origin request — including requests triggered by a malicious third-party page. This is the CSRF (Cross-Site Request Forgery) attack surface: an attacker's page can cause the victim's browser to fire a state-changing request to the target site, authenticated by the session cookie, without the user's knowledge. `SameSite=Lax` blocks most cross-site cookie sends (all but top-level navigations), but does not prevent all CSRF attacks. For high-value state-changing operations — money transfers, email changes, password resets, admin actions — an additional anti-CSRF token provides defense-in-depth. The plugin house opinion #4 states this explicitly.

## How to apply

**Two-layer CSRF defense:**

**Layer 1 — SameSite cookie attribute (always):**

```http
Set-Cookie: session=...; HttpOnly; Secure; SameSite=Lax; Path=/
```

- `SameSite=Lax`: cookies are sent on same-site requests and on top-level navigations from other sites (clicking a link). Cookies are **not** sent on cross-site subresource requests (XHR, fetch from another origin, form POST from another site).
- `SameSite=Strict`: cookies are never sent on any cross-site request, including top-level navigation. Stronger protection but breaks "come back to your account" links in emails.

**Layer 2 — Anti-CSRF token on state-changing requests:**

```
1. On login / session creation:
   - Generate a cryptographically random token (e.g., 32 bytes, URL-safe base64).
   - Store it server-side, associated with the session.
   - Send it to the browser as a non-HttpOnly cookie (so JS can read it) OR as a response body value (stored in memory or a non-HttpOnly cookie).

2. On state-changing requests (POST/PUT/PATCH/DELETE):
   - Client includes the token in a custom header (X-CSRF-Token) or request body.
   - Server verifies: the value in the header/body matches the value stored in the session.
   - Reject with 403 if they do not match.
```

**Double Submit Cookie pattern (simpler, same protection):**

```javascript
// Client: read the CSRF cookie value and send it in the header
const csrfToken = document.cookie.match(/csrf_token=([^;]+)/)?.[1];
fetch('/api/transfer', {
  method: 'POST',
  headers: { 'X-CSRF-Token': csrfToken, 'Content-Type': 'application/json' },
  body: JSON.stringify({ amount: 100 })
});
```

**Do:**
- Apply CSRF defense to all state-changing endpoints (POST/PUT/PATCH/DELETE); read-only GET endpoints are not CSRF attack surfaces.
- Use a `SameSite=Strict` cookie for the CSRF token itself so it is not sent cross-site.
- Rotate the CSRF token on each session creation and on privilege escalation.

**Don't:**
- Skip the anti-CSRF token because `SameSite=Lax` is set — `Lax` still allows top-level POST navigations from form submits on other origins in some older browsers.
- Accept the CSRF token in a GET parameter — GET requests should not be state-changing, and URL parameters are logged.
- Use the session ID as the CSRF token — they are different things with different threat models.

## Edge cases / when the rule does NOT apply

- **Pure API endpoints authenticated only by Bearer token in `Authorization` header**: the browser does not automatically send custom headers cross-site, so CSRF is not a risk for header-authenticated APIs. CSRF defense is required only for cookie-authenticated sessions.
- **Stateless JWT sessions in memory** (no cookie at all): CSRF is not a risk; the CSRF token would be redundant.

## See also

- [`../agents/auth-implementation-engineer.md`](../agents/auth-implementation-engineer.md) — implements the CSRF defense in the session middleware
- [`./never-store-tokens-in-localstorage.md`](./never-store-tokens-in-localstorage.md) — the companion rule on where refresh tokens live (the HttpOnly cookie that needs CSRF defense)

## Provenance

Codifies house opinion #4 ("Cookie sessions imply CSRF defense") from `CLAUDE.md` §3. CSRF prevention from OWASP Cross-Site Request Forgery Prevention Cheat Sheet (verified 2026-06-05). _Last reviewed: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_
