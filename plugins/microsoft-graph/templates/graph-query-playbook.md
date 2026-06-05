> Use this template to design and document a set of Microsoft Graph queries for a new integration — OData shapes, paging strategy, permissions required, and the test-case checklist.

# Graph Query Playbook: [Integration Name]

## Metadata

| Field | Value |
|---|---|
| Integration name | [e.g., User Directory Sync, Meeting Room Finder] |
| App registration | [App name + client ID] |
| Graph version | [v1.0 — use /beta only with explicit justification] |
| Owner | [Name / Team] |
| Last reviewed | [YYYY-MM-DD] |

---

## Query inventory

For each distinct Graph query in this integration:

---

### Query [1]: [Short name, e.g., "List active users"]

**Business purpose:** [What this query provides]

**Endpoint:**
```http
GET https://graph.microsoft.com/v1.0/[resource]
  ?$select=[field1,field2]
  &$filter=[condition]
  &$orderby=[field asc|desc]
  &$top=[N]
```

**Headers required:**
- `Authorization: Bearer {token}`
- `ConsistencyLevel: eventual` — [ ] Required (for $search/$count) / [ ] Not required

**Permissions:**
- Delegated: [Permission name] or `—`
- Application: [Permission name] or `—`

**Paging strategy:**
- [ ] Single page — `$top=[N]`, result fits one page
- [ ] Follow `@odata.nextLink` to exhaustion (estimated [X] pages at [N]/page)
- [ ] Delta query — store `@odata.deltaLink` for incremental sync

**Sample response fields used:**

| Field | Type | Purpose |
|---|---|---|
| `id` | string | Primary key for upsert |
| `displayName` | string | Display in UI |
| `[field]` | [type] | [use] |

**Error handling:**
- `400` (advanced query missing header): [Add ConsistencyLevel: eventual]
- `429` (throttled): [Honour Retry-After; SDK retry handler or custom backoff]
- `404` (not found): [Log and skip; resource may have been deleted]

---

### Query [2]: [Short name]

*(Copy the Query 1 block above for each additional query)*

---

## Batch opportunities

List queries that can be combined into a `$batch` call (max 20 per batch, all same Graph version):

| Batch group | Queries included | Dependency order? |
|---|---|---|
| Startup | [Query 1, Query 2] | [ ] Independent |
| Per-user sync | [Query 3, Query 4] | [ ] Query 4 depends on Query 3 |

---

## Delta / change-tracking strategy

| Resource | Strategy | State stored | Renewal needed? |
|---|---|---|---|
| [Users] | [Delta query] | `@odata.deltaLink` in [DB table] | [ ] N/A |
| [Messages] | [Change notification subscription] | Subscription ID + expiry | [ ] Yes — renew [X] hours before expiry |

---

## Test-case checklist

- [ ] Happy path: query returns expected fields for a known resource.
- [ ] Empty result: query for non-existent filter returns `{"value": []}`, not an error.
- [ ] Paging: query with `$top=1` on a multi-record resource returns `@odata.nextLink`; follow it.
- [ ] Throttle: simulate 429 response; verify Retry-After is honoured and the call retries.
- [ ] Permission: run as a non-admin user; confirm delegated scope is sufficient (admin account bypasses some checks).
- [ ] Advanced query: if using `$search` or `$count`, test without `ConsistencyLevel` header to confirm expected 400.

---

## Change log

| Date | Change | Author |
|---|---|---|
| [YYYY-MM-DD] | [Initial query design] | [Name] |
| | | |
