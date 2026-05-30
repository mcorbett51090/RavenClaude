# Copilot (Graph) connectors — schema, semantic labels, ACLs (2026)

**Last reviewed:** 2026-05-30
**Confidence:** High on schema/label/ACL model (first-party). `[verify-at-build]` on item quotas + the federated/MCP GA status.
**Read when:** building a Copilot connector to ground Copilot on a line-of-business store.

---

## Synced vs federated

- **Synced** — crawl the source, **index into Microsoft Graph**, semantic ranking; honors **ingested ACLs** for per-user trimming; scales. Crawl/refresh has **semantic-index latency** — "ingested" ≠ "queryable now".
- **Federated (MCP)** — **real-time over MCP**, **no index**; freshness over scale; ACLs per the source. `[verify-at-build]` on GA status.

Grounding: [Copilot connectors overview](https://learn.microsoft.com/microsoft-365/copilot/extensibility/overview-copilot-connector).

## The schema + mandatory semantic labels

Every connector defines an `externalItem` schema (properties + types + searchable/queryable/retrievable attributes). **Semantic labels are mandatory** — they map properties to the meaning Copilot ranks + cites on:

| Semantic label | Maps to | Why it matters |
|---|---|---|
| `title` | item title | primary ranking signal + citation text |
| `url` | item URL | citation link |
| `iconUrl` | item icon | citation rendering |
| `createdBy` / `lastModifiedBy` | people | recency/authority ranking |
| `authors` | people | people-based retrieval |
| `createdDateTime` / `lastModifiedDateTime` | timestamps | recency ranking |

An unlabeled property degrades semantic ranking and won't render in citations. House opinion #6: **no unlabeled connector properties.** See the [`copilot-connector-schema-design`](../skills/copilot-connector-schema-design/SKILL.md) skill + the [`copilot-connector-schema`](../templates/copilot-connector-schema.md) template.

## ACL ingestion + trimming (a security control)

Copilot trims results **per identity** using the ACLs you ingest with each item (Entra users/groups, "everyone", or external). **A connector indexed with "everyone" ACLs is an oversharing incident.** House opinion #7: connector ACLs are a security control — **route the ACL design through `ravenclaude-core/security-reviewer`** and coordinate oversharing remediation with `copilot-admin-governance` (see [`copilot-security-purview-2026.md`](copilot-security-purview-2026.md)).

## Crawl + refresh

Full vs incremental crawl; deletion handling; the semantic-index latency window. The connector SDK + Microsoft Graph connector APIs (Entra-authenticated) drive ingestion; the prebuilt connector gallery covers common sources.

## Licensing impact

Connectors are Copilot-license-gated and meter **item quotas** per tenant — a large source can exhaust the quota. State the seat + quota impact on every connector recommendation.

## Refresh triggers
- Federated/MCP connector GA status changes.
- Item-quota numbers change.
