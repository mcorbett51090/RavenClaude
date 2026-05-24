# Embedded analytics landscape 2026

> **Last reviewed:** 2026-05-21. Sources: vendor pricing pages (verified where noted), Vendr/G2 procurement benchmarks (secondary), 2026 industry awards (Embeddable Data Breakthrough). Refresh when: (a) a major BI tool restructures pricing, (b) Gartner MQ or Forrester Wave publishes new edition, (c) M&A reshapes the tier-1 landscape, or (d) an EdTech-vertical CFA platform finally launches (would materially rewrite this file).

## Key 2026 finding: no K-12-vertical CSP exists

After extensive vendor / job-board / industry-coverage search, **zero K-12-vertical customer-facing analytics platforms exist as of 2026**. EdTech vendors use generic CFA platforms (most commonly Gainsight, ChurnZero, or HubSpot) and bolt on rostering integration (Clever, ClassLink, Ednition). **The plugin's value sits in the EdTech-shaped methodology layer above generic platforms — not in recommending a magic vertical tool.**

## Default recommendation (opinionated)

For a 4-6 engagement/year solo consulting practice:

- **Case A (portfolio on ravenpower.net):** **Evidence.dev OSS** (MIT) → static deploy to Vercel/Netlify. $0 hosting.
- **Case B (client deliverable):** **Apache Superset OR Metabase OSS**, self-hosted on $20-40/mo VPS, JWT-secured embed.
- **Case B alt for Microsoft clients:** **Power BI Embedded F2 reserved (~$156/mo)**.
- **Case C (productized SaaS):** **Cube OSS (Apache 2.0) + Next.js + Tremor + Recharts + shadcn/ui + Postgres RLS.**

**Resists by default:** Looker (~$200-300k/yr deployment), Tableau Embedded (~$60-150k/yr), Sigma ($61k median), Metabase Pro Interactive Embedding ($575/mo + $12/viewer). The per-viewer-pricing math doesn't fit SMB consulting profiles.

## Tier 1 — Gartner MQ Leaders (2024 + 2025)

The 2024 and 2025 Gartner Magic Quadrant for Customer Success Management Platforms named **Gainsight, ChurnZero, and Totango** as Leaders both years.

