# data-platform plugin

> Data-platform team for the RavenClaude marketplace. Guides a consultant or operator through the four-layer stack — cloud database, ELT/connectors, interactive dashboard, embed pattern — needed to ship a database-backed dashboard inside a website or a client's web app.

**Designed for:** SMB consulting engagements ($25-50k, 4-6/year) where the deliverable is a custom database + dashboard + embed, not an off-the-shelf BI deployment.

## What's in the box

| Layer | What this plugin covers |
|---|---|
| **Database** | Supabase / Neon / RDS / Azure SQL / Fabric / DuckDB. Multi-tenant schema starter with RLS. |
| **ELT / connectors** | Airbyte / Fivetran / n8n. QuickBooks Online, Stripe, Salesforce, HubSpot, GA4, Shopify deep-dives. Custom Airbyte connector pattern for vendors not natively supported (EdTech LMS is the canonical gap). |
| **Dashboard front-end** | Evidence.dev (portfolio/marketing-site), Apache Superset / Metabase (client deliverable), Cube + Next.js + Tremor + Recharts (productized SaaS). |
| **Embed + auth** | JWT-issuance scaffolding, multi-tenant RLS policy templates, CSP / iframe-sandbox guidance. Postgres RLS, Cube `securityContext`, Power BI DAX roles. |

## Team

4 specialist agents:

- `database-setup-guide` — cloud-database setup, multi-tenant schema, RLS policies
- `etl-pipeline-engineer` — ELT pipeline design + source-system specifics (QBO / Stripe / Salesforce / HubSpot / GA4 / Shopify)
- `dashboard-builder` — Evidence / Superset / Metabase / Cube front-end work; JWT-embed flows
- `connector-developer` — custom Airbyte connector authoring (esp. EdTech LMS)

Plus **two skill-routed escalations to ravenclaude-core**:

- `ravenclaude-core/architect` — invoked for "what stack should I use?" engagement questions; reads this plugin's `stack-selection` skill
- `ravenclaude-core/security-reviewer` — invoked for any auth / JWT / RLS / embed CSP / iframe-sandboxing change; reads this plugin's `jwt-embed-issuance`, `rls-policy-authoring`, and `embed-csp-and-iframe-sandboxing` skills

## House rule (cross-plugin)

This plugin follows the marketplace's house rule: **domain plugins extend core via skills and knowledge; they fork core agents only when the domain's review rubric is genuinely incompatible with core's.** That's why there's no plugin-specific architect or security-reviewer here — the work is delegated upward to core, with this plugin supplying the domain-specific skills + knowledge.

## What's opinionated

- **Resists per-viewer-priced BI tools** (Looker, Tableau Embedded, Sigma, Metabase Pro) for SMB consulting. The math doesn't work at 5-50 viewers × 4-6 clients × $400+/viewer.
- **Tenant isolation is enforced at the closest-to-data layer the viewer's token cannot influence** — never at the rendering layer. Postgres RLS for raw-Postgres-backed; semantic layer (Cube, Power BI DAX roles) for semantic-layer-fronted.
- **Default stack for a 4-6-engagement consulting firm:** Supabase Pro ($25/mo) + DuckDB embedded + Airbyte Cloud Standard ($10/mo) + dbt Core + Apache Superset / Metabase OSS or Evidence.dev → ~$900/yr base cost.
- **Microsoft-stack clients are special.** Power BI Embedded + Fabric F2 reserved (~$156/mo) is often correct for M365-aligned engagements even when it's not the cheapest.
- **EdTech LMS is a connector gap.** Native ELT vendor coverage for Canvas / Moodle / Schoology is thin. The custom-Airbyte-connector pattern is the consulting differentiator. (See `knowledge/edtech-lms-connector-gap.md`.)

## Requires

- `ravenclaude-core@>=0.7.0`

## Install

```bash
/plugin marketplace add ravenclaude
/plugin install data-platform@ravenclaude
```

## Companion plugins (recommended when relevant)

- `power-platform` — when the engagement uses Power BI Embedded; `power-bi-engineer` owns DAX / semantic-model / PBIP, this plugin owns the embed pattern + non-Microsoft data stack
- `web-design` — when integrating the dashboard into a marketing site or app; `frontend-coder` integrates the components
- `edtech-partner-success` — when the engagement is EdTech vertical; this plugin owns the LMS connector + data layer, partner-success owns the renewal / QBR / health-scoring layer above

## Status

v0.1.0 — first ship. Scope sized at 4 agents / 7 skills / 7 knowledge files / 10 templates / 1 hook based on expert-reviewed plan (5 expert verdicts on 5 blockers, all accepted 2026-05-21).

## See also

- `CLAUDE.md` — full team constitution (12 sections)
- `plugins/ravenclaude-core/CLAUDE.md` — the domain-neutral team constitution inherited by every plugin
- `../../CLAUDE.md` — the meta-repo developer guide (working *on* the marketplace, not consuming it)

## Portfolio report (BI)

A self-contained, Power-BI/Tableau-style **pipeline-health report — freshness donut, latency trend, per-pipeline table with failure drill-downs** ships with this plugin.

> 📊 **[▶ View the report rendered in your browser](https://mcorbett51090.github.io/RavenClaude/plugins/data-platform/report.html)** — sortable, filterable, with row drill-downs. _(Published, read-only preview of the demo / synthetic data.)_
>
> _(Or [view the raw HTML source](report.html), or download and open locally — no server, no build step.)_

Rebuild from real data by editing [`bi-report/data.json`](bi-report/data.json) and running `python3 scripts/generate-bi-report.py --plugin data-platform`. Charts are inline SVG (no CDN); the engine + data shape are documented in [`edtech-partner-success/skills/health-report-dashboard`](../edtech-partner-success/skills/health-report-dashboard/SKILL.md).
