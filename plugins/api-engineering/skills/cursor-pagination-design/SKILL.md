---
name: cursor-pagination-design
description: "Playbook for designing cursor (keyset) pagination on list endpoints: cursor encoding, response envelope, query parameter contract, and the migration path away from offset pagination."
---

# Cursor Pagination Design

## When to Use This Skill

Use whenever you are building or reviewing a list endpoint. Default to cursor (keyset) pagination. Use offset/page only when: the dataset is static, or the consumer requires random-access page-jumping (e.g. a UI with a page-number picker on a dataset guaranteed < 10 000 rows). Document the trade explicitly when you choose offset.

## Why Cursor Beats Offset

| Concern | Offset/Page | Cursor (Keyset) |
|---|---|---|
| Deep-page performance | Full `OFFSET N` scan — degrades O(N) | `WHERE id > cursor` — index seek, O(1) |
| Consistency during mutations | Rows inserted/deleted shift pages → duplicates/skips | Cursor anchored to a row; inserts/deletes after it are invisible |
| Real-time / high-write tables | Unreliable | Stable |
| Random-access (jump to page 42) | Supported | Not supported — use if required |

## Response Envelope

```json
{
  "data": [ { "id": "u_01", "name": "Alice" }, "..." ],
  "pagination": {
    "nextCursor": "eyJpZCI6InVfMTAwIn0",
    "hasMore": true,
    "pageSize": 50
  }
}
```

| Field | Type | Notes |
|---|---|---|
| `data` | array | The page of results. |
| `pagination.nextCursor` | string\|null | Opaque base64-encoded cursor. `null` when no more pages. |
| `pagination.hasMore` | boolean | Convenience flag (derived from `nextCursor != null`). |
| `pagination.pageSize` | integer | Actual count returned (≤ requested `limit`). |

Do not expose `total` by default — a COUNT(*) on large tables is expensive. Provide it as an opt-in (`?includeTotalCount=true`) only when UX demands it.

## Query Parameter Contract

```
GET /users?limit=50&cursor=eyJpZCI6InVfMTAwIn0&sort=createdAt_asc
```

| Parameter | Default | Constraint |
|---|---|---|
| `limit` | 20 | Server enforces max (e.g. 100); reject `> max` with 422 + Problem Details |
| `cursor` | omitted (first page) | Opaque — treat as a black box; validate signature before use |
| `sort` | stable default (e.g. `id_asc`) | Only supported sort expressions; reject unknown with 422 |

## Cursor Encoding

The cursor encodes the **last-seen keyset values** (not a row offset). Common strategies:

1. **Single-key:** `{ "id": "u_100" }` → base64url → URL-safe string.
2. **Composite sort:** `{ "createdAt": "2026-01-15T10:00:00Z", "id": "u_100" }` — include the unique tiebreaker (`id`) to handle duplicate sort-key values.
3. **Signed cursor:** HMAC-sign the JSON payload to prevent cursor manipulation (prevents a client from crafting cursors that bypass authorization scoping).

```python
import base64, json, hmac, hashlib

def encode_cursor(payload: dict, secret: bytes) -> str:
    raw = json.dumps(payload, separators=(",", ":")).encode()
    sig = hmac.new(secret, raw, hashlib.sha256).hexdigest()[:16]
    return base64.urlsafe_b64encode(raw + b"." + sig.encode()).decode().rstrip("=")
```

## SQL Query Pattern

```sql
-- cursor = { "createdAt": "2026-01-15T10:00:00Z", "id": "u_100" }
SELECT * FROM users
WHERE (created_at, id) > (:cursorCreatedAt, :cursorId)
ORDER BY created_at ASC, id ASC
LIMIT :limit + 1;  -- fetch one extra to determine hasMore
```

Fetch `limit + 1` rows. If you get `limit + 1` back, `hasMore = true`; return only `limit` rows and encode the last returned row's keyset as `nextCursor`.

## Pitfalls

- Exposing the cursor as a raw unencoded offset or row ID — reveals internal keys and allows parameter manipulation.
- Using `OFFSET` behind a "cursor" parameter — defeats the purpose; degrades on deep pages.
- Missing the unique tiebreaker in a composite sort — causes duplicate or missing rows when sort-key values collide.
- Accepting any caller-supplied cursor without validation — enables injection / authorization bypass; sign cursors.
- Omitting `limit` enforcement server-side — unbounded queries are a DoS and a cost vector (OWASP API4).
- Not advertising `pageSize` in the response — consumers can't detect partial pages or truncation.

## See Also

- [`../../agents/api-implementation-engineer.md`](../../agents/api-implementation-engineer.md) — owns pagination implementation
- [`../../agents/api-security-engineer.md`](../../agents/api-security-engineer.md) — resource-consumption limits (OWASP API4)
- [`../../CLAUDE.md`](../../CLAUDE.md) — house opinion #5 (cursor pagination by default)
