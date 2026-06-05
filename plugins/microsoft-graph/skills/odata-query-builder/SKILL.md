---
name: odata-query-builder
description: "Playbook for constructing well-shaped Microsoft Graph OData queries: $select, $filter, $expand, $search, $count, $orderby, $top, $skip, the ConsistencyLevel header for advanced queries, and the common 400-error patterns. Owned by graph-api-engineer."
---

# OData Query Builder

## When to invoke

- Writing a new Microsoft Graph GET request with filter/expand/search requirements.
- Receiving a `400 Bad Request` on a `$search` or `$count` query.
- Over-fetching (no `$select`) or seeing slow queries from missing server-side filters.
- Combining `$filter` with `$search` or `$count`.

## The baseline rule

**Never issue a bare collection GET.** Always apply `$select` with the exact fields needed. Graph resources carry dozens of properties; fetching all of them for large directories produces oversized payloads and hits throttling faster.

```http
# Bad — fetches all user properties
GET https://graph.microsoft.com/v1.0/users

# Good — fetches only what the app needs
GET https://graph.microsoft.com/v1.0/users?$select=id,displayName,mail,userPrincipalName
```

## OData operator reference

| Operator | Syntax | Notes |
|---|---|---|
| `$select` | `$select=field1,field2` | Required on every collection call |
| `$filter` | `$filter=startsWith(displayName,'Alex')` | Server-side; supported operators vary by resource — check docs |
| `$search` | `$search="displayName:Alex"` | Full-text; requires `ConsistencyLevel: eventual` header + `$count=true` |
| `$expand` | `$expand=manager($select=id,displayName)` | Inline-expand related navigation properties; nest `$select` inside |
| `$count` | `$count=true` | Returns total count inline; requires `ConsistencyLevel: eventual` for directory resources |
| `$orderby` | `$orderby=displayName asc` | Not supported on all resources; check before using |
| `$top` | `$top=50` | Max value varies by resource (users: 999); combine with paging |
| `$skip` | `$skip=100` | Token-based paging via `@odata.nextLink` is preferred; `$skip` is expensive on large directories |

## Advanced query: ConsistencyLevel requirement

Queries using `$search`, `$count=true`, `$filter` on non-indexed properties, or `$orderby` on directory resources require **two things** or they return `HTTP 400`:

1. Request header: `ConsistencyLevel: eventual`
2. Query parameter: `$count=true`

```http
GET https://graph.microsoft.com/v1.0/users?$search="displayName:Contoso"&$count=true
ConsistencyLevel: eventual
```

"Eventual" means the result reflects a slightly delayed index (milliseconds to seconds). For most search/filter operations this is acceptable. For security-critical queries (checking group membership before granting access), use a non-eventual call or verify with a direct membership check.

## $filter expression patterns

```http
# String prefix
$filter=startsWith(displayName,'Alex')

# Exact match
$filter=mail eq 'alex@contoso.com'

# In list (Graph v1.0, Entra resources)
$filter=id in ('guid1','guid2','guid3')

# Date comparison (ISO 8601)
$filter=createdDateTime ge 2025-01-01T00:00:00Z

# Combined (AND)
$filter=accountEnabled eq true and department eq 'Engineering'
```

`OR` conditions and `not` are supported on most directory resources but may require `ConsistencyLevel: eventual`. Test with the Graph Explorer before building code.

## $expand — inline related resources

```http
GET https://graph.microsoft.com/v1.0/me/messages?$select=id,subject,from
    &$expand=attachments($select=id,name,size)
    &$top=20
```

Rules:
- Always nest `$select` inside `$expand` to prevent over-fetching the expanded resource.
- `$expand` on `members` of a large group returns up to 20 members inline; page the `/members` endpoint separately for full membership.
- `$expand` counts as additional API calls internally — throttling applies to the expanded resources too.

## Worked example — find all enabled users in Engineering, paginated

```python
import httpx

headers = {"Authorization": f"Bearer {token}", "ConsistencyLevel": "eventual"}
url = (
    "https://graph.microsoft.com/v1.0/users"
    "?$select=id,displayName,mail,department,accountEnabled"
    "&$filter=accountEnabled eq true and department eq 'Engineering'"
    "&$count=true"
    "&$top=100"
)

all_users = []
while url:
    resp = httpx.get(url, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    all_users.extend(data.get("value", []))
    url = data.get("@odata.nextLink")  # None when last page

print(f"Total: {len(all_users)}")
```

## Pitfalls

- `$search` without `ConsistencyLevel: eventual` → always `400 Bad Request`.
- `$orderby` on a property that doesn't support ordering → `400` with a vague message; check the resource's [supported query parameters](https://learn.microsoft.com/en-us/graph/query-parameters) before using.
- Trusting the first page of a collection as "all results" — follow `@odata.nextLink` to exhaustion.
- Using `$skip` for large directory pages — `$skip` is O(n) on directory resources; `@odata.nextLink` is O(1).
- Passing `$count=true` without `ConsistencyLevel: eventual` on directory resources — returns `400`.
