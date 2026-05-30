# Delta for what changed — track changes, don't re-pull the collection

**Status:** Pattern — for "what changed since last time," use a delta query or change notification, not a periodic full read.

**Domain:** Web API / change tracking

**Applies to:** `microsoft-graph`

---

## Why this exists

The most common cause of self-inflicted throttling is a cron job that re-reads an entire collection every hour to diff it client-side. Microsoft Learn names this anti-pattern directly: "continuously polling a resource ... [is] more likely to lead to applications being throttled." Delta queries solve it — Graph hands you a `@odata.deltaLink` that, on the next call, returns **only** what was added, updated, or removed since you last asked. You sync the full set once, then ride incremental rounds forever, paying for changes instead of the whole tenant.

## How to apply

Initial round: `GET /resource/delta`, drain every `@odata.nextLink` (more baseline pages), and stop when you receive a `@odata.deltaLink`. **Persist that deltaLink.** Next round: GET the saved deltaLink; it returns the changes plus a new deltaLink.

```http
GET https://graph.microsoft.com/v1.0/users/delta?$select=displayName,mail
# ... follow @odata.nextLink through the baseline ...
# final page: "@odata.deltaLink":"https://graph.microsoft.com/v1.0/users/delta?$deltatoken=..."

# later, to get only changes:
GET https://graph.microsoft.com/v1.0/users/delta?$deltatoken={saved token}
```

```csharp
// Removed objects arrive with an @removed annotation, not as absence:
// { "id": "...", "@removed": { "reason": "changed" } }  // restorable from deletedItems
// { "id": "...", "@removed": { "reason": "deleted" } }  // permanent
```

**Do:**
- Specify `$select` (and any query params) **only in the initial** delta request — the token encodes them; don't repeat them on subsequent calls. The `id` is always returned.
- Persist the entire `@odata.deltaLink`/`@odata.nextLink` URL verbatim; treat the token as opaque.
- Handle `@removed` for deletes and the `propertyName@delta` annotations (e.g. `members@delta`) for relationship changes; merge defensively — an item can appear more than once.

**Don't:**
- Re-read the whole collection on a timer to find changes.
- Assume order — delta makes no `$orderby` guarantee; the same item can appear anywhere across pages.
- Forget to handle replication delay — a just-created object may need a retry of the deltaLink to surface.

## Edge cases / when the rule does NOT apply

If you only need future changes (not the current baseline), skip the initial sync with `$deltatoken=latest` (`token=latest` for OneDrive/SharePoint) to get a deltaLink immediately. For `user`/`group`, `$expand` and `$top` aren't supported on delta, and `$filter` is limited (scope by object `id` only, ≤50 IDs). When you need *push* rather than *pull* — react within seconds, or avoid any polling — use a **change-notification subscription** instead (escalate the subscription/decryption-key design to `graph-workloads-engineer` and `ravenclaude-core/security-reviewer`). Not every resource supports delta `[verify-at-build]`.

## See also

- [`./api-honor-throttling-and-retry-after.md`](./api-honor-throttling-and-retry-after.md) — polling is the throttling you brought on yourself
- [`./api-page-to-exhaustion.md`](./api-page-to-exhaustion.md) — the baseline round still pages, but ends on deltaLink
- [`../knowledge/api-query-decision-trees.md`](../knowledge/api-query-decision-trees.md) — query-vs-delta-vs-notification tree
- [`../agents/graph-api-engineer.md`](../agents/graph-api-engineer.md) — owns change tracking
- [Use delta query to track changes in Microsoft Graph data](https://learn.microsoft.com/graph/delta-query-overview) — authoritative

## Provenance

From the Microsoft Learn "delta query overview," "user: delta," and "group: delta" pages (retrieved 2026-05-30 via Microsoft Learn MCP), codifying team house opinion #6. The set of delta-supported resources and the per-resource query-parameter restrictions are version-sensitive — `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
