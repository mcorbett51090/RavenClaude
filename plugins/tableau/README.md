# tableau

A Claude Code plugin: a specialist **Tableau analytics team** for Tableau Desktop / Cloud / Server, Tableau Prep, and the developer + platform surface.

## What's inside

- **3 agents** — `tableau-viz-engineer` (VizQL, calculations/LOD/table-calcs, dashboard design), `tableau-data-architect` (modeling, extracts vs live, Prep, performance), `tableau-admin` (governance, RLS, content ALM, embedding, Pulse/Tableau-Next).
- **knowledge/** — citation-grounded reference with Mermaid **decision trees** (chart selection, relationship vs join vs blend, extract vs live, LOD vs table calc, RLS mechanism, embedding auth, content promotion).
- **best-practices/** — named, citable rules (one per file) surfaced in the marketplace repo-guide + dashboard Guidance tab.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install tableau@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.

## Boundaries (seams)

| Need | Goes to |
|---|---|
| Warehouse / semantic modeling upstream | `data-platform`, `microsoft-fabric` |
| Salesforce source data / CRM Analytics on-platform | `salesforce` |
| Power BI comparison / migration | `power-platform/power-bi-engineer` |
| RLS / Connected Apps / embedding auth review | `ravenclaude-core/security-reviewer` |

See [`CLAUDE.md`](./CLAUDE.md) for the team constitution (roster, routing, house opinions, anti-patterns).
