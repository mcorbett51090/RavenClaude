# Limit $expand depth and property count — nested expands degrade performance and hit 400 limits

**Status:** Primary diagnostic
**Domain:** Microsoft Graph / API query patterns
**Applies to:** `microsoft-graph`

---

## Why this exists

`$expand` lets you retrieve a related resource in the same Graph call instead of a follow-up request. Developers over-use it in two ways: deeply nesting expansions (e.g., `$expand=members($expand=manager)`) which Graph limits to a single level on most resources, and expanding large collections without `$select` on the expanded entity (e.g., expanding all `members` of a large group retrieves the full profile of every member). The result is either a `400 Bad Request` for unsupported expansion depth or a multi-megabyte response payload for a query that needed five fields. `$expand` without `$select` on the expanded entity is a silent performance hazard.

## How to apply

Always chain `$select` inside `$expand`:

```http
# Wrong — expands members with all properties, potentially megabytes
GET /v1.0/groups/{id}?$expand=members

# Correct — expands members and selects only the needed fields
GET /v1.0/groups/{id}?$select=id,displayName&$expand=members($select=id,displayName,mail)
```

Rules:
- Maximum **one level** of `$expand` on directory objects (user, group, etc.) — `$expand=members($expand=manager)` throws `400` on most resources `[verify-at-build]`.
- `$expand=members` is limited to **100 members by default** — for groups with > 100 members, use `GET /groups/{id}/members` with paging instead.
- Never use `$expand=attachments` on a mail collection list — expand attachments only on an individually identified message.

**Do:**
- Always add `$select` to the expanded entity: `$expand=members($select=id,displayName)`.
- Prefer separate calls for large-membership groups over a single `$expand` — paging the `/members` endpoint is more reliable at scale.
- Test expansion limits in Graph Explorer before coding — the supported depth and top-N vary by resource.

**Don't:**
- Use `$expand` when you need all items in a large collection — `$expand=members` silently truncates at 100 without a `nextLink`.
- Chain two levels of `$expand` (e.g., `$expand=members($expand=memberOf)`) — this typically returns `400 Unsupported query`.
- Use `$expand=attendees` on a calendar event in a list view — expand only on individually fetched events.

## Edge cases / when the rule does NOT apply

Some Graph resources (e.g., `/sites` and SharePoint-related APIs) support deeper expansion — verify per-resource in the Graph documentation `[verify-at-build]` before assuming the single-level limit applies universally.

## See also

- [`../agents/graph-api-engineer.md`](../agents/graph-api-engineer.md) — owns OData query design
- [`./api-select-only-what-you-need.md`](./api-select-only-what-you-need.md) — the `$select` discipline that makes `$expand` safe to use

## Provenance

Codifies CLAUDE.md §3 #3 ("select what you need; `$filter`/`$search` server-side; never over-fetch") applied to `$expand`; Microsoft Graph OData expansion documentation.

---

_Last reviewed: 2026-06-05 by `claude`_
