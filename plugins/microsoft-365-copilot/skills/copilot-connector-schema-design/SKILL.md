---
name: copilot-connector-schema-design
description: "Design a Microsoft 365 Copilot (Graph) connector schema — choose synced vs federated (MCP), declare property attributes (searchable/queryable/retrievable), apply the mandatory semantic-label map (title/url/createdBy/...), ingest ACLs for per-user trimming, and plan crawl/refresh + semantic-index latency. Use when building a Copilot connector to ground Copilot on a line-of-business store."
---

# Copilot connector schema design

Playbook for `graph-connector-engineer`. Source of truth: [`../../knowledge/copilot-connectors-2026.md`](../../knowledge/copilot-connectors-2026.md). Template: [`../../templates/copilot-connector-schema.md`](../../templates/copilot-connector-schema.md).

## 1. Synced or federated?
- **Synced** — index into Graph, semantic ranking, ACL-trimmed, scales (semantic-index latency).
- **Federated (MCP)** — real-time, no index, freshness over scale `[verify-at-build]`.

## 2. Define properties + attributes
Per property: `searchable` / `queryable` / `retrievable` / `refinable`. Only mark what you need — over-marking bloats the index.

## 3. Apply the mandatory semantic labels
Every relevant property maps to a semantic label — **unlabeled properties degrade ranking and break citations:**

| Label | Property |
|---|---|
| `title` | item title (primary ranking + citation) |
| `url` | item link (citation) |
| `iconUrl` | icon (citation rendering) |
| `createdBy` / `lastModifiedBy` | people (authority/recency) |
| `authors` | people retrieval |
| `createdDateTime` / `lastModifiedDateTime` | recency ranking |

## 4. Ingest ACLs (security control)
Attach ACLs (Entra users/groups / everyone / external) per item so Copilot trims per identity. **An "everyone" ACL is an oversharing incident** → route the ACL design to `ravenclaude-core/security-reviewer` and remediation to `copilot-admin-governance`.

## 5. Crawl + refresh
Full vs incremental; deletion handling; set expectations on the semantic-index latency window ("ingested" ≠ "queryable now").

## 6. Licensing impact
Connectors are Copilot-license-gated + meter item quotas — state seat + quota impact.

## Anti-patterns
- Any unlabeled property; "everyone" ACLs; promising instant queryability after ingestion; choosing synced/federated by habit; grounding org data with no license line.
