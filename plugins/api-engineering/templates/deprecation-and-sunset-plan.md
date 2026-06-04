# Deprecation & sunset plan — `<API / version>`

> Copy and fill in before retiring an API version or endpoint. A silent retirement is a
> broken promise (and a shadow-API security risk — OWASP API9). See
> [`../best-practices/operate-deprecate-with-sunset-headers.md`](../best-practices/operate-deprecate-with-sunset-headers.md).

## What is being deprecated

- **Surface:** `<e.g. /v1/* — entire v1>` or `<e.g. GET /v2/orders?legacyShape=true>`
- **Replacement:** `<e.g. /v2 — migration guide link>`
- **Reason:** `<breaking change / consolidation / security>`
- **Why it's breaking:** `<the specific incompatibility — removed field / changed semantics / etc.>`

## Timeline (dated)

| Milestone | Date | Action |
|---|---|---|
| Announce | `<YYYY-MM-DD>` | Migration guide published; known consumers emailed; changelog entry |
| Headers live | `<YYYY-MM-DD>` | `Deprecation: true` + `Sunset` + `Link rel="deprecation"` on every deprecated response |
| Reminder | `<YYYY-MM-DD>` | Chase remaining consumers still on the old surface (per traffic data) |
| Brownout (optional) | `<YYYY-MM-DD>` | Brief scheduled outages of the old surface to surface hidden dependencies |
| **Sunset** | `<YYYY-MM-DD>` | Old surface returns `410 Gone`; only if traffic has drained or sign-off obtained |

## In-band signals (the headers)

```http
Deprecation: true
Sunset: <Sat, 30 Nov 2026 23:59:59 GMT>          # RFC 8594
Link: <https://api.example.com/docs/migrate>; rel="deprecation"
Warning: 299 - "This version is deprecated; migrate before <date>"
```

## Drain monitoring

- [ ] Traffic to the deprecated surface is tracked **per consumer** (key/client id).
- [ ] A dashboard shows the drain curve toward the sunset date.
- [ ] **Do not sunset** while material traffic remains without explicit owner sign-off (record it here).

## Consumer comms

- **Channels:** `<email list / dev portal banner / changelog / status page>`
- **Migration guide:** `<link>` — includes a field-by-field mapping and code examples.
- **Support contact:** `<who handles migration questions>`

## Sign-off

- **Owner:** `<name>` · **Security (API9 inventory):** `<routed to security-reviewer? y/n>` · **Approved:** `<date>`
