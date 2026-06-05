# Validate CORS origins explicitly — never use wildcard with credentials

**Status:** Absolute rule
**Domain:** API security / CORS
**Applies to:** `api-engineering`

---

## Why this exists

`Access-Control-Allow-Origin: *` with `Access-Control-Allow-Credentials: true` is rejected by every browser — but attempting to combine them signals a misconfigured CORS policy that may have partial protections in place. More broadly, a wildcard `*` on an API that handles user data allows any origin to make cross-origin requests with ambient credentials (cookies, browser-stored tokens in some configurations). CORS is a defense layer; it requires an explicit allowlist of origins you have decided to trust.

## How to apply

```typescript
import cors from 'cors';

const ALLOWED_ORIGINS = new Set([
  'https://app.example.com',
  'https://admin.example.com',
  // Dev only — gated by environment
  ...(process.env.NODE_ENV === 'development' ? ['http://localhost:3000'] : []),
]);

app.use(cors({
  origin: (origin, callback) => {
    // Allow requests with no origin (mobile apps, curl, Postman)
    if (!origin) return callback(null, true);
    if (ALLOWED_ORIGINS.has(origin)) return callback(null, true);
    callback(new Error(`CORS: origin ${origin} not allowed`));
  },
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization'],
}));
```

**Do:**
- Maintain an explicit allowlist of trusted origins, loaded from configuration.
- Set `credentials: true` only when your API uses cookies or `Authorization` headers with CORS requests.
- Return the specific `Origin` value in `Access-Control-Allow-Origin` (not `*`) when credentials are involved.
- Validate the `Origin` header server-side; do not rely on the browser's preflight alone.

**Don't:**
- Combine `Access-Control-Allow-Origin: *` with `Access-Control-Allow-Credentials: true`.
- Reflect the caller's `Origin` header back unconditionally without an allowlist check.
- Use regex matching like `*.example.com` without anchoring — `evil-example.com` would match.
- Leave the CORS config as `app.use(cors())` (permissive default) in production.

## Edge cases / when the rule does NOT apply

A public read-only API (e.g., a public maps or data API with no user identity) that genuinely serves any origin and uses no credentials may legitimately use `Access-Control-Allow-Origin: *`. Still verify that no credential-carrying request path is reachable under the wildcard policy.

## See also

- [`../agents/api-security-engineer.md`](../agents/api-security-engineer.md) — owns CORS policy and security misconfiguration. Escalate every verdict.
- [`./secure-validate-tokens-and-scopes-server-side.md`](./secure-validate-tokens-and-scopes-server-side.md) — CORS is a browser control; token validation is the server-side control; both are required.

## Provenance

OWASP API Security Top 10 (2023) — API8 Security Misconfiguration; also caught by the plugin's `check-api-anti-patterns.sh` hook (§4a). Codifies `api-security-engineer`'s CORS anti-pattern from CLAUDE.md §4.

---

_Last reviewed: 2026-06-05 by `claude`_
