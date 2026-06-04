# Evidence.dev Project Structure — `plugins/edtech-partner-success/dashboard-evidence/`

> Reference skeleton for the Tier 1 (single-PSM) rendering layer. Codex copies this tree, customizes per the spec in `docs/research/2026-06-04-partner-success-dashboard-requirements/spec.md`, and ships a Cloudflare-Pages-hostable static site.
>
> Source: `/tmp/research-rendering-layer.md §1.1 + §6` (deferred)

## Directory tree

```
plugins/edtech-partner-success/dashboard-evidence/
├── README.md                              # one-paragraph "what + how to run"
├── package.json                           # Evidence pinned version, `npm run dev` / `npm run build`
├── .gitignore                             # node_modules/, .evidence/, .env
├── .env.example                           # SNOWFLAKE_ACCOUNT, USER, ROLE, WAREHOUSE, DATABASE (template only)
├── evidence.config.yaml                   # site title, theme tokens, navigation
├── sources/
│   └── snowflake/
│       ├── connection.yaml                # native Snowflake connector config (creds via env)
│       ├── portfolio_summary.sql          # § Home Dashboard / Portfolio Summary
│       ├── portfolio_health_snapshot.sql  # § Home Dashboard / Portfolio Health Snapshot
│       ├── daily_action_center.sql        # § Daily Action Center — prioritized task list
│       ├── partner_360.sql                # § Partner 360 — single-partner detail
│       ├── account_timeline.sql           # § Account Timeline — merged event history
│       ├── lifecycle_stages.sql           # § Lifecycle Tracking
│       ├── contract_alerts.sql            # § Contract Center (180/120/90/60/30-day alerts)
│       ├── usage_adoption.sql             # § Usage & Adoption (Snowflake-native)
│       ├── family_engagement.sql          # § Family Engagement
│       ├── top15.sql                      # § Top 15 Dashboard
│       ├── renewals.sql                   # § Renewal Command Center (180/120/90/60/30 buckets)
│       ├── support_escalations.sql        # § Support & Escalation
│       ├── expansion_opportunities.sql    # § Expansion Opportunity
│       └── priority_ranking.sql           # § Dashboard Priority Ranking Logic
├── pages/
│   ├── index.md                           # Home Dashboard (the 5-second-test page)
│   ├── action-center.md                   # Daily Action Center (full prioritized list)
│   ├── calendar.md                        # Calendar View (monthly/weekly/upcoming)
│   ├── partner/
│   │   └── [partner_id].md                # Partner 360 — drill-down (parameterized route)
│   ├── lifecycle.md                       # Lifecycle Tracking
│   ├── contracts.md                       # Contract Center
│   ├── usage.md                           # Usage & Adoption
│   ├── family-engagement.md               # Family Engagement
│   ├── top15.md                           # Community Top 15
│   ├── health.md                          # Health Dashboard
│   ├── sentiment.md                       # Sentiment Dashboard
│   ├── success-plans.md                   # Success Plan Dashboard
│   ├── renewals.md                        # Renewal Command Center
│   ├── support.md                         # Support & Escalation
│   ├── expansion.md                       # Expansion Opportunity
│   ├── pd-tracker.md                      # Professional Development Tracker
│   └── relationships.md                   # Relationship Mapping
├── components/
│   ├── StatusBadge.svelte                 # green/yellow/red + icon (WCAG 1.4.1 compliant)
│   ├── FreshnessChip.svelte               # "Updated 2 min ago" + Live/Stale/Paused
│   ├── ActionRow.svelte                   # one row of the Daily Action Center
│   ├── EmptyState.svelte                  # diagnostic-headline + CTA pattern
│   └── Bandline.svelte                    # Few's bandline extension of Tufte sparkline
├── static/
│   ├── styles/
│   │   └── dashboard-styles.css           # color tokens (see /tmp/enhancement-reference-dashboard-styles.css)
│   └── icons/                             # status icons (filled/hollow circle, triangle, square)
└── tests/
    └── acceptance-checklist.md            # the wife's 5-second test (see acceptance-tests file)
```

## Key file purposes

| File | Purpose | Rationale (source) |
|---|---|---|
| **`sources/snowflake/connection.yaml`** | Single named connection consumed by every `.sql` file via `${snowflake.<query>}`. Creds come from env at *build* time, so the published static site never carries warehouse creds. | Research §1.1 Evidence "queries run at build time… so the public site never holds warehouse creds." |
| **`sources/snowflake/*.sql`** | One file per logical dataset the dashboard needs. Named to match the spec sections so a PSM reviewing the SQL can find what feeds what. Snowflake-flavored (DATEADD, IFF, QUALIFY, TRY_TO_NUMBER). | Spec § "Data Sources" — Snowflake is the warehouse for usage/adoption/messaging. |
| **`pages/index.md`** | The Home Dashboard. Must be answerable in 5 s without scrolling, filtering, or hovering. | UX research §3 / §11 principle 1: 5-second rule governs top fold. |
| **`pages/partner/[partner_id].md`** | Parameterized drill-down route. Evidence supports `[param]` in filenames and `params.partner_id` in queries. | Research §1.1: "Parameterized pages + `<DataTable link=…>` components. Works well for hierarchical drill." |
| **`components/StatusBadge.svelte`** | Reusable status indicator — color + icon + text (≥2 channels). | UX research §4 + §11 principle 2: never color-only. WCAG 1.4.1. |
| **`components/FreshnessChip.svelte`** | "Updated N min ago" + state pill. | UX research §7: always show data freshness; three-state Live/Stale/Paused. |
| **`components/EmptyState.svelte`** | Diagnostic-headline + supporting copy + one CTA. | UX research §6: distinguish first-run / filter-emptied / healthy-empty. |
| **`evidence.config.yaml`** | Site title, theme tokens (load `dashboard-styles.css`), nav order. | Evidence's responsive grid + theme presets (research §1.1 "Mobile responsive: Yes — built-in"). |
| **`.env.example`** | Documents required env vars; the real `.env` stays out of git. | Standard 12-factor; Snowflake creds only at build time. |

## Build / run

```bash
# Local dev (hot-reload, queries hit Snowflake live)
cd plugins/edtech-partner-success/dashboard-evidence
npm install
cp .env.example .env       # fill in Snowflake creds
npm run dev                # opens http://localhost:3000

# Production build (static HTML + baked query results)
npm run build              # outputs build/ — deploy to Cloudflare Pages

# Scheduled rebuild (hourly is the sweet spot — see /tmp/research-rendering-layer.md §1.1)
# Cloudflare Pages > Settings > Builds > Cron: "0 * * * *"
```

## What Codex should customize

1. **`sources/snowflake/connection.yaml`** — point at the real Snowflake account/role/warehouse.
2. **Each `.sql` file** — replace the placeholder table names with the actual schema. The query *shapes* are correct; the `FROM` clauses are stubs.
3. **`evidence.config.yaml`** navigation — re-order pages by the wife's preferred sequence after the 5-second test runs (see `enhancement-reference-dashboard-acceptance-tests.md`).
4. **`components/StatusBadge.svelte`** — wire the icon set in `static/icons/` to the green/yellow/red tokens. Don't invent new colors; use `dashboard-styles.css` tokens.

## What Codex should NOT do

- Don't add an "embed" or "iframe" mode — Evidence v0 is single-PSM; multi-tenant is a v2 React+Cube concern (research §6 migration path).
- Don't try to make the site real-time. Evidence is "awkward" at sub-hour refresh (research §1.1). For the live operational panel, use Streamlit-in-Snowflake (separate file).
- Don't put creds in `evidence.config.yaml` or any committed file. Env-only.
