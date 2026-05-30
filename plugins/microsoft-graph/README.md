# microsoft-graph

A Claude Code plugin: a specialist **Microsoft Graph developer team** for the Graph API — querying, identity/authorization on Entra, and the workload surfaces.

## What's inside

- **3 agents** — `graph-api-engineer` (OData query/paging/`$batch`/delta, throttling, SDKs), `graph-identity-engineer` (Entra app registration, delegated vs application permissions, scopes/consent, auth flows, least-privilege), `graph-workloads-engineer` (users/groups, mail/calendar, Teams, files, change notifications/subscriptions).
- **knowledge/** — citation-grounded reference with Mermaid **decision trees** (permission type, auth flow, query vs delta vs subscription, paging/batching, throttling response, large-file upload).
- **best-practices/** — named, citable rules surfaced in the marketplace repo-guide + dashboard Guidance tab.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install microsoft-graph@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.

## Boundaries (seams)

| Need | Goes to |
|---|---|
| Copilot (Graph) **connectors** / external-item ingestion for Copilot | `microsoft-365-copilot/graph-connector-engineer` |
| Entra **tenant** identity governance (Conditional Access, PIM, B2B/B2C) | `azure-cloud/entra-identity` |
| Dataverse / Power Platform data | `power-platform` |
| Permission-scope / consent / secret-handling review | `ravenclaude-core/security-reviewer` |

This plugin owns the **app-on-Graph** developer surface broadly; it cross-links the Copilot-connector and tenant-identity surfaces rather than duplicating them. See [`CLAUDE.md`](./CLAUDE.md) for the team constitution.
