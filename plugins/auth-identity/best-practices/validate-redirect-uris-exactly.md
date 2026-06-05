# Validate OAuth Redirect URIs with Exact-Match Allowlisting

**Status:** Absolute rule
**Domain:** Auth & Identity — OAuth security
**Applies to:** `auth-identity`

---

## Why this exists

The OAuth `redirect_uri` is the destination for the authorization code after the user authenticates. If the authorization server accepts a `redirect_uri` that differs from the registered one — whether through a substring match, prefix match, or open redirect — an attacker can redirect the authorization code to a server they control and exchange it for tokens. This is one of the most reliably exploited OAuth vulnerabilities in the wild. The fix is exact-match allowlisting: the `redirect_uri` in the authorization request must be character-for-character identical to a URI registered in the OAuth client configuration. No wildcards, no path-prefix matching, no pattern-matching on scheme or domain only.

## How to apply

**Provider-side (Google Cloud Console, Supabase Auth, Clerk):**

Register every redirect URI as an exact string. Do not register domain-level wildcards (`https://*.example.com`). If you need to support multiple environments, register each explicitly:

```
https://app.example.com/auth/callback        ← production
https://staging.example.com/auth/callback    ← staging
http://localhost:3000/auth/callback          ← local dev
```

**Application-side validation (custom or Supabase Auth callback route):**

```typescript
const ALLOWED_REDIRECT_URIS = new Set([
  "https://app.example.com/auth/callback",
  "https://staging.example.com/auth/callback",
  process.env.NODE_ENV === "development"
    ? "http://localhost:3000/auth/callback"
    : null,
].filter(Boolean) as string[]);

export async function GET(req: Request) {
  const url = new URL(req.url);
  const redirectUri = url.searchParams.get("redirect_uri");

  if (!redirectUri || !ALLOWED_REDIRECT_URIS.has(redirectUri)) {
    return Response.json({ error: "Invalid redirect_uri" }, { status: 400 });
  }
  // proceed with OAuth exchange
}
```

**Key validation rules:**
- Compare the full URI string: scheme + host + path + (no query string or fragment).
- Reject any `redirect_uri` not present in the explicit allowlist — return `400 Bad Request`.
- Never allow `javascript:`, `data:`, or other non-`https:` schemes (except `http://localhost` in dev).
- Log rejected redirect URIs — they are a signal for active probing.

**Do:**
- Register the redirect URI in both the provider's dashboard **and** validate it in your application callback handler.
- Keep the allowlist in an environment variable or config, not hardcoded in source, so it can be updated without a deploy.
- Audit the registered redirect URIs when rotating domains, deprecating environments, or adding new deployment targets.

**Don't:**
- Register `https://example.com/*` or any wildcard form.
- Accept a `redirect_uri` that is a URL parameter in a different URL parameter (open redirect via indirection).
- Trust the `redirect_uri` value from the request body when the authorization server should be enforcing exact match — defense-in-depth: validate in both places.

## Edge cases / when the rule does NOT apply

- **`urn:ietf:wg:oauth:2.0:oob`:** the out-of-band URI used in some device flows that display the code to the user. This is a specific, non-URL redirect URI type defined in the OAuth spec. The exact-match rule still applies: the authorization server must recognize this specific string.
- **Supabase Auth with `@supabase/ssr`:** Supabase manages the OAuth callback URI internally. The `NEXT_PUBLIC_SUPABASE_URL` includes the base for redirect URIs; verify the registered Site URL and Additional Redirect URLs in the Supabase dashboard match your deployment URLs exactly.

## See also

- [`../agents/auth-architect.md`](../agents/auth-architect.md) — designs the OAuth flow and specifies the allowed redirect URI set
- [`../agents/auth-implementation-engineer.md`](../agents/auth-implementation-engineer.md) — registers URIs and implements callback validation
- [`../templates/auth-architecture-decision-record.md`](../templates/auth-architecture-decision-record.md) — document the registered URIs and rotation process

## Provenance

Codifies OAuth 2.0 Security Best Current Practice (RFC 9700) §4.1 and OAuth 2.0 for Browser-Based Apps (RFC 9449) redirect URI exact-match requirement. Redirect URI manipulation is listed in the OWASP OAuth Cheat Sheet as a critical misconfiguration category.

---

_Last reviewed: 2026-06-05 by `claude`_
