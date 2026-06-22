# Copilot (Graph) connectors — schema, semantic labels, ACLs (2026)

**Last reviewed:** 2026-06-13 · **Federated/MCP GA status + custom-federated-connector support re-verified 2026-06-13** via the Microsoft-Learn MCP.
**Confidence:** High on schema/label/ACL model (first-party). `[verify-at-build]` on item quotas. **Federated (MCP) connectors are now Generally Available (GA 2026-06-02).**
**Read when:** building a Copilot connector to ground Copilot on a line-of-business store.

---

## Synced vs federated

- **Synced** — crawl the source, **index into Microsoft Graph**, semantic ranking; honors **ingested ACLs** for per-user trimming; scales. Crawl/refresh has **semantic-index latency** — "ingested" ≠ "queryable now".
- **Federated (MCP)** — **real-time over MCP**, **no index**; freshness over scale; ACLs per the source (user identity/permissions; **read-only**; auditable in Purview). **GA 2026-06-02** across M365 Copilot Chat, the Researcher agent, and **Agent Mode in Excel**; admin-managed in **Admin Center → Copilot → Connectors** with a **7-day admin review window** before end-user availability + staged rollout. Sources: Microsoft-published, partner-submitted-and-approved, **or custom federated connectors built by your org** — the prior "synced only" restriction was lifted. A custom federated connector starts with an **org-stood-up remote MCP server** exposing **read-only** tools (e.g. `search`/`fetch`/`query`, each with the `readOnlyHint` annotation); auth via **Microsoft Entra SSO or OAuth 2.0** (registration ID from the Teams Developer Portal); created in **Admin Center → Copilot → Connectors → Gallery → "Created by your org" → Create a new connector**. Requires Global Administrator or AI Administrator. **Because the MCP server is org-operated (not Microsoft-managed), route its auth/scope/ACL design through `ravenclaude-core/security-reviewer` before production enablement (house opinion #7).** ([set up custom federated connectors](https://learn.microsoft.com/microsoft-365/copilot/connectors/set-up-custom-federated-connectors), [submit a federated connector](https://learn.microsoft.com/microsoft-365/copilot/connectors/submit-federated-connector), [federated connectors overview](https://learn.microsoft.com/microsoft-365/copilot/connectors/federated-connectors-overview)) `[verified 2026-06-13 via microsoft_docs_search against learn.microsoft.com/microsoft-365/copilot/connectors/set-up-custom-federated-connectors]` `[verify-at-use — GA status + Admin Center path subject to Microsoft UI/preview changes]`

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
- Federated/MCP connector GA status changes. _(GA reached 2026-06-02; **custom org-built federated connectors shipped — verified 2026-06-13**; watch for further surface/feature expansion beyond Chat/Researcher/Excel Agent Mode.)_
- Item-quota numbers change.
