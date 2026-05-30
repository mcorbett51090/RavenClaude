# Semantic-label every connector property and ingest real ACLs — never index with "everyone"

**Status:** Absolute rule — an unlabeled property degrades ranking; an "everyone" ACL is an oversharing incident.

**Domain:** Grounding / Copilot (Graph) connectors

**Applies to:** `microsoft-365-copilot`

---

## Why this exists

A Copilot (Graph) connector indexes a line-of-business source into Microsoft Graph so Copilot can rank and cite it. Two things make or break that index. First, **semantic labels** map each schema property to the meaning Copilot ranks and cites on — `title`, `url`, `iconUrl`, `createdBy`/`lastModifiedBy`, `authors`, timestamps. An unlabeled property degrades semantic ranking and won't render in citations. Second, **ACLs are the security control**: Copilot trims results per identity using the ACLs you ingest with each item. A connector indexed with "everyone" ACLs surfaces every item to every user — latent oversharing turned into active discovery. These are house opinions #6 and #7. The ACL *verdict* is owned by `ravenclaude-core/security-reviewer`, not this plugin.

## How to apply

Label every property, ingest per-item ACLs from the source (Entra users/groups), and route the ACL design to the security reviewer.

```jsonc
// Schema: map properties to semantic labels (the ranking + citation signals)
{
  "baseType": "microsoft.graph.externalItem",
  "properties": {
    "title":        { "type": "String",         "isSearchable": true, "labels": ["title"] },
    "url":          { "type": "String",          "isRetrievable": true, "labels": ["url"] },
    "author":       { "type": "String",          "isQueryable": true,  "labels": ["authors", "createdBy"] },
    "lastModified": { "type": "DateTime",         "isRetrievable": true, "labels": ["lastModifiedDateTime"] }
  }
}

// Item ingestion: per-identity ACL so Copilot trims per user — NOT "everyone"
{
  "acl": [
    { "type": "group", "value": "<entra-group-id>", "accessType": "grant" }
  ]
}
```

**Do:**
- Apply a semantic label to **every** schema property — at minimum `title` / `url` / `iconUrl` plus people + timestamp labels.
- Ingest real per-item ACLs (Entra users/groups) so Copilot trims results per user.
- Account for **semantic-index latency** — "ingested" ≠ "queryable now"; a missing result may just be crawl lag.
- Route the ACL design through `ravenclaude-core/security-reviewer` and coordinate oversharing with `copilot-admin-governance`.

**Don't:**
- Leave any property unlabeled.
- Index with "everyone" / broad ACLs to "make it work" — that is an oversharing incident.
- State a connector recommendation without a `Licensing impact:` line (connectors are seat-gated and meter item quotas, #8).

## Edge cases / when the rule does NOT apply

A **federated (MCP)** connector fetches in real time and does **not** index into Graph — there is no semantic index to rank against, and ACLs are honored per the source rather than ingested, so the index-trimming mechanics differ (verify federated/MCP GA status, `[verify-at-build]`). Genuinely public, tenant-wide reference content may legitimately carry an "everyone" ACL — but that is a deliberate, reviewed classification, never the default for line-of-business data.

## See also

- [`../knowledge/copilot-connectors-2026.md`](../knowledge/copilot-connectors-2026.md) — the schema, the full semantic-label map, ACL ingestion/trimming, synced vs federated
- [`../knowledge/grounding-source-decision-2026.md`](../knowledge/grounding-source-decision-2026.md) — the grounding-source decision tree (connector vs SharePoint knowledge vs API plugin)
- [`./remediate-oversharing-before-enabling-copilot.md`](./remediate-oversharing-before-enabling-copilot.md) — the tenant-level companion to per-connector ACL trimming
- [`../skills/copilot-connector-schema-design/SKILL.md`](../skills/copilot-connector-schema-design/SKILL.md) · [`../agents/graph-connector-engineer.md`](../agents/graph-connector-engineer.md)

## Provenance

Codifies house opinions #6, #7, and #8 from [`../CLAUDE.md`](../CLAUDE.md). Grounded in [`../knowledge/copilot-connectors-2026.md`](../knowledge/copilot-connectors-2026.md), sourced from the Microsoft Learn Copilot-connectors overview. The ACL *verdict* escalates to `ravenclaude-core/security-reviewer` per the plugin constitution.

---

_Last reviewed: 2026-05-30 by `claude`_
