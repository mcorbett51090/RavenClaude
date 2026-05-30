# Choose synced vs federated for the right reason, and set crawl/refresh to match the data's freshness — "ingested" is not "queryable now"

**Status:** Primary diagnostic — when connector data is missing, stale, or slow to appear, check the synced/federated choice and the crawl schedule first; semantic-index latency is the most common false alarm.

**Domain:** Grounding / Copilot (Graph) connectors

**Applies to:** `microsoft-365-copilot`

---

## Why this exists

A Copilot connector grounds Copilot on a line-of-business store, and the first decision — **synced vs federated** — determines its entire latency and scale profile. A **synced** connector crawls the source and **indexes into Microsoft Graph** with semantic ranking: it scales, ranks well, and honors ingested ACLs, but it has **crawl + semantic-index latency** — newly ingested content is *not* instantly queryable. A **federated (MCP)** connector fetches **real-time over MCP with no index**: fresh by construction, but it doesn't scale or rank like the index and ACLs are honored per the source. The recurring incident is choosing synced for data that must be real-time (and then fighting crawl lag), or choosing federated for a large store that needs ranked retrieval (and getting slow, unranked results). The second recurring incident is reporting "my data doesn't show up" minutes after ingestion when it is simply **index latency** — the default crawl is 15 min incremental / 1 week full, and the semantic index trails the crawl. Match the connector type to the freshness requirement, then set the crawl schedule deliberately. This is house opinion #5.

## How to apply

Pick the connector type from the data's freshness + scale need, then set incremental and full crawl intervals to match how often the source changes. Expect — and communicate — index latency on synced connectors.

```text
SYNCED  (index into Graph, ranked, scales, ingested ACLs)
        use for: scale + ranked retrieval over a LoB store that tolerates minutes of lag
        crawl:   incremental (default 15 min) + full (default 1 week) — tune to change rate
        caveat:  semantic-index latency — "ingested" ≠ "queryable now"; deletion handling matters

FEDERATED / MCP  (real-time over MCP, no index)
        use for: freshness-over-scale; data that can't or shouldn't be indexed
        crawl:   N/A (no index) — ACLs per the source         [verify-at-build: GA status]
```

```jsonc
// Synced connector refresh settings (illustrative — set to the source's real change rate)
{
  "refresh": {
    "incrementalCrawlIntervalMinutes": 15,   // pick lower for fast-changing data
    "fullCrawlIntervalDays": 7,              // pick lower if items are deleted/restructured often
    "deletionHandling": "incremental"        // ensure removed source items leave the index
  }
}
```

**Do:**
- Choose **synced for scale + ranking**, **federated/MCP for real-time** — match the type to the job (#5).
- Set incremental + full crawl intervals to the source's actual change rate; don't accept defaults blindly.
- Plan **deletion handling** so removed source items leave the index (a stale citation is a trust failure).
- Set expectations on **semantic-index latency** — diagnose "missing result" as crawl/index lag before schema.

**Don't:**
- Pick synced for data that must be real-time, or federated for a store that needs ranked scale.
- Report "doesn't work" within the index-latency window — confirm crawl completion + index propagation first.
- State a connector recommendation without a `Licensing impact:` line — connectors are seat-gated and meter item quotas (#8).

## Edge cases / when the rule does NOT apply

Some Microsoft-built connectors (e.g. Azure Blob Storage) **cannot ingest item-level ACLs** and index everything as visible to everyone — that is an oversharing trap, not a freshness choice; route it to `copilot-admin-governance` + `ravenclaude-core/security-reviewer` before use (see [`./label-and-acl-trim-every-connector-property.md`](./label-and-acl-trim-every-connector-property.md)). Federated/MCP GA status and quota numbers are `[verify-at-build]`. If the data's *origin* is Fabric/OneLake, the lakehouse design is the `microsoft-fabric` seam; only the surfacing-into-Copilot is this plugin's.

## See also

- [`./label-and-acl-trim-every-connector-property.md`](./label-and-acl-trim-every-connector-property.md) — the schema + ACL half of every connector
- [`./connector-add-urltoitemresolver-and-user-activities-for-ranking.md`](./connector-add-urltoitemresolver-and-user-activities-for-ranking.md) — the ranking signals beyond labels
- [`../knowledge/copilot-connectors-2026.md`](../knowledge/copilot-connectors-2026.md) · [`../knowledge/grounding-source-decision-2026.md`](../knowledge/grounding-source-decision-2026.md)
- [`../agents/graph-connector-engineer.md`](../agents/graph-connector-engineer.md)
- [Copilot connectors overview](https://learn.microsoft.com/microsoft-365/copilot/extensibility/overview-copilot-connector) · [crawl-setting guidelines](https://learn.microsoft.com/microsoft-365/copilot/connectors/deployment-overview)

## Provenance

Codifies house opinion #5 from [`../CLAUDE.md`](../CLAUDE.md). Grounded in the Microsoft Learn Copilot-connectors overview, the deployment/crawl-settings guidelines (15-min incremental / 1-week full defaults), and the per-connector ACL pages (e.g. the ADLS Gen2 connector's "Everyone vs only people with access" permission model), retrieved 2026-05-30. Federated/MCP GA status is `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
