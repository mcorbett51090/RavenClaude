---
description: Build a Microsoft 365 Copilot (Graph) connector — choose synced vs federated for the right reason, semantic-label every schema property, ingest real per-item ACLs (never "everyone"), and set crawl/refresh to the source's change rate.
argument-hint: "[the source, e.g. 'index our LoB ticketing system into Copilot']"
---

# Build a Graph connector

You are running `/microsoft-365-copilot:build-graph-connector`. Build (or diagnose) the Copilot connector for what the user described (`$ARGUMENTS`), following this plugin's `graph-connector-engineer` discipline — labels drive ranking and citation, ACLs are the security control.

## When to use this

Copilot needs to ground on and rank/cite a line-of-business store. If Copilot needs to *act* against the backend (create/update/delete), that's an API plugin — use `/microsoft-365-copilot:scaffold-api-plugin`. If the data lives in Fabric/OneLake, the lakehouse design is the `microsoft-fabric` seam; only the surfacing-into-Copilot is here.

## Steps

1. **Choose synced vs federated from the data's freshness + scale need** — synced (indexes into Graph, ranked, scales, ingested ACLs, but crawl/index latency) vs federated/MCP (real-time over MCP, no index, doesn't scale/rank) (`connector-choose-synced-vs-federated-and-set-crawl-refresh.md`).
2. **Set incremental + full crawl intervals to the source's real change rate** — don't accept the 15-min/1-week defaults blindly; plan deletion handling so removed items leave the index (same file).
3. **Semantic-label every schema property** — at minimum `title`/`url`/`iconUrl` plus people (`createdBy`/`lastModifiedBy`/`authors`) and timestamp labels; an unlabeled property degrades ranking and won't render in citations (`label-and-acl-trim-every-connector-property.md`).
4. **Ingest real per-item ACLs** (Entra users/groups) so Copilot trims results per user — never index with "everyone"; that's an oversharing incident (same file). Watch for connectors (e.g. ADLS Gen2) that can't ingest item-level ACLs — route those to governance first.
5. **Set expectations on semantic-index latency** — "ingested" is not "queryable now"; diagnose a missing result as crawl/index lag before schema (`connector-choose-synced-vs-federated-and-set-crawl-refresh.md`).
6. **Coordinate with tenant oversharing remediation** — a connector is the per-source companion to the tenant-level cleanup (`remediate-oversharing-before-enabling-copilot.md`). Use the `templates/copilot-connector-schema.md` shape.

## Guardrails

- Never leave a property unlabeled or index with broad/"everyone" ACLs to "make it work."
- The ACL design *verdict* routes to `ravenclaude-core/security-reviewer` (mandatory); oversharing coordination to `copilot-admin-governance`.
- State a `Licensing impact:` line — connectors are seat-gated and meter item quotas. This plugin is advisory: emit the schema + Graph/SDK snippets the engineer runs in their own tenant.