### Gainsight
- **Market position:** Leader in 2025 Gartner MQ, Leader in Forrester Wave Q4 2025
- **Corporate:** Vista Equity Partners majority owner from $1.1B 2021 acquisition [per TechCrunch](https://techcrunch.com/2020/11/30/vista-acquires-gainsight-for-1-1b-adding-to-its-growing-enterprise-arsenal/)
- **Pricing (secondary):** Essentials ~$1,200-$2,400/user; Enterprise ~$2,400-$4,200/user; mid-market CS Cloud deployments $60-120k/year. **Vendor doesn't publish list prices.**
- **Implementation:** 3-6 months in practice; total cost 1.2-1.5× license once services included

### ChurnZero
- **Consensus mid-market pick.** Gartner MQ Leader 2024, 2025. G2 4.7/5 across 1,400+ reviews.
- **AI Marketplace** launched 2025 with **14 agentic AI teammates** [per ChurnZero press release](https://churnzero.com/press-release/churnzero-extends-industry-leadership-by-reshaping-customer-success-with-ai-teammates/). The most production-ready autonomous-agent layer at mid-market price points in 2026.
- **Pricing (secondary):** starts ~$12,000/year; HubSpot Marketplace listing $16,000/year + per-user

### Totango (post-merger)
- **Totango + Catalyst merged February 28, 2024** in all-stock deal (no cash). Backed by Great Hill Partners. Co-CEOs Alistair Rennie (ex-Totango) and Edward Chiu (ex-Catalyst). **Verified [via TechCrunch](https://techcrunch.com/2024/02/28/totango-catalyst-merger-customer-success/) 2026-05-21.**
- **Parative AI acquisition Oct 22, 2024** — launched "Unison" AI-driven churn-intelligence engine
- **Catalyst brand on sunset trajectory** — treat as historical for new evaluations

## Tier 2 — Credible challengers

### Planhat
- Stockholm-based, ~200 employees, ~$50.9M raised, 2022 SEK 494M led by Sprints Capital
- **Differentiation:** unified data-model platform — CRM + time-series + comm data + tickets + transcripts as first-class objects with parent-child hierarchies. Real technical differentiator vs. Gainsight's playbook-centric design.

### Vitally
- Brooklyn-based, Series B Feb 2023, ~$40.2M total raised (Andreessen Horowitz + Next47)
- **PLG-focused.** 2025 "Hubs" feature positioned as productivity layer replacing Notion/Google Docs

### ClientSuccess
- Lehi UT, ~36 employees, ~$6M raised. Acquired Status (onboarding) Nov 2023, Baton 2024, Product Signals Jan 2025.
- **SMB-to-lower-mid-market;** built-in onboarding via Status + Baton

### Custify
- **Starts $899/month**, implementation in days
- **Target:** 2-10 CSM teams ready to leave spreadsheets but not ready for Gainsight-scale spend

## Pure embedded-analytics specialists

### Sigma
- **Median deployment $61,158/year ($17.5k-$131k range, Vendr 117 buyers).** Embedded add-on can 2-3× the base.
- **Still private** May 2026 (no IPO). $80M raised May 18 2026 at $1.5B valuation.
- **Out of scope** for SMB consulting.

### Cube (cube.dev)
- **Cube Core is Apache 2.0, fully free, self-hostable.** Semantic layer + caching + API layer; not a chart library.
- **Cube Cloud (verified 2026-05-21):** Free → **Starter $40/dev/mo** → **Premium $80/dev/mo** (Premium includes embedded dashboards) [per cube.dev/pricing](https://cube.dev/pricing)
- **2026 positioning:** Cube Copilot, Tesseract modeling engine, Visual Modeler, Data Access Policies. Joined Open Semantic Interchange spec (Jan 2026).
- **The strongest non-BI building block** for a consulting firm productizing a dashboard offering

### Embeddable.com
- **Won Embedded Analytics Solution of the Year at Data Breakthrough Awards 2026**
- **Web-component-based** (not iframe); custom React UI in consumer's codebase; Embeddable handles backend + RLS + SDK
- **Pricing opaque** (fixed monthly, sales-quoted)

### GoodData
- **Workspace-based pricing starting $1,500/mo** with unlimited users
- React/Python SDKs; supports white-label

### Domo Everywhere
- **~$3,000/month starting**, credit-based (every customer view/filter burns credits)
- Forecasting cost is notoriously hard

### Klipfolio Klips / PowerMetrics
- **Klips $90-$350/mo; PowerMetrics from $60/mo**, scales by metric volume
- Embedding supported; geared to agencies showing client KPIs, not deep SaaS embed

## BI tools with embed offerings (the per-viewer-pricing trap zone)

### Looker (Embedded)
- **Base platform ~$60K/yr; viewers ~$400/yr each; developers ~$1,665/yr**
- **Total typical analytics spend for real embedded deployment $200K-$300K+ annually**
- **Out of scope** for 4-6 engagement consulting

### Power BI Embedded
- **Now via Microsoft Fabric F-SKUs, starting F2 at $262/mo PAYG (~$156/mo reserved)** [per azure.microsoft.com/pricing](https://azure.microsoft.com/en-us/pricing/details/power-bi-embedded/) (verify before quoting)
- **App-Owns-Data:** end users do NOT need individual licenses — capacity covers them
- **But report builders need Power BI Pro at $14/mo each** (raised from $10 in April 2025)
- **Brand-familiarity win** for Microsoft-stack clients

### Tableau Embedded (Salesforce)
- **Custom-quoted; reportedly $60K-$150K/yr year-1 floor**; per-viewer ~$420/yr
- Now lives under "Tableau Next" Salesforce bundle (2026)
- **Out of scope** for SMB consulting

### Metabase
- **OSS (AGPL v3) Static Embedding:** free with "Powered by Metabase" badge ✅ **Verified 2026-05-21.**
- **Pro Interactive Embedding:** **$575/mo base + $12/user/month**; 10 users included ✅ **Verified 2026-05-21.**
- **AGPL implication:** modify and serve = must publish modifications. Most SaaS teams take commercial license.
- **Math at 50 viewers across 6 clients:** ~$74k/yr. **Don't default for SMB consulting.**

### Apache Superset / Preset
- **Superset OSS Apache 2.0, fully free, including embedded SDK** [per github.com/apache/superset](https://github.com/apache/superset)
- **Embed pattern:** server issues guest token with RLS rules → frontend loads via iframe SDK
- Used in production by Airbnb, Dropbox, Netflix
- Operational cost is real — requires Docker/Kubernetes engineering
- **Preset Cloud** managed-Superset adds $500/mo for 50 Embedded Dashboard Viewer Licenses (don't need Preset user accounts — important for B2C-ish loads)

### Mode Analytics
- **Acquired by ThoughtSpot July 2023 for $200M; folded into ThoughtSpot Analyst Studio early 2025.**
- **Mode no longer exists as a standalone product. Don't plan on it.**

### Looker Studio (free Google product)
- **Free** for the base product; **Looker Studio Pro $9/user/project/month annual**
- Embed is iframe-only; "powered by Looker Studio" feel
- OK for marketing site if the firm is fine with the branding

## Code-first / lightweight

### Evidence.dev
- **OSS MIT-licensed**, fully free for self-host
- **Cloud (verified 2026-05-21):** **NO free tier**; Team $15/user/mo, Pro $25/user/mo, **Embedded is Enterprise-tier only**
- **Build dashboards by writing Markdown with embedded SQL** — Git-versioned, static-deployable
- **Strong candidate for Case A (ravenpower.net portfolio) on OSS, NOT the Cloud product**

### Streamlit
- **Snowflake acquired in March 2022**
- **Streamlit-in-Snowflake docs explicitly position it for internal tools, NOT for high-concurrency public-facing apps**
- **Don't use for customer-facing dashboards.** Internal portals, analyst tools, demos — fine.

### Quarto dashboards
- Open source. Author in `.qmd`, render to static HTML or Shiny-backed interactive
- For interactivity needs Shiny Server / shinyapps.io / Posit Connect (operational weight)

## Multi-tenancy + auth patterns

See [`multi-tenant-rls-patterns.md`](multi-tenant-rls-patterns.md) for the closeness-to-data invariant and stack-specific enforcement patterns.

**2026 standard for customer-facing embeds:**
- Host app issues short-lived JWT (5-15 min) with `tenant_id` claim
- Embed verifies signature, enforces scope at query time
- Postgres RLS for raw-Postgres-backed (Metabase/Superset against DB)
- Semantic-layer enforcement for Cube (`securityContext`), Power BI (DAX roles), Fabric (workspace roles)
- App-code filters are NEVER the load-bearing control on viewer-facing read paths

See [`jwt-embed-issuance.md`](../skills/jwt-embed-issuance/SKILL.md) for the JWT flow, [`rls-policy-authoring.md`](../skills/rls-policy-authoring/SKILL.md) for the enforcement layer.

## Performance reference

- **D3 + SVG:** ~1,000 elements comfortable; degrades above
- **Canvas (Chart.js, ECharts):** ~10,000 elements at 60fps
- **WebGL:** 50,000+ data points at 58fps
- **DuckDB-WASM in browser:** 10M-row aggregations in ~1.8s, complex joins ~3.5s on a 1.5 GB Parquet (real practitioner reports). Real production gotchas around CSP / web-worker loading / Vite vs Webpack bundling.

**Practical heuristic:** pre-aggregate in a semantic layer (Cube) or warehouse — humans don't read 100k points.

## Stripe / Shopify / Mixpanel — patterns to learn from

- **Stripe Dashboard:** built on Apache Pinot, **p99 70ms / 10K+ QPS / 3PB clusters**. Real-time, columnar OLAP behind a React UI. Architectural ideal for high-tenancy / low-latency.
- **Shopify Analytics:** single-store/single-currency assumptions documented as a known limitation at scale
- **Mixpanel:** "Bookmarks" as first-class named resources (saved Insights/Funnels/Retention/Flows). Clean "headless analytics API + thin UI" pattern.

## Recommended stack per use case

| Use case | Stack | Year-1 cost |
|---|---|---|
| Portfolio (Case A) | Evidence.dev OSS → Vercel/Netlify | $0 |
| Client deliverable (Case B) | Apache Superset OR Metabase OSS self-hosted, JWT-embedded | $480/yr + dev time |
| Case B M365 alt | Power BI Embedded F2 reserved | ~$3,330/yr (Pro + capacity) |
| Productized SaaS (Case C) | Cube OSS + Next.js + Tremor + Recharts + Postgres RLS | $0 license + Postgres/Cube Cloud cost |
| Case C managed | Embeddable.com (sales-quoted) | $? — sales conversation |

## Refresh triggers

- New Gartner MQ or Forrester Wave for CSM/CFA platforms
- Major M&A reshaping tier 1
- Meaningful new entrant (>5% mid-market share)
- An EdTech-vertical CFA platform launches (would materially rewrite this file)
- Power BI Embedded pricing restructure (Microsoft does this annually)
- Cube / Embeddable / Sigma adds new feature that changes the stack-decision calculus
