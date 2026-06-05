# The PKCE Code Verifier Is One-Use-Only and Must Be Stored Securely in the Client

**Status:** Absolute rule
**Domain:** Auth & Identity — OAuth / PKCE implementation
**Applies to:** `auth-identity`

---

## Why this exists

PKCE (Proof Key for Code Exchange) defends the authorization code flow against authorization-code injection attacks. It works by generating a random `code_verifier` on the client before redirecting to the authorization server, hashing it as the `code_challenge`, and then presenting the verifier when exchanging the code for tokens. Two implementation errors destroy this protection: (1) reusing the same verifier across multiple authorization requests (the verifier loses its per-request uniqueness, and an intercepted code can be replayed), and (2) storing the verifier in an XSS-accessible location (e.g., localStorage) — an attacker who reads it can complete the token exchange themselves.

## How to apply

**Correct PKCE implementation:**

```javascript
// 1. Generate a fresh code_verifier for EVERY authorization request
function generateCodeVerifier() {
  const array = new Uint8Array(32);
  crypto.getRandomValues(array);
  return btoa(String.fromCharCode(...array))
    .replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
}

// 2. Derive the code_challenge
async function generateCodeChallenge(verifier) {
  const data = new TextEncoder().encode(verifier);
  const digest = await crypto.subtle.digest('SHA-256', data);
  return btoa(String.fromCharCode(...new Uint8Array(digest)))
    .replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
}

// 3. Store the verifier ONLY in sessionStorage (not localStorage), or pass through a
//    server-side session if a server is in the loop (preferred)
sessionStorage.setItem('pkce_verifier', codeVerifier);

// 4. After the authorization code is received:
const verifier = sessionStorage.getItem('pkce_verifier');
sessionStorage.removeItem('pkce_verifier');  // Delete immediately after use
// Exchange code + verifier at the token endpoint
```

**Supabase note:** Supabase Auth manages the PKCE flow (verifier generation, storage, and exchange) automatically via `signInWithOAuth()` when `flowType: 'pkce'` is set in the `createClient` config. Do not reimplement PKCE manually on top of Supabase Auth.

**Security rules:**
- Generate a new `code_verifier` (via `crypto.getRandomValues`) for every authorization redirect.
- Use `code_challenge_method=S256` (SHA-256 hash) — never `plain`.
- Delete the verifier from storage immediately after it is used in the token exchange.
- Prefer storing the verifier in a server-side session (via BFF/SSR) over `sessionStorage` when a server is available.

**Do:**
- Verify that the authorization library you're using (Supabase Auth, `@auth/sveltekit`, `openid-client`) handles PKCE automatically before implementing it manually.
- Log a security event if a PKCE exchange fails with `invalid_grant` — it may indicate a code-injection attempt.

**Don't:**
- Store the `code_verifier` in `localStorage` (persists across sessions, XSS-exfiltratable).
- Reuse a cached `code_verifier` for multiple authorization requests.
- Use `code_challenge_method=plain` — it provides no protection against an attacker who can observe the authorization request.

## Edge cases / when the rule does NOT apply

- **Server-side confidential clients using Authorization Code + PKCE**: the verifier is generated and held server-side (in the session or BFF); the client-side storage concern does not apply. PKCE is still required (OAuth 2.1 mandates it for confidential clients too).

## See also

- [`../agents/auth-implementation-engineer.md`](../agents/auth-implementation-engineer.md) — implements the OAuth callback and PKCE token exchange
- [`./use-authorization-code-pkce-never-implicit.md`](./use-authorization-code-pkce-never-implicit.md) — the parent rule requiring PKCE; this doc covers the implementation discipline

## Provenance

Codifies PKCE implementation correctness from `oauth-oidc-and-google-sso.md`. PKCE specification: RFC 7636. OAuth 2.1 mandates PKCE for all client types (IETF OAuth WG, 2025 `[verify-at-build — OAuth 2.1 draft-to-RFC status]`). _Last reviewed: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_
