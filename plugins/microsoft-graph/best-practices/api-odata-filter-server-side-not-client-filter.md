# Filter server-side with $filter — never page the full collection client-side to find a subset

**Status:** Absolute rule
**Domain:** Microsoft Graph / API query patterns
**Applies to:** `microsoft-graph`

---

## Why this exists

`GET /users` with no `$filter` returns every user in the tenant, paged. A developer who fetches all pages and then filters the resulting array client-side (`array.filter(u => u.department === 'Engineering')`) has transferred the entire user corpus over the wire, held it in memory, and spent hundreds of API calls — when a single `$filter=department eq 'Engineering'` call on the server would return only the matching users. This is the most common Graph over-fetch pattern and it causes self-inflicted throttling on large tenants. Server-side `$filter` is the rule; client-side filtering of a server-filterable attribute is a defect.

## How to apply

```http
# Wrong — fetches every user, filters in code
GET /v1.0/users
# ... then in code: users.filter(u => u.department === 'Engineering')

# Correct — server-side filter, only returns matching users
GET /v1.0/users?$filter=department eq 'Engineering'&$select=id,displayName,mail
```

For indexed vs non-indexed properties:
- `id`, `userPrincipalName`, `mail`, `mailNickname`, `proxyAddresses` — directly filterable without advanced-query headers.
- `displayName`, `department`, `jobTitle` — filterable with advanced-query headers:
  ```http
  GET /v1.0/users?$filter=department eq 'Engineering'&$count=true
  ConsistencyLevel: eventual
  ```

**Do:**
- Always combine `$filter` with `$select` — filtering narrows the row set, `$select` narrows the columns.
- Use `startsWith(displayName, 'Smith')` for prefix searches on string properties (advanced query required).
- Test `$filter` expressions against a small dataset first — a malformed OData expression returns `400` with a descriptive message.

**Don't:**
- Use `$search` when `$filter` can express the predicate — `$search` does full-text and returns approximate results; `$filter` is exact.
- Fetch `/users` with no filter to "check if a user exists" — use `$filter=userPrincipalName eq 'user@domain.com'` and check the `value` array length.
- Combine `$filter` and `$search` on the same request — they are incompatible on most resources.

## Edge cases / when the rule does NOT apply

When the filter attribute is not indexable or filterable (some extension attributes, some beta properties), client-side filtering after a narrowed server-side `$select` query may be unavoidable. Document the limitation and file a feature request.

## See also

- [`../agents/graph-api-engineer.md`](../agents/graph-api-engineer.md) — owns OData query shaping
- [`./api-advanced-query-consistencylevel.md`](./api-advanced-query-consistencylevel.md) — the required headers for advanced `$filter` expressions

## Provenance

Codifies CLAUDE.md §3 #3 ("select what you need; never `GET /users` bare; `$filter`/`$search` server-side; never page the whole tenant to filter client-side"); Microsoft Graph OData query documentation.

---

_Last reviewed: 2026-06-05 by `claude`_
