# Never accept API keys in query strings

**Status:** Absolute rule
**Domain:** API security
**Applies to:** `api-engineering`

---

## Why this exists

An API key in a query string appears verbatim in server access logs, browser history, referrer headers, and CDN/proxy logs — all places you do not control. One compromised log file exposes every caller's credentials. The `Authorization` header is the correct place for bearer tokens; request headers are not logged by default and are not included in `Referer` redirects. An OpenAPI `securityScheme` with `in: query` is a flag the automated hook catches for this exact reason.

## How to apply

```yaml
# Bad — OpenAPI spec with API key in query
components:
  securitySchemes:
    ApiKeyQuery:
      type: apiKey
      in: query         # This is the anti-pattern
      name: api_key

# Good — API key in a header
components:
  securitySchemes:
    ApiKeyHeader:
      type: apiKey
      in: header
      name: X-API-Key

# Better — use Bearer token (OAuth2 / JWT)
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

Server-side: reject any request that presents credentials in the query string, even if your primary scheme is correct.

```typescript
// Middleware: refuse credentials in query params
app.use((req, _res, next) => {
  if (req.query['api_key'] || req.query['token'] || req.query['access_token']) {
    throw new BadRequestError('Credentials must not be sent in the query string');
  }
  next();
});
```

**Do:**
- Accept API keys only in the `Authorization: Bearer <token>` or `X-API-Key: <key>` header.
- Document the correct header-based scheme in your OpenAPI spec.
- Audit existing integrations before removing query-string support and provide a migration window.

**Don't:**
- Generate or document a query-string API key scheme in the OpenAPI spec.
- Use `?token=`, `?api_key=`, `?access_token=` as the primary or fallback authentication path.
- Accept both paths simultaneously ("for convenience") — this permanently exposes the log-leak surface.

## Edge cases / when the rule does NOT apply

Webhook signature verification (verifying an HMAC on the query string itself) is not the same as passing an API key — the signature is a validation, not a credential. Some legacy OAuth 2.0 flows expose `access_token` in URI fragments (not query strings) for implicit grant — this is a separate (deprecated) pattern.

## See also

- [`../agents/api-security-engineer.md`](../agents/api-security-engineer.md) — owns API authentication posture; escalate every verdict.
- [`./secure-validate-tokens-and-scopes-server-side.md`](./secure-validate-tokens-and-scopes-server-side.md) — token validation requirements for all bearer token schemes.

## Provenance

OWASP API Security Top 10 (2023) — API8 Security Misconfiguration; also enforced by the plugin's `check-api-anti-patterns.sh` hook (§4a). Codifies `api-security-engineer`'s anti-pattern list from CLAUDE.md §4.

---

_Last reviewed: 2026-06-05 by `claude`_
