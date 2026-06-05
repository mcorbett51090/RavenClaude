# Implement content negotiation via the Accept header

**Status:** Pattern
**Domain:** HTTP build craft
**Applies to:** `api-engineering`

---

## Why this exists

Hard-coding a response format (`/users.json`, `/users.csv`) in the URL conflates the resource identity with its representation — a REST violation and a maintenance burden. The HTTP `Accept` header is the standard mechanism for a client to request a preferred representation (`application/json`, `text/csv`, `application/problem+json`). Implementing content negotiation correctly means one endpoint serves multiple consumers (browser, API client, BI export) without URL proliferation, and it makes `application/problem+json` error responses work without special-casing.

## How to apply

```typescript
// Express example
app.get('/orders', (req, res) => {
  const accept = req.headers['accept'] ?? 'application/json';

  const orders = orderService.list();

  if (accept.includes('text/csv')) {
    res.setHeader('Content-Type', 'text/csv');
    return res.send(toCsv(orders));
  }

  if (accept.includes('application/json') || accept.includes('*/*')) {
    return res.json(orders);
  }

  // 406 Not Acceptable if we can't satisfy the Accept header
  return res.status(406).json({
    type: 'https://api.example.com/errors/not-acceptable',
    title: 'Not Acceptable',
    detail: `Supported types: application/json, text/csv`,
  });
});
```

**Do:**
- Return `406 Not Acceptable` when you cannot satisfy the `Accept` header.
- Set `Content-Type` explicitly in every response to match what you actually sent.
- Treat `Accept: */*` (the default) as equivalent to your primary format (JSON).
- Use `Accept` negotiation for the error format too — some clients want `application/problem+json` explicitly.

**Don't:**
- Put the format in the URL (`/orders.json`, `/orders.csv`) — that's not how HTTP works.
- Silently return a format the client didn't request.
- Ignore the `Accept` header entirely and always return JSON without checking.

## Edge cases / when the rule does NOT apply

GraphQL APIs use `application/json` (or `application/graphql-response+json`) exclusively — content negotiation is not applicable at the operation level. Binary-only APIs (e.g., a file download endpoint) that produce only one format do not need to negotiate.

## See also

- [`../agents/api-implementation-engineer.md`](../agents/api-implementation-engineer.md) — owns HTTP semantics and build craft.
- [`./build-use-http-status-codes-and-methods-correctly.md`](./build-use-http-status-codes-and-methods-correctly.md) — the `406` response is part of correct HTTP status usage.

## Provenance

RFC 9110 §12 (HTTP Semantics — Content Negotiation). Codifies `api-implementation-engineer`'s HTTP-semantics discipline from this plugin's CLAUDE.md §3.

---

_Last reviewed: 2026-06-05 by `claude`_
