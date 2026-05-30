# Template — Copilot (Graph) connector schema

Copy + fill. Source of truth: [`../knowledge/copilot-connectors-2026.md`](../knowledge/copilot-connectors-2026.md). Every relevant property gets a semantic label; ingest ACLs.

## Connection + schema (Microsoft Graph `externalConnectors`)

```jsonc
{
  "id": "<connectionId>",
  "name": "<connection display name>",
  "description": "<source>",
  // synced vs federated — see grounding-source-decision-2026.md
  "connectorMode": "synced", // or "federated" (MCP) [verify-at-build]
  "schema": {
    "baseType": "microsoft.graph.externalItem",
    "properties": [
      { "name": "title",        "type": "String",  "isSearchable": true,  "isRetrievable": true, "labels": ["title"] },
      { "name": "url",          "type": "String",  "isRetrievable": true, "labels": ["url"] },
      { "name": "iconUrl",      "type": "String",  "isRetrievable": true, "labels": ["iconUrl"] },
      { "name": "author",       "type": "String",  "isQueryable": true,   "isRetrievable": true, "labels": ["createdBy", "authors"] },
      { "name": "lastModified", "type": "DateTime","isRefinable": true,   "isRetrievable": true, "labels": ["lastModifiedDateTime"] },
      { "name": "body",         "type": "String",  "isSearchable": true }
      // Mark only what you need. EVERY relevant property should carry a semantic label.
    ]
  }
}
```

## Per-item ingestion (ACLs — the security control)

```jsonc
{
  "id": "<itemId>",
  "acl": [
    // Trim per identity. Avoid { "value": "everyone" } — that's an oversharing incident.
    { "type": "group", "value": "<entra-group-id>", "accessType": "grant" }
  ],
  "properties": { "title": "<...>", "url": "<...>", "author": "<...>", "lastModified": "<...>", "body": "<...>" },
  "content": { "value": "<full text>", "type": "text" }
}
```

## Activity settings (optional, for people/recency ranking)
Map share/view/comment activity to boost ranking where the source supports it.

## Pre-ship checklist
- [ ] Synced vs federated chosen from the decision tree.
- [ ] **Every relevant property carries a semantic label** (title/url/createdBy/...).
- [ ] **ACLs ingested per item** for per-user trimming; no "everyone" grants.
- [ ] ACL design routed to `ravenclaude-core/security-reviewer`.
- [ ] Crawl/refresh + deletion handling defined; semantic-index latency communicated.

**Licensing impact:** <connector item quota; Copilot seats; or "none">
