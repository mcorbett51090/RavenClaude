# Schedule incremental crawls for ongoing freshness — full recrawls only for schema or ACL changes

**Status:** Pattern
**Domain:** Copilot connectors
**Applies to:** `microsoft-365-copilot`

---

## Why this exists

A Copilot connector's **full crawl** re-ingests every item from the source, updating all properties and ACLs. A **incremental crawl** fetches only items changed since the last crawl, using a delta/watermark mechanism. Engineers who configure full recrawls for ongoing freshness consume connector capacity quota at a far higher rate than incremental crawls and can trigger semantic-index throttling on large data sources. The semantic-index latency (time from crawl to Copilot citation) is longer for full crawls because the entire corpus must be re-processed. Incremental crawls are the correct ongoing mechanism; full recrawls are reserved for schema changes, ACL overhauls, or initial indexing.

## How to apply

In the connector registration, set both crawl types:

```json
{
  "searchSettings": {
    "searchResultTemplates": [...],
    "activitySettings": {
      "urlToItemResolvers": [...]
    }
  },
  "activitySettings": {
    "urlToItemResolvers": [...]
  }
}
```

Via Microsoft Graph connector APIs or the admin center connector configuration:
- **Full crawl:** schedule monthly or triggered by schema/ACL change.
- **Incremental crawl:** schedule every 15–60 minutes for near-real-time, or every 24 hours for daily freshness.

Trigger for a manual full recrawl:
- Schema change (new property added, semantic label changed).
- ACL overhaul (new security group, permission model change).
- Source data migration or restructuring.
- First-time indexing.

**Do:**
- Monitor the connector's `crawlStatus` via the Graph API (`GET /external/connections/{id}/items` or the admin center) after a schema change to confirm the full crawl completed successfully before re-enabling incremental.
- Document the full-recrawl trigger conditions in the connector runbook so future operators do not run full recrawls speculatively.
- Set the incremental crawl interval based on the source's change frequency — a document library that changes once a day doesn't need a 15-minute crawl.

**Don't:**
- Schedule daily full recrawls for a connector with > 100,000 items — the connector quota and index latency cost is disproportionate.
- Disable incremental crawls entirely and rely only on full recrawls — items changed between full-crawl cycles will not appear in Copilot results until the next full crawl.
- Assume a completed crawl means the items are immediately searchable in Copilot — semantic-index latency can be 15 minutes to 24 hours depending on queue depth `[verify-at-build]`.

## Edge cases / when the rule does NOT apply

A connector for a small, read-only archive (< 1,000 items, changes < monthly) may use only full crawls with no incremental schedule if the data update frequency does not justify the incremental setup complexity. Document the item count and update frequency.

## See also

- [`../agents/graph-connector-engineer.md`](../agents/graph-connector-engineer.md) — owns connector crawl strategy and semantic-index latency
- [`./connector-choose-synced-vs-federated-and-set-crawl-refresh.md`](./connector-choose-synced-vs-federated-and-set-crawl-refresh.md) — the upstream synced/federated decision that determines whether a crawl schedule is needed at all

## Provenance

Codifies the `copilot-connector-schema-design` skill from CLAUDE.md §9 on crawl/refresh patterns; Microsoft Graph connectors crawl documentation.

---

_Last reviewed: 2026-06-05 by `claude`_
