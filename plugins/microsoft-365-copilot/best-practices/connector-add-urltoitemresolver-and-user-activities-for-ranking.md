# Add a `urlToItemResolver` and user activities, and fill the `content` property — labels alone don't make a connector rank

**Status:** Pattern — strong default; semantic labels are necessary but not sufficient, the ranking signals (resolver, activities, rich content) are what move a connector from "indexed" to "actually cited".

**Domain:** Grounding / Copilot (Graph) connectors

**Applies to:** `microsoft-365-copilot`

---

## Why this exists

Teams label every connector property correctly, ingest ACLs, and still find their content rarely cited by Copilot. The reason is that semantic labels tell Copilot what each property *means*, but ranking is driven by additional signals most authors skip. Three of them matter most. **`urlToItemResolver`** (configured in the connection's `activitySettings`) lets the platform recognize when users share a URL to your content with each other — Copilot then boosts that item's importance for those users. **User activities** added on items (via the `addActivities` Graph API) boost items that are actually used — more activity, higher rank. And the **`content` property** must be ingested with rich, human-readable text: Copilot grounds and matches against `content`, and it "performs better on content-rich items" — a connector that indexes only metadata gives Copilot nothing to match a prompt against. A connector with perfect labels but no resolver, no activities, and a thin `content` field is technically correct and practically invisible.

## How to apply

Beyond the mandatory `title`/`url`/`iconUrl` labels, set `urlToItemResolver` in `activitySettings` at connection time, push user activities on items, and ingest rich text into `content`. Mark `content` and key text properties **searchable** (and remember labels require **retrievable**).

```jsonc
// 1. activitySettings at connection creation — enables share-detection boosting
{
  "activitySettings": {
    "urlToItemResolvers": [
      {
        "@odata.type": "#microsoft.graph.externalConnectors.itemIdResolver",
        "urlMatchInfo": { "baseUrls": ["https://lob.contoso.com"], "urlPattern": "/items/(?<id>[^/]+)" },
        "itemId": "{id}",
        "priority": 1
      }
    ]
  }
}

// 2. Rich `content` + searchable text so prompts have something to match
{
  "content": { "type": "text", "value": "<full human-readable body of the item, not just metadata>" },
  "properties": {
    "title": { "type": "String", "isSearchable": true, "isRetrievable": true, "labels": ["title"] }
  }
}

// 3. Boost frequently-used items with activities (Graph addActivities) — viewed/modified/shared
```

**Do:**
- Configure a **`urlToItemResolver`** in `activitySettings` so shared-URL boosting works.
- Ingest **rich `content`** text — Copilot matches prompts against `content`; metadata-only items rank poorly.
- Push **user activities** (`addActivities`) on items so usage boosts importance.
- Give the connection a **meaningful name + description** at creation — Copilot uses them to decide if the source is relevant.

**Don't:**
- Stop at semantic labels and assume the connector will rank — labels are necessary, not sufficient.
- Map a property to a label without marking it **retrievable** — labels require it, and large content mapped to a label increases search latency.
- Index only metadata with an empty/thin `content` property.

## Edge cases / when the rule does NOT apply

A **federated (MCP)** connector has **no index** and therefore no semantic-ranking or activity-boost surface — these signals don't apply; relevance there is the source's responsibility. Currently only the `title` semantic label is usable directly in M365 Copilot *prompts* (more are surfacing as the platform evolves, `[verify-at-build]`) — but you should still apply *all* applicable labels so you don't have to re-create the schema later. Activity ingestion adds write volume against the source; weigh it for very high-cardinality stores.

## See also

- [`./label-and-acl-trim-every-connector-property.md`](./label-and-acl-trim-every-connector-property.md) — the mandatory labels + ACL this rule builds on
- [`./connector-choose-synced-vs-federated-and-set-crawl-refresh.md`](./connector-choose-synced-vs-federated-and-set-crawl-refresh.md) — why these signals only apply to synced connectors
- [`../knowledge/copilot-connectors-2026.md`](../knowledge/copilot-connectors-2026.md) · [`../agents/graph-connector-engineer.md`](../agents/graph-connector-engineer.md)
- [Make your Graph connector work better with Copilot](https://learn.microsoft.com/graph/connecting-external-content-experiences) — the resolver + activities + content guidance

## Provenance

Grounded in the Microsoft Learn "Copilot connector experiences" and "Configure custom connectors for Microsoft 365 Copilot" pages — the explicit five-point list (semantic labels; rich `content`; `searchable`; `urlToItemResolver` in `activitySettings`; user activities) and the "only the `title` label currently usable in prompts" note — plus the schema-management "properties must be retrievable before mapping to labels" rule, all retrieved 2026-05-30. Extends house opinion #6 from [`../CLAUDE.md`](../CLAUDE.md).

---

_Last reviewed: 2026-05-30 by `claude`_
