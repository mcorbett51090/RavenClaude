# PSM Command Center — Rendering Layer Selection (2026-06-04)

> Deep research report comparing 10 rendering platforms for a single-PSM (Project / Senior Manager) operational console hitting Snowflake, with an eye toward productization into a multi-tenant SaaS.
>
> Method: 13 fanned-out web searches across official docs, comparison sites, HN, Medium analyst posts, and contrarian/critical reviews. 40+ sources triangulated. Adversarial verification on every load-bearing claim (price, limitation, lock-in). Confidence flagged inline where independent sources disagree.

---

## 1. Per-platform deep dive

Each section uses the same 10-dimension grid. Cells marked `[unverified — single source]` need a confirmation pass before being written into a procurement doc.

### 1.1 Evidence.dev — SQL + Markdown → static site

| Dimension | Finding |
|---|---|
| **Auth (single PSM)** | None required — `evidence dev` runs locally; published build is a static site behind Cloudflare/Netlify basic-auth or an IdP proxy. Ideal for one user. |
| **Auth (multi-tenant)** | Evidence **Pro** (self-serve tier) adds SSO + SCIM ([Evidence blog — Studio launch](https://evidence.dev/blog/evidence-studio)). Native row-level multi-tenancy is **not** first-class; you per-build a site per tenant or use parameterized pages with token-gated routes. |
| **Snowflake integration** | First-class native connector; SQL queries run at build time against Snowflake and bake into the static site (so the public site never holds warehouse creds). |
| **Drill-down** | Parameterized pages + `<DataTable link=…>` components. Works well for hierarchical drill (account → project → PSM → task). Not as fluid as Hex/Sigma. |
| **Filter persistence + URL** | URL-state for input components is supported; query params persist filters across reloads. |
| **Time-to-first-dashboard** | **2–4 hours** for a competent SQL engineer. Lowest in this set alongside Metabase. |
| **TCO (single PSM)** | Open source + local build = **$0** infra, plus negligible static hosting (<$5/mo on Cloudflare Pages). Evidence Cloud is being sunset; Evidence **Studio** replaces it ([Evidence blog](https://evidence.dev/blog/evidence-studio)). Pro tier pricing not public — `[unverified]`. |
| **Codex-buildability** | **Very high.** SQL + Markdown + a small component vocabulary (`<BarChart>`, `<LineChart>`, `<Value>`) is exactly what LLMs are best at. The Streamlit Agent-Skills pattern ([streamlit/agent-skills](https://github.com/streamlit/agent-skills)) is the cautionary tale — without a constrained component list, agents hallucinate APIs. Evidence's small surface area helps. |
| **Mobile responsive** | Yes — built-in responsive grid, theme presets. |
| **Real-time-ish (10-min)** | **Awkward.** Static-site model means rebuild → redeploy. 10-min refresh = scheduled build every 10 min, which is workable but wasteful. Better fit: hourly. |
| **Lock-in risks** | **Low.** Source is SQL + Markdown — both trivially portable. Worst case: rewrite component invocations against another renderer. |
| **Sources** | [Evidence official site](https://evidence.dev/) · [Code-based BI tools comparison (Evidence's own blog)](https://evidence.dev/blog/business-intelligence-tools) · [HN discussion — 2023](https://news.ycombinator.com/item?id=35645464) · [BuildPilot comparison](https://trybuildpilot.com/677-evidence-vs-metabase-vs-apache-superset-2026) · [Holistics open-source BI guide](https://www.holistics.io/blog/best-open-source-bi-tools/) |

---

### 1.2 Apache Superset (+ Preset managed)

| Dimension | Finding |
|---|---|
| **Auth (single PSM)** | Local username/password works. For one user, both self-hosted and **Preset Free (5 users)** are valid. |
| **Auth (multi-tenant)** | **First-class.** Embedded SDK + `/api/v1/security/guest_token/` produces JWTs that carry per-tenant RLS rules and dashboard scopes ([Superset Embedded SDK docs](https://superset.apache.org/user-docs/using-superset/embedding/), [Sameer Hussain Medium](https://medium.com/@sameerhussain230/building-secure-role-based-embedded-dashboards-with-apache-superset-fastapi-and-react-3798ed7f8651)). Token TTL default 5 min; refresh required. |
| **Snowflake integration** | Native connector. **3× more connectors than Metabase** ([Preset blog](https://preset.io/blog/superset-vs-metabase/)). |
| **Drill-down** | Cross-filtering + jump-to-dashboard since v3. Not as natural as Sigma. |
| **Filter persistence + URL** | Yes — filter sets serialize to URL. |
| **Time-to-first-dashboard** | **30–60 min** if you know what you're doing ([elest.io guide](https://blog.elest.io/apache-superset-vs-metabase-vs-redash-which-open-source-bi-tool-to-self-host-in-2026/)). Semantic-layer setup adds cost before non-technical users can self-serve. |
| **TCO (single PSM)** | **Self-host:** Postgres + Redis + web + worker + beat ≈ 5 processes; $30–60/mo on a single VM, plus your time. **Preset Free:** $0 forever for 5 users. **Preset Pro:** $20/user flat (cheaper than Metabase Pro under ~50 users). |
| **Codex-buildability** | **Medium.** Dashboards are config (YAML/JSON) — agent-friendly. Chart-as-code via `superset-ui` plugins is less so. Agents go wrong on: Jinja templating in SQL, RLS-via-guest-token wiring, and `superset.yaml` import format drift across versions. |
| **Mobile responsive** | Partial — desktop-first, dashboards reflow but many chart types degrade. |
| **Real-time-ish (10-min)** | Yes — dashboard refresh interval is configurable to 10 s; underlying queries hit Snowflake live (so cost-control via caching matters). |
| **Lock-in risks** | **Low** if self-hosted (Apache 2.0). **Medium** with Preset (their managed control plane / governance UI isn't OSS). |
| **Sources** | [Preset's Superset-vs-Metabase post](https://preset.io/blog/superset-vs-metabase/) · [elest.io 2026 OSS BI comparison](https://blog.elest.io/apache-superset-vs-metabase-vs-redash-which-open-source-bi-tool-to-self-host-in-2026/) · [Valiotti 2026 buyer's guide](https://valiotti.com/apache-superset-2026-guide/) (critical view: 5-process operational surface) · [Embedded SDK npm](https://www.npmjs.com/package/@superset-ui/embedded-sdk) · [Guest-token discussion #29824](https://github.com/apache/superset/discussions/29824) · [MeghGen production guide](https://medium.com/meghgen/fast-secure-embedded-running-apache-superset-in-production-the-right-way-67f3db643c53) |

---

### 1.3 Metabase

| Dimension | Finding |
|---|---|
| **Auth (single PSM)** | Local accounts, magic-link, or OSS-tier Google OAuth. Easiest single-user story in the set. |
| **Auth (multi-tenant)** | **Cloud Pro+** ($575/mo, ≤10 users) adds **Data Sandboxing** — column- and row-level permissions, one-DB-per-tenant native ([Metabase pricing](https://www.metabase.com/pricing/), [Coefficient breakdown](https://coefficient.io/metabase-pricing)). Previously a "weeks of custom RLS" task, now built-in. |
| **Snowflake integration** | Native; supported, well-trodden path. Connector count smaller than Superset but covers the majors. |
| **Drill-down** | Excellent automatic drill-through on visualizations (the "X-ray" feature). Best-in-class for non-technical drill. |
| **Filter persistence + URL** | Yes — dashboard filters serialize. |
| **Time-to-first-dashboard** | **1–3 hours.** GUI-first means a SQL engineer can stand up a useful dashboard fastest of any tool here, especially if they're not yet comfortable in the platform. |
| **TCO (single PSM)** | **OSS self-host:** $0 license, **$15–20K/yr hidden cost** for hosting + ops ([Coefficient](https://coefficient.io/metabase-pricing)). **Cloud Starter:** $100/mo (5 users). **Cloud Pro:** $575/mo (10 users). **Enterprise:** median $39K/yr (Vendr). |
| **Codex-buildability** | **Medium-low for dashboards-as-code** (Metabase dashboards aren't natively code; serialization API exists but is fragile). **High for SQL questions** — agents can author Saved Questions via API. |
| **Mobile responsive** | Yes — official mobile app + responsive web dashboards. |
| **Real-time-ish (10-min)** | Yes — dashboard auto-refresh down to 1 min. |
| **Lock-in risks** | **Low** for OSS (AGPL), **Medium** for Pro/Enterprise feature gating (Sandboxing, SSO, audit are paid-only). AGPL licensing has copyleft implications if you embed and modify. |
| **Sources** | [Metabase pricing (official)](https://www.metabase.com/pricing/) · [Coefficient 2026 pricing analysis](https://coefficient.io/metabase-pricing) · [CheckThat.ai TCO](https://checkthat.ai/brands/metabase/pricing) · [Metabase cloud-vs-self-host docs](https://www.metabase.com/docs/latest/cloud/cloud-vs-self-hosting) · [Metabase vs Definite (critical: hidden ops cost)](https://www.definite.app/blog/metabase-vs-definite) · [Vendr median Enterprise contract](https://www.vendr.com/marketplace/metabase) |

---

### 1.4 Hex

| Dimension | Finding |
|---|---|
| **Auth (single PSM)** | Community tier free; password / Google login. |
| **Auth (multi-tenant)** | Enterprise tier supports SSO, single-tenant deployment, and EU multi-tenant region. Multi-tenancy is workspace-level, not row-level out of the box — RLS via Snowflake roles + Snowpark OAuth passthrough. |
| **Snowflake integration** | **Deep.** OAuth + key-pair connections; Snowpark / Cortex callable inline; purchasable via Snowflake Marketplace using Snowflake credits ([Hex × Snowflake](https://hex.tech/product/integrations/snowflake/)). |
| **Drill-down** | Notebook + app dual-view; drill-throughs via input parameters; not as fluid as Sigma but better than Streamlit. |
| **Filter persistence + URL** | Yes — input components are URL-bound. |
| **Time-to-first-dashboard** | **2–6 hours** for a SQL engineer (notebook idiom slows the first dashboard, accelerates the 10th). |
| **TCO (single PSM)** | **Community = $0** for one user (Hex's free tier is the most-generous of the commercial set). Team Creator seats **$149–$199/user/mo** ([Hex pricing](https://hex.tech/pricing/) via comparison sources). Enterprise = custom. |
| **Codex-buildability** | **Low-medium.** Hex projects are proprietary JSON; agents can't easily "write a Hex app from a spec." API exists but is partial. Magic AI features live inside the product, not at the codegen layer. |
| **Mobile responsive** | Partial — viewable on mobile, not designed for it. |
| **Real-time-ish (10-min)** | Yes — scheduled runs + live SQL. |
| **Lock-in risks** | **High.** Project format is proprietary; export-to-static is limited. Migrating off Hex = rewrite. |
| **Sources** | [Hex × Snowflake](https://hex.tech/product/integrations/snowflake/) · [Hex pricing](https://hex.tech/pricing/) (403 to direct fetch; specs from comparison sources) · [Vendr Hex marketplace](https://www.vendr.com/marketplace/hex-technologies) · [Fabi.ai — Hex alternatives (critical view)](https://www.fabi.ai/blog/best-alternatives-to-hex) · [PowerDrill — 12 Hex alternatives 2026](https://powerdrill.ai/blog/best-hex-alternatives-for-data-analysis) |

---

### 1.5 Streamlit (incl. Streamlit-in-Snowflake / SiS)

| Dimension | Finding |
|---|---|
| **Auth (single PSM)** | OSS: none; you wrap with `streamlit-authenticator` or an OIDC proxy. **SiS:** uses Snowflake's RBAC — your PSM is already authenticated as a Snowflake user. **Cleanest single-PSM auth in the set if Snowflake login is acceptable.** |
| **Auth (multi-tenant)** | OSS: app-level + reverse proxy. **SiS:** Snowflake roles → owner-execution model means **the app runs as the owner's identity, not the caller's** — this is the "governance pitfall" called out by Ignatius Soputro's Feb 2026 SiS review ([Medium](https://medium.com/towards-data-engineering/evaluating-streamlit-in-snowflake-sis-c4f466cff179)). For true multi-tenant you need caller-rights setup or one-app-per-tenant. |
| **Snowflake integration** | **Maximum.** SiS runs **inside** Snowflake — no egress, no warehouse-creds-in-app, packages from Snowflake Anaconda channel (warehouse runtime) or PyPI via External Access Integration (container runtime). |
| **Drill-down** | Manual — you build it with `st.selectbox` / `st.button` → re-render. Re-runs from top on every interaction (unless you use `st.fragment`). |
| **Filter persistence + URL** | `st.query_params` since 1.30 — works but you wire it yourself. |
| **Time-to-first-dashboard** | **3–8 hours.** Python is more verbose than Evidence's SQL+Markdown, but the iteration loop is fast. |
| **TCO (single PSM)** | **OSS:** $0 + Streamlit Community Cloud free tier. **SiS:** included in Snowflake bill; runs on serverless warehouse (small XS warehouse + storage). The killer feature for single-PSM cost: no separate hosting. |
| **Codex-buildability** | **Highest in this set.** Streamlit's `streamlit/agent-skills` repo specifically targets Claude Code / Cursor / Codex / Copilot, and the docs explicitly note that **without** Agent Skills, agents hallucinate APIs but **with** them work in a single shot ([streamlit/agent-skills](https://github.com/streamlit/agent-skills), [Streamlit blog — vibe code with AGENTS.md](https://blog.streamlit.io/vibe-code-streamlit-apps-with-ai-using-agents-md-04b7480f754e)). |
| **Mobile responsive** | **Weak.** Documented limitation: columns don't reflow until near-phone widths; tables overflow ([Issue #6592](https://github.com/streamlit/streamlit/issues/6592), [DigitalDefynd pros/cons](https://digitaldefynd.com/IQ/pros-cons-of-streamlit/)). For a PSM on mobile this is a real concern. |
| **Real-time-ish (10-min)** | Yes — `st.cache_data(ttl=600)` plus auto-rerun; or scheduled refresh. SiS runs serverless. |
| **Lock-in risks** | **Low for OSS** (Apache 2.0). **Medium-high for SiS:** code is in Snowflake stages, packages constrained to Snowflake Anaconda channel in warehouse runtime, 32 MB single-command output cap ([Snowflake docs — SiS limitations](https://docs.snowflake.com/en/developer-guide/streamlit/limitations)). Moving off SiS = repackage + re-host. |
| **Sources** | [Streamlit-in-Snowflake official](https://www.snowflake.com/en/product/features/streamlit-in-snowflake/) · [SiS limitations doc](https://docs.snowflake.com/en/developer-guide/streamlit/limitations) · [Soputro — SiS Good/Bad/Ugly Feb 2026](https://medium.com/towards-data-engineering/evaluating-streamlit-in-snowflake-sis-c4f466cff179) · [GitLab — structured SiS framework](https://about.gitlab.com/blog/how-we-built-a-structured-streamlit-application-framework-in-snowflake/) · [streamlit/agent-skills (Codex-buildability)](https://github.com/streamlit/agent-skills) · [Streamlit responsive limitation #6592](https://github.com/streamlit/streamlit/issues/6592) · [DigitalDefynd pros/cons](https://digitaldefynd.com/IQ/pros-cons-of-streamlit/) |

---

### 1.6 Plain React + Tremor + Recharts + Cube

| Dimension | Finding |
|---|---|
| **Auth (single PSM)** | Whatever you wire — Auth0, Clerk, NextAuth, or just basic-auth. No constraints. |
| **Auth (multi-tenant)** | Whatever you wire — typically JWT with `tenant_id` claim → Cube `securityContext` → query-time RLS injection ([Querio — multi-tenant embedded](https://querio.ai/articles/multi-tenant-embedded-analytics-architecture)). The textbook multi-tenant pattern. |
| **Snowflake integration** | **Via Cube as semantic layer** — Cube speaks Snowflake natively, materializes pre-aggregations, and exposes REST/GraphQL/SQL APIs. React queries Cube, never Snowflake directly ([Cube case study — 2× Snowflake cost reduction](https://cube.dev/case-studies/faster-performance-and-a-2x-reduction-in-snowflake-cost)). |
| **Drill-down** | Bespoke — whatever you build. Best ceiling, worst floor. |
| **Filter persistence + URL** | Bespoke — Next.js `searchParams` or React Router state. |
| **Time-to-first-dashboard** | **2–10 days.** Highest by an order of magnitude. |
| **TCO (single PSM)** | **Highest engineering cost, lowest license cost.** Cube OSS = $0 (Apache 2.0). Cube Cloud = consumption-based starting $0 ([Cube pricing](https://cube.dev/pricing)). Hosting = ~$20/mo on Vercel. Tremor and Recharts are free (Vercel acquired Tremor — actively maintained, [Tremor GitHub](https://github.com/tremorlabs/tremor)). **Real cost = engineering weeks**, which dominates for a single-PSM ROI. |
| **Codex-buildability** | **High for the React + Tremor layer** — agents are very good at "stitch this Tremor component to this Cube query." **Medium for the Cube schema** — agents reliably miss join cardinality and pre-aggregation tuning. |
| **Mobile responsive** | **Excellent** — Tremor is Tailwind-based, mobile-first by default. |
| **Real-time-ish (10-min)** | Yes — Cube's pre-aggregations refresh on schedule; React polls or streams. |
| **Lock-in risks** | **Lowest** — every layer is OSS and swappable. Tremor → shadcn/ui, Recharts → Tremor's own charts or visx, Cube → dbt Semantic Layer. |
| **Sources** | [Cube official](https://cube.dev/) · [Cube pricing](https://cube.dev/pricing) · [Cube + Recharts dashboard guide](https://cube.dev/blog/building-a-recharts-dashboard-with-cube) · [Cube Snowflake cost case study](https://cube.dev/case-studies/faster-performance-and-a-2x-reduction-in-snowflake-cost) · [Tremor (Vercel-acquired)](https://www.tremor.so/) · [Tremor GitHub](https://github.com/tremorlabs/tremor) · [Querio multi-tenant architecture](https://querio.ai/articles/multi-tenant-embedded-analytics-architecture) |

---

### 1.7 Looker (Google embedded BI)

| Dimension | Finding |
|---|---|
| **Auth (single PSM)** | Looker accounts (Google OAuth). Heavyweight for one user. |
| **Auth (multi-tenant)** | **Signed embedding** — HMAC-signed URLs carry `user_attributes` (incl. `tenant_id`) and the LookML model uses them in `sql_always_where:` clauses ([Looker signed-embedding docs](https://cloud.google.com/looker/docs/signed-embedding)). Must be explicitly enabled by a Google Cloud sales rep on Original Looker instances. |
| **Snowflake integration** | Native. LookML compiles to Snowflake SQL. |
| **Drill-down** | First-class — drill fields, links, jump-to-dashboard all native in LookML. |
| **Filter persistence + URL** | Yes — Look URLs encode every filter. |
| **Time-to-first-dashboard** | **3–5 days** for a SQL engineer who's never seen LookML. LookML is a separate skill set from SQL ([Analytify alternatives](https://analytify.ai/looker-alternatives/)). |
| **TCO (single PSM)** | **Wildly disproportionate.** Standard plan **$35K–$60K/yr** for 10 standard + 2 dev users ([Luzmo](https://www.luzmo.com/blog/looker-pricing), [Toucan Toco](https://www.toucantoco.com/en/blog/looker-pricing)). Enterprise averages **$150K/yr**. One reviewer quoted $35K base hit ~$100K with usage ([Modern DataTools](https://www.modern-datatools.com/tools/looker/pricing)). **Embedded viewers ~$400/yr each** — destroys SaaS unit economics ([Analytify](https://analytify.ai/looker-alternatives/)). |
| **Codex-buildability** | **Low.** LookML is a DSL with strict semantics agents partially know; mistakes silently produce wrong numbers (worst failure mode). |
| **Mobile responsive** | Yes — Looker dashboards have mobile layouts; mobile app exists. |
| **Real-time-ish (10-min)** | Yes — schedule + live query. |
| **Lock-in risks** | **Highest in this set.** LookML is non-portable. Google Cloud dependency. Pricing power asymmetric (recent contrarian: Omni Analytics was founded by ex-Looker engineers explicitly to build "what Looker should have been," raised $69M Series B in Mar 2025). |
| **Sources** | [Looker signed embedding (official)](https://cloud.google.com/looker/docs/signed-embedding) · [Luzmo Looker pricing](https://www.luzmo.com/blog/looker-pricing) · [Toucan Toco Looker pricing](https://www.toucantoco.com/en/blog/looker-pricing) · [Modern DataTools enterprise breakdown](https://www.modern-datatools.com/tools/looker/pricing) · [Analytify alternatives (critical: LookML lock-in, $400/viewer)](https://analytify.ai/looker-alternatives/) · [Qrvey embedded review](https://qrvey.com/blog/looker-embedded-analytics/) · [Astrato competitors](https://www.astrato.io/blog/looker-competitors) |

---

### 1.8 Sigma Computing

| Dimension | Finding |
|---|---|
| **Auth (single PSM)** | Sigma account; SSO available. |
| **Auth (multi-tenant)** | Embedded analytics with secure-embed signed URLs; RLS via Sigma's row-access controls **or** Snowflake roles ([Sigma RLS docs](https://help.sigmacomputing.com/docs/restrict-access-to-data-in-embedded-content), [phData implementation post](https://www.phdata.io/blog/implementing-row-level-security-in-embedded-sigma-dashboards-with-schema-isolation/), [Snowflake + Sigma quickstart](https://www.snowflake.com/en/developers/guides/snowflake-build-secure-multitenant-data-applications-snowflake-sigma/)). |
| **Snowflake integration** | **Native, live-query.** No extract layer — every interaction hits Snowflake. |
| **Drill-down** | **Best in class** — spreadsheet idiom means drilling is "double-click on cell." Designed for the business analyst. |
| **Filter persistence + URL** | Yes — workbook state in URL. |
| **Time-to-first-dashboard** | **1–4 hours** for someone who thinks in Excel. SQL engineers need to unlearn habits. |
| **TCO (single PSM)** | **Misaligned with single-PSM economics.** Starts $300/mo; SMB average $56K/yr; Enterprise $230K/yr ([CheckThat.ai](https://checkthat.ai/brands/sigma-computing/pricing)). PeerSpot user: **$30K platform fee + $1K/Creator** ([reported via Knowi review](https://www.knowi.com/blog/the-ultimate-sigma-review-pros-cons-and-who-it-is-for/)). |
| **Codex-buildability** | **Low.** Workbooks are GUI-built; no code surface for agents to target. |
| **Mobile responsive** | Yes. |
| **Real-time-ish (10-min)** | Live by default — every filter is a Snowflake query, which is a **double-edged sword**. |
| **Lock-in risks** | **High** — workbook format proprietary. **Hidden Snowflake cost lock-in** is the recurring critique: every filter spikes the warehouse bill ([Lokad review](https://www.lokad.com/review-of-sigmacomputing-com/), [Index.app review](https://index.app/blog/sigma-computing-reviews-pricing-alternatives)). |
| **Sources** | [Sigma official](https://www.sigmacomputing.com/) · [Sigma RLS docs](https://help.sigmacomputing.com/docs/restrict-access-to-data-in-embedded-content) · [Snowflake + Sigma multi-tenant quickstart](https://www.snowflake.com/en/developers/guides/snowflake-build-secure-multitenant-data-applications-snowflake-sigma/) · [phData RLS implementation](https://www.phdata.io/blog/implementing-row-level-security-in-embedded-sigma-dashboards-with-schema-isolation/) · [G2 reviews](https://www.g2.com/products/sigma-computing-sigma/reviews) · [Lokad critical review](https://www.lokad.com/review-of-sigmacomputing-com/) · [Knowi pros/cons](https://www.knowi.com/blog/the-ultimate-sigma-review-pros-cons-and-who-it-is-for/) · [CheckThat.ai TCO](https://checkthat.ai/brands/sigma-computing/pricing) |

---

### 1.9 Mode Analytics (ThoughtSpot Analyst Studio)

| Dimension | Finding |
|---|---|
| **Status** | **Mode no longer exists as a standalone product.** Absorbed into ThoughtSpot's **Analyst Studio**, GA early 2025 ([ThoughtSpot blog](https://www.thoughtspot.com/blog/thoughtspot-acquires-mode), [5000fish Medium](https://medium.com/@5000fish/mode-analytics-was-acquired-by-thoughtspot-best-mode-alternatives-in-2026-6f02c83fe0e3)). Selection question becomes "do you want ThoughtSpot?" |
| **Auth (single PSM)** | ThoughtSpot accounts; SSO. |
| **Auth (multi-tenant)** | ThoughtSpot Everywhere (embedded tier) — signed JWTs, per-tenant RLS via ThoughtSpot worksheets. |
| **Snowflake integration** | Native. Mode's SQL Workbench + Python/R notebooks remain in Analyst Studio. |
| **Drill-down** | ThoughtSpot's "search-driven" UX is the differentiator; Mode's notebook surface added code-first depth. |
| **Filter persistence + URL** | Yes. |
| **Time-to-first-dashboard** | **2–4 hours** for a SQL engineer in Analyst Studio. |
| **TCO (single PSM)** | **Enterprise pricing.** Essentials $25/user, Pro $50/user, Enterprise custom & "typically six figures" ([Luzmo on ThoughtSpot](https://www.luzmo.com/blog/thoughtspot-pricing)). Wrong shape for a single-PSM rollout. |
| **Codex-buildability** | **Low.** Workbook + worksheet semantics aren't well-represented in training data; agents perform poorly. |
| **Mobile responsive** | Yes. |
| **Real-time-ish (10-min)** | Yes. |
| **Lock-in risks** | **High** + **acquisition risk realized once already** — buyers should weigh the precedent. |
| **Sources** | [ThoughtSpot acquires Mode (press)](https://www.thoughtspot.com/press-releases/thoughtspot-acquires-mode-analytics-for-200m) · [Acquisition completion press](https://www.thoughtspot.com/press-releases/thoughtspot-completes-200m-acquisition-of-mode-analytics) · [TechCrunch coverage](https://techcrunch.com/2023/06/26/thoughtspot-acquires-mode-analytics-a-bi-platform-for-200m-in-cash-and-stock/) · [Diginomica analysis](https://diginomica.com/thoughtspots-200m-mode-analytics-acquisition-step-one-being-massive-says-ceo) · [5000fish Mode alternatives 2026 (critical)](https://medium.com/@5000fish/mode-analytics-was-acquired-by-thoughtspot-best-mode-alternatives-in-2026-6f02c83fe0e3) · [DashboardFox alternatives](https://dashboardfox.com/blog/mode-analytics-alternatives/) · [Luzmo ThoughtSpot pricing](https://www.luzmo.com/blog/thoughtspot-pricing) |

---

### 1.10 Observable Framework

| Dimension | Finding |
|---|---|
| **Auth (single PSM)** | Static-site auth (Cloudflare Access, basic-auth, IdP proxy). No built-in. |
| **Auth (multi-tenant)** | **No native multi-tenant.** Data is baked at build time and shipped to client — fundamentally a publishing tool. Multi-tenant = build-per-tenant + scoped hosting. |
| **Snowflake integration** | Via **data loaders** — any language can run `snowsql` / SDK at build, output to JSON/Parquet ([Data loaders docs](https://observablehq.observablehq.cloud/framework/data-loaders)). |
| **Drill-down** | Yes via parameterized routes + client JS, but you wire it. |
| **Filter persistence + URL** | Yes — but bespoke. |
| **Time-to-first-dashboard** | **1–3 days.** JS comfort required; lower-level than Evidence. |
| **TCO (single PSM)** | **$0** OSS + ~$5/mo static hosting. Observable Cloud / scheduled-build add-on optional. |
| **Codex-buildability** | **High for layout/chart code** (D3/Plot + JS is well-represented in training), **medium for data-loader plumbing**. |
| **Mobile responsive** | Yes — author-controlled, but defaults are good. |
| **Real-time-ish (10-min)** | **Awkward — same as Evidence.** Scheduled rebuilds. Not designed for sub-hour. |
| **Lock-in risks** | **Lowest.** Output is HTML + JS + data files. Reverse-engineering is trivial. |
| **Sources** | [Framework GitHub](https://github.com/observablehq/framework) · [Framework data loaders](https://observablehq.observablehq.cloud/framework/data-loaders) · [Simon Willison — interesting ideas in Framework](https://simonwillison.net/2024/Mar/3/interesting-ideas-in-observable-framework/) · [Appsilon big-scale dashboards](https://www.appsilon.com/post/observable-framework-data-science-dashboards) · [MakerStack 2026 review](https://makerstack.co/reviews/observable-review/) · [OSACON 2024 session](https://osacon.io/sessions/2024/observable-framework-a-new-open-source-static-site-generator-to-get-data-past-the-last-mile/) · Contrarian: [HN Starboard discussion](https://news.ycombinator.com/item?id=26857888) — concerns about ObservableHQ dependency for cloud features. |

---

## 2. Decision tree — which platform when?

```mermaid
flowchart TD
    Start([Need to render a Snowflake-backed console]) --> Q1{Is it 1 user / today<br/>or productizing?}

    Q1 -- "Today, 1 PSM" --> Q2{Sub-hour refresh needed?}
    Q1 -- "Future SaaS, N tenants" --> Q3{Hard auth + RLS<br/>required from day 1?}

    Q2 -- "No: hourly is fine" --> EvidenceA[Evidence.dev<br/>2-4h, $0, lowest lock-in]
    Q2 -- "Yes: 10-min" --> Q4{SQL engineer or Python engineer?}

    Q4 -- "SQL" --> Metabase[Metabase OSS<br/>1-3h, Cloud $100/mo]
    Q4 -- "Python" --> SiS[Streamlit-in-Snowflake<br/>3-8h, billed via Snowflake]

    Q3 -- "Yes, must ship now" --> Q5{Budget?}
    Q3 -- "Yes, but can engineer it" --> Cube[React + Tremor + Cube<br/>2-10d, lowest lock-in, mobile-first]

    Q5 -- "$575+/mo OK" --> MetabasePro[Metabase Pro<br/>Data Sandboxing native]
    Q5 -- "Sub-$100/mo, OSS-comfort" --> Superset[Apache Superset<br/>+ Embedded SDK + guest tokens]
    Q5 -- "$35K+/yr, enterprise" --> Sigma[Sigma or Looker<br/>watch Snowflake bill]

    Cube --> MobileBest{Mobile-first PSM?}
    MobileBest -- "Yes" --> CubeFinal[Stay with React+Tremor]
    MobileBest -- "No" --> Reconsider[Reconsider: Superset or Metabase Pro<br/>shorter time-to-market]

    classDef chosen fill:#1f7a3a,stroke:#0a3,color:#fff
    classDef avoid fill:#7a1f1f,stroke:#a00,color:#fff
    class EvidenceA,Cube chosen
    class Sigma avoid
```

---

## 3. Cost model side-by-side

Assumptions: Snowflake cost held constant (call it $X/mo independent of rendering layer), 1 user reads daily, ~50 dashboards, refresh every 10 min during business hours.

| Platform | **Single PSM** | **10-tenant SaaS** | **100-tenant SaaS** |
|---|---|---|---|
| Evidence.dev (OSS + Cloudflare Pages) | **$0–$5/mo** | $50/mo (per-tenant builds) + Pro tier for SSO `[unverified pricing]` | Per-tenant builds become operationally heavy; switch to dynamic renderer |
| Apache Superset (self-host) | **$30–60/mo VM** + your time | $30–60/mo VM + Embedded SDK wiring | $200–400/mo larger cluster + worker scale-out |
| Preset (managed Superset) | **Free tier (5 users)** | **$20/user flat ≈ $200/mo** | $20/user ≈ $2K/mo + Enterprise quote |
| Metabase OSS (self-host) | **$30/mo VM** + $15–20K/yr hidden ops | $30/mo VM, but no Sandboxing without Pro | Sandboxing requires Pro |
| Metabase Cloud Starter | **$100/mo** (5 users) | Not multi-tenant — skip | — |
| Metabase Cloud Pro | $575/mo (10 users) | **$575/mo with Sandboxing** (sweet spot) | Enterprise: ~$39K/yr median (Vendr) |
| Hex Community | **$0** for 1 user | Not multi-tenant; need Team/Enterprise | Enterprise quote |
| Hex Team | $149–199/Creator/mo | $1.5K–2K/mo per Creator | Enterprise contract |
| Streamlit OSS + Community Cloud | **$0** | Community Cloud doesn't multi-tenant; need self-host | Self-host on K8s + auth proxy |
| Streamlit-in-Snowflake | **Snowflake bill only** (~$50–200/mo for XS warehouse) | Same — scales with Snowflake credits | Same; per-tenant role isolation needed |
| React + Tremor + Cube OSS | **$20/mo Vercel** + engineering weeks | $20/mo + Cube self-host | Cube Cloud or beefier self-host |
| Looker Original | **$35–60K/yr** (way over-built for 1 user) | $35–60K/yr | $150K/yr+ enterprise |
| Sigma Computing | **$300/mo+** plus Snowflake spike from live queries | $56K/yr SMB avg | $230K/yr Enterprise avg |
| Mode / ThoughtSpot Analyst Studio | Enterprise pricing — unsuitable single-PSM | $50/user Pro tier | Six-figure annual |
| Observable Framework (OSS) | **$5/mo** static hosting | Per-tenant builds — same scaling problem as Evidence | Switch to dynamic renderer |

**Headline:** for a single PSM, the under-$10/mo tier is real (Evidence, Observable, SiS, OSS Streamlit, OSS Metabase, OSS Superset). The decision is engineering-time and lock-in, not license.

---

## 4. Codex-buildability ranking

Ranked by how reliably an autonomous coding agent (Claude / Codex / Cursor) with a spec produces a correct, runnable dashboard on the first or second iteration.

| Rank | Platform | Why | Common failure mode |
|---|---|---|---|
| 1 | **Streamlit (incl. SiS)** | First-party `streamlit/agent-skills` and `AGENTS.md` standard turn Streamlit into the canonical "AI vibe-coded BI" target ([streamlit/agent-skills](https://github.com/streamlit/agent-skills), [Streamlit blog](https://blog.streamlit.io/vibe-code-streamlit-apps-with-ai-using-agents-md-04b7480f754e)). | Without Agent Skills loaded, agents still hallucinate widget APIs across versions. |
| 2 | **Evidence.dev** | SQL + Markdown + ~30 components. Smallest correct surface area in the field. | Agents wrong about Markdown component prop names; gets corrected within 1 iteration. |
| 3 | **React + Tremor + Recharts (UI layer)** | Tailwind + React + named chart components is heavily represented in training data. | Cube schema mistakes are the real risk — agents miss join cardinality / pre-agg tuning. |
| 4 | **Observable Framework** | D3/Plot + JS + Markdown — well-represented. | Data-loader plumbing across languages is fiddly; agents skip incremental-build patterns. |
| 5 | **Superset (config + plugins)** | YAML/JSON dashboard exports; SQL Jinja; Embedded SDK has TS types. | Jinja-in-SQL and `superset.yaml` schema drift across releases. |
| 6 | **Metabase (API + SQL questions)** | API is REST; SQL is plain. Dashboards-as-code is fragile. | Serialization API undocumented edges; LLM tries to construct dashboards via UI calls. |
| 7 | **Cube (semantic schema)** | YAML/JS cube definitions are agent-friendly. | Pre-aggregations + join graph subtle — silently wrong numbers. |
| 8 | **Hex** | Project format proprietary; partial API. | Agents can't author Hex projects from scratch — only fragments via API. |
| 9 | **Looker (LookML)** | DSL with strict semantics; partially in training. | Silent numeric errors — worst failure mode. Agents over-confident. |
| 10 | **Sigma / Mode (ThoughtSpot)** | GUI-built, no meaningful code surface. | Not a sensible Codex target at all. |

---

## 5. Migration paths (Evidence v0 → Superset v1 → multi-tenant v2)

```
v0  (Today, weeks 1-2):  Evidence.dev local + Cloudflare Pages
    └─ One PSM, daily snapshot, $0 ops cost
    └─ Source of truth = Git repo of .md + .sql

v1  (Multi-user, months 1-3): Apache Superset self-hosted on Fly.io / Railway
    └─ 5-10 internal users, dashboards-as-config exported to repo
    └─ Reuse same Snowflake SQL queries (rewrite Markdown → Superset SQL Lab)
    └─ Cost: $50/mo infra + auth proxy

v2a (Internal scale-up, months 3-9):  Preset Pro or Metabase Cloud Pro
    └─ Drop the self-host overhead; gain SSO, audit, Sandboxing
    └─ Cost: $20-$575/mo depending on choice

v2b (Productize → SaaS, months 6-18):  React + Tremor + Cube
    └─ Trigger: customer-facing, hard RLS, custom branding, mobile-first
    └─ Cube schema = formalize what Evidence/Superset SQL did informally
    └─ JWT auth with tenant_id claim → Cube securityContext → row-scoped queries
    └─ Cost: engineering weeks + $20-100/mo hosting + Cube Cloud or self-host
```

**The pivot points to look for**

- "Three users want different views of the same dashboard" → time to move v0 → v1.
- "We need to embed this in a customer-facing product" → time to move v1 → v2b. Do **not** try to multi-tenant Evidence past 2-3 tenants.
- "We need audit and SSO" → v2a, not v2b.

**The migration foot-gun (well-documented):** going Superset → Looker is hard because LookML is non-portable. Going Superset → Cube is easy because both use plain SQL + a schema layer.

---

## 6. Specific recommendation for the PSM Command Center

**Recommendation: Evidence.dev for v0 → Streamlit-in-Snowflake for v0.5 if real-time-ish matters → React + Tremor + Cube for v2 SaaS.**

**Rationale:**

1. **Today's reality is one PSM.** Evidence buys you a polished, version-controlled console in 2–4 hours, costs nothing, and locks you into nothing. The SQL written here is the same SQL you'll reuse downstream.
2. **The 10-min-refresh problem is real and Evidence is awkward at it.** If sub-hour refresh is load-bearing (it is, per the spec), keep Evidence for the narrative/snapshot pages and add **Streamlit-in-Snowflake for the live operational panels**. SiS handles auth via Snowflake RBAC for free, no separate hosting, and the Codex-buildability is best-in-class — that matters because RavenClaude itself will build a lot of this.
3. **Avoid Sigma, Looker, ThoughtSpot.** All three over-fit the one-PSM case 10–100× on cost. Sigma's live-query Snowflake bill spike is the documented failure pattern.
4. **Avoid Hex.** Free tier is generous but lock-in is high and Codex-buildability is poor — both matter for a tool RavenClaude will iterate on autonomously.
5. **When/if productizing:** Cube + Tremor is the textbook multi-tenant pattern. The migration from "Evidence SQL files" to "Cube schema files" is a refactor, not a rewrite.

**Counter-arguments considered and rejected:**

- *"Superset has guest tokens and RLS today, just start there."* True, but five processes for one PSM is operational waste, and Superset's mobile experience is weaker than Tremor's. Acceptable for v1 (internal scale-up); over-built for v0.
- *"Metabase Cloud Pro at $575/mo is a one-shot answer."* It is — and it's the right answer if engineering time is the bottleneck. Pick this if the team is small and doesn't want to write Markdown components.
- *"Pure React + Cube from day 1, skip Evidence."* Tempting but wastes 1–2 weeks before any value lands. Migrating SQL files is cheap; building UI from scratch is not.

**Hedged uncertainties to verify before commit:**

- Evidence Pro pricing (the page 403'd on direct fetch; quote needed).
- SiS container-runtime limits at PSM dashboard scale (32 MB single-command cap is the documented worry).
- Whether Snowflake's authoring tier covers the SiS container runtime for the PSM's role.

---

## 7. RavenClaude knowledge file paths + sketches

Suggested durable artifacts. Paths follow the marketplace's `.repo-layout.json` allowed globs (plugin-internal knowledge stays under `plugins/<plugin>/knowledge/`).

```
plugins/ravenclaude-core/knowledge/rendering-layer/
├── decision-record.md            # ADR-style: chose Evidence + SiS + (later) Cube
├── platform-matrix.md            # the per-platform grid (Section 1 of this report)
├── codex-buildability.md         # Section 4 + dos/don'ts per platform
├── migration-paths.md            # v0 → v1 → v2 + pivot triggers
├── tco-model.md                  # Section 3 + a per-platform refresh checklist
└── snippets/
    ├── evidence-snowflake-conn.md    # `.env` + sources/<name>.yaml + cred rotation
    ├── sis-app-skeleton.py           # `streamlit_app.py` with st.cache_data(ttl=600), st.fragment
    ├── superset-guest-token.md       # FastAPI snippet + RLS injection
    ├── cube-multitenant-schema.yaml  # securityContext + tenant_id claim
    └── tremor-recharts-snapshot.tsx  # baseline Next.js page wiring Cube + Tremor
```

Sketch — `plugins/ravenclaude-core/knowledge/rendering-layer/decision-record.md`:

```markdown
# ADR-0001 — PSM Command Center rendering layer

Status: Proposed (2026-06-04)
Context: One PSM today, possibly N tenants later. Snowflake is the warehouse.
Decision: Evidence.dev for narrative + snapshot pages; Streamlit-in-Snowflake
for live operational panels. Defer multi-tenant React+Cube to v2.
Consequences: Two rendering systems coexist briefly. SQL files become the
portable artifact across all phases. Avoid Hex, Sigma, Looker.
Reversal cost: ~1 week to rewrite Evidence pages as Superset dashboards.
```

Sketch — `plugins/ravenclaude-core/knowledge/rendering-layer/snippets/sis-app-skeleton.py`:

```python
# Streamlit-in-Snowflake skeleton — caller-rights, 10-min refresh, mobile-aware
import streamlit as st
from snowflake.snowpark.context import get_active_session

st.set_page_config(page_title="PSM Console", layout="wide")
session = get_active_session()

@st.cache_data(ttl=600)  # 10-min refresh aligns with refresh SLO
def load_kpis():
    return session.sql("SELECT * FROM psm_console.kpi_snapshot").to_pandas()

@st.fragment(run_every="60s")
def live_panel():
    # st.fragment avoids full-app rerun, fixing SiS's single-session cache limit
    df = session.sql("SELECT * FROM psm_console.alerts_live").to_pandas()
    st.dataframe(df, use_container_width=True)

st.title("PSM Command Center")
kpis = load_kpis()
cols = st.columns([1, 1, 1])
for c, (label, value) in zip(cols, kpis.itertuples(index=False)):
    c.metric(label, value)

live_panel()
```

---

## Sources ledger

(43 sources, deduplicated, with one-line note. Marked **[O]** official docs / **[C]** comparison or case study / **[X]** critical or contrarian view, per the source-class requirement.)

### Evidence.dev

1. **[O]** [Evidence.dev official](https://evidence.dev/) — BI-as-code positioning, feature list.
2. **[O]** [Evidence — Code-based BI tools reviewed](https://evidence.dev/blog/business-intelligence-tools) — Evidence's own comparison (Evidence vs Streamlit vs Observable).
3. **[O]** [Evidence Studio launch](https://evidence.dev/blog/evidence-studio) — Studio replaces Cloud; Pro tier adds SSO + SCIM.
4. **[C]** [BuildPilot — Evidence vs Metabase vs Superset 2026](https://trybuildpilot.com/677-evidence-vs-metabase-vs-apache-superset-2026) — head-to-head OSS BI matrix.
5. **[X]** [HN discussion: Evidence.dev — BI as Code](https://news.ycombinator.com/item?id=35645464) — critical takes on code-first BI ergonomics.

### Apache Superset / Preset

6. **[O]** [Embedding Superset (official docs)](https://superset.apache.org/user-docs/using-superset/embedding/) — Embedded SDK + guest-token mechanics.
7. **[O]** [@superset-ui/embedded-sdk](https://www.npmjs.com/package/@superset-ui/embedded-sdk) — npm package.
8. **[O]** [Preset — Step 2: Deployment / Embedding](https://docs.preset.io/docs/step-2-deployment) — managed-tier embedding guide.
9. **[C]** [Preset — Superset vs Metabase](https://preset.io/blog/superset-vs-metabase/) — Preset's framing of pricing + connectors.
10. **[C]** [elest.io — Superset vs Metabase vs Redash self-host 2026](https://blog.elest.io/apache-superset-vs-metabase-vs-redash-which-open-source-bi-tool-to-self-host-in-2026/) — operational comparison.
11. **[C]** [MeghGen — Running Superset in production right](https://medium.com/meghgen/fast-secure-embedded-running-apache-superset-in-production-the-right-way-67f3db643c53) — production checklist incl. secrets, RLS, guest tokens.
12. **[X]** [Valiotti — Apache Superset 2026 buyer's guide](https://valiotti.com/apache-superset-2026-guide/) — critical: 5-process operational surface.
13. **[C]** [Sameer Hussain — Secure role-based Superset embedding](https://medium.com/@sameerhussain230/building-secure-role-based-embedded-dashboards-with-apache-superset-fastapi-and-react-3798ed7f8651) — FastAPI + React + guest tokens worked example.
14. **[O]** [Guest-token discussion #29824 (Superset GH)](https://github.com/apache/superset/discussions/29824) — official API caveats.

### Metabase

15. **[O]** [Metabase pricing (official)](https://www.metabase.com/pricing/) — Starter $100, Pro $575, OSS free, Enterprise quote.
16. **[O]** [Metabase — Cloud vs self-hosting](https://www.metabase.com/docs/latest/cloud/cloud-vs-self-hosting) — trade-off doc.
17. **[C]** [Coefficient — Metabase pricing & hidden costs 2026](https://coefficient.io/metabase-pricing) — $15–20K/yr hidden ops cost for OSS self-host.
18. **[C]** [CheckThat.ai — Metabase TCO 2026](https://checkthat.ai/brands/metabase/pricing) — plan-by-plan economics.
19. **[X]** [Definite — Metabase vs Definite: real cost of OSS BI](https://www.definite.app/blog/metabase-vs-definite) — critical view of "free" OSS.
20. **[C]** [Vendr — Metabase pricing data](https://www.vendr.com/marketplace/metabase) — median Enterprise $39K/yr.

### Hex

21. **[O]** [Hex × Snowflake integration](https://hex.tech/product/integrations/snowflake/) — Snowpark, OAuth, Marketplace billing.
22. **[O]** [Hex pricing](https://hex.tech/pricing/) — tier framework (page direct-fetch 403'd; specs triangulated).
23. **[O]** [Hex — Snowflake setup guide](https://learn.hex.tech/docs/connect-to-data/data-connections/setup-guides/connect-to-snowflake) — official connection doc.
24. **[C]** [Vendr — Hex pricing](https://www.vendr.com/marketplace/hex-technologies) — independent procurement data.
25. **[X]** [Fabi.ai — Best alternatives to Hex](https://www.fabi.ai/blog/best-alternatives-to-hex) — critical of Hex's price/lock-in.
26. **[X]** [PowerDrill — 12 Hex alternatives 2026](https://powerdrill.ai/blog/best-hex-alternatives-for-data-analysis) — broad contrarian survey.

### Streamlit + SiS

27. **[O]** [Streamlit-in-Snowflake (official)](https://www.snowflake.com/en/product/features/streamlit-in-snowflake/) — product page.
28. **[O]** [Snowflake docs — SiS limitations](https://docs.snowflake.com/en/developer-guide/streamlit/limitations) — 32 MB cap, package channel, CSP issues.
29. **[O]** [streamlit/agent-skills GitHub](https://github.com/streamlit/agent-skills) — Codex/Claude buildability standard.
30. **[O]** [Streamlit blog — Vibe code with AGENTS.md](https://blog.streamlit.io/vibe-code-streamlit-apps-with-ai-using-agents-md-04b7480f754e) — official AI-codegen pattern.
31. **[C]** [GitLab — Structured Streamlit framework in Snowflake](https://about.gitlab.com/blog/how-we-built-a-structured-streamlit-application-framework-in-snowflake/) — production case study.
32. **[X]** [Soputro — Evaluating SiS: the Good, the Bad, the Ugly (Feb 2026)](https://medium.com/towards-data-engineering/evaluating-streamlit-in-snowflake-sis-c4f466cff179) — critical review.
33. **[X]** [Streamlit responsive limitation #6592](https://github.com/streamlit/streamlit/issues/6592) — official issue acknowledging mobile-reflow weakness.
34. **[X]** [DigitalDefynd — 15 Pros & Cons of Streamlit 2026](https://digitaldefynd.com/IQ/pros-cons-of-streamlit/) — critical mobile/server-side coverage.

### React + Tremor + Cube

35. **[O]** [Cube — official site](https://cube.dev/) — semantic-layer positioning.
36. **[O]** [Cube — pricing](https://cube.dev/pricing) — consumption-based starting $0.
37. **[O]** [Cube — Recharts dashboard guide](https://cube.dev/blog/building-a-recharts-dashboard-with-cube) — official worked example.
38. **[C]** [Cube case study — 2× Snowflake cost reduction](https://cube.dev/case-studies/faster-performance-and-a-2x-reduction-in-snowflake-cost) — pre-aggregation impact.
39. **[O]** [Tremor (Vercel-acquired)](https://www.tremor.so/) — official site, active maintenance.
40. **[O]** [Tremor GitHub](https://github.com/tremorlabs/tremor) — active repo, Oct 2025 commits.
41. **[C]** [Querio — Multi-tenant embedded analytics architecture](https://querio.ai/articles/multi-tenant-embedded-analytics-architecture) — JWT + RLS textbook pattern.
42. **[X]** [Querio — RLS for multi-tenant SaaS analytics](https://querio.ai/articles/row-level-security-multi-tenant-saas-analytics) — critical detail on token-based isolation.

### Looker

43. **[O]** [Looker — Signed embedding (official)](https://cloud.google.com/looker/docs/signed-embedding) — HMAC URLs + user_attributes mechanism.
44. **[O]** [Codelabs — Signed Embedding with Looker](https://codelabs.developers.google.com/codelabs/looker-embed) — Google's official walkthrough.
45. **[C]** [Luzmo — Looker pricing 2026](https://www.luzmo.com/blog/looker-pricing) — $35K–60K/yr standard, $150K Enterprise.
46. **[C]** [Toucan Toco — Looker pricing](https://www.toucantoco.com/en/blog/looker-pricing) — independent estimate, matches Luzmo.
47. **[C]** [Modern DataTools — Looker enterprise breakdown](https://www.modern-datatools.com/tools/looker/pricing) — $35K → $100K hidden-cost case.
48. **[X]** [Analytify — 8 best Looker alternatives 2026](https://analytify.ai/looker-alternatives/) — critical: LookML lock-in, $400/viewer SaaS economics, Omni Series B.
49. **[X]** [Qrvey — Looker embedded analytics review 2026](https://qrvey.com/blog/looker-embedded-analytics/) — critical on bolt-on embedding story.
50. **[X]** [Astrato — Looker competitors](https://www.astrato.io/blog/looker-competitors) — contrarian alternatives survey.

### Sigma

51. **[O]** [Sigma — Restrict access in embedded content](https://help.sigmacomputing.com/docs/restrict-access-to-data-in-embedded-content) — official RLS docs.
52. **[O]** [Snowflake + Sigma — Multi-tenant data apps quickstart](https://www.snowflake.com/en/developers/guides/snowflake-build-secure-multitenant-data-applications-snowflake-sigma/) — official architecture pattern.
53. **[O]** [Sigma — Compute cost efficiency & caching FAQ](https://www.sigmacomputing.com/resources/product-faq/sigma-compute-cost-efficiency-and-caching-overview-snowflake-and-bigquery) — Sigma's own framing of the cost question.
54. **[C]** [phData — Implementing RLS in embedded Sigma dashboards](https://www.phdata.io/blog/implementing-row-level-security-in-embedded-sigma-dashboards-with-schema-isolation/) — practitioner case study.
55. **[C]** [CheckThat.ai — Sigma pricing & TCO 2026](https://checkthat.ai/brands/sigma-computing/pricing) — $300/mo+, SMB $56K/yr.
56. **[X]** [Lokad — Review of Sigma Computing](https://www.lokad.com/review-of-sigmacomputing-com/) — critical view of spreadsheet-first ceiling.
57. **[X]** [Knowi — Sigma Computing review 2026](https://www.knowi.com/blog/the-ultimate-sigma-review-pros-cons-and-who-it-is-for/) — pros/cons, warehouse-cost critique.
58. **[X]** [Index.app — Sigma reviews & alternatives](https://index.app/blog/sigma-computing-reviews-pricing-alternatives) — contrarian survey.

### Mode / ThoughtSpot

59. **[O]** [ThoughtSpot acquires Mode Analytics (press)](https://www.thoughtspot.com/press-releases/thoughtspot-acquires-mode-analytics-for-200m) — June 2023 announcement.
60. **[O]** [ThoughtSpot completes acquisition](https://www.thoughtspot.com/press-releases/thoughtspot-completes-200m-acquisition-of-mode-analytics) — July 19, 2023 close.
61. **[C]** [TechCrunch — ThoughtSpot acquires Mode for $200M](https://techcrunch.com/2023/06/26/thoughtspot-acquires-mode-analytics-a-bi-platform-for-200m-in-cash-and-stock/) — independent coverage.
62. **[C]** [Diginomica — ThoughtSpot's Mode acquisition](https://diginomica.com/thoughtspots-200m-mode-analytics-acquisition-step-one-being-massive-says-ceo) — CEO interview.
63. **[X]** [5000fish — Mode alternatives 2026](https://medium.com/@5000fish/mode-analytics-was-acquired-by-thoughtspot-best-mode-alternatives-in-2026-6f02c83fe0e3) — critical: Mode is no longer standalone, Analyst Studio GA 2025.
64. **[C]** [Luzmo — ThoughtSpot pricing 2026](https://www.luzmo.com/blog/thoughtspot-pricing) — Essentials $25, Pro $50, Enterprise six-figure.
65. **[X]** [DashboardFox — Mode alternatives](https://dashboardfox.com/blog/mode-analytics-alternatives/) — contrarian alternatives.

### Observable Framework

66. **[O]** [Observable Framework GitHub](https://github.com/observablehq/framework) — official repo.
67. **[O]** [Framework — Data loaders docs](https://observablehq.observablehq.cloud/framework/data-loaders) — any-language build-time loaders.
68. **[O]** [Observable blog — From exploration to data apps](https://observablehq.com/blog/from-data-exploration-to-data-apps-with-observable) — official narrative.
69. **[C]** [Simon Willison — Interesting ideas in Observable Framework](https://simonwillison.net/2024/Mar/3/interesting-ideas-in-observable-framework/) — respected practitioner analysis.
70. **[C]** [Appsilon — Big-scale data dashboards with Observable Framework](https://www.appsilon.com/post/observable-framework-data-science-dashboards) — case study.
71. **[X]** [MakerStack — Observable review 2026](https://makerstack.co/reviews/observable-review/) — critical review.
72. **[X]** [HN — Starboard / ObservableHQ dependency concerns](https://news.ycombinator.com/item?id=26857888) — contrarian on cloud lock-in.
73. **[C]** [OSACON 2024 — Framework session](https://osacon.io/sessions/2024/observable-framework-a-new-open-source-static-site-generator-to-get-data-past-the-last-mile/) — conference framing.

### Cross-cutting (auth, multi-tenant, semantic layers)

74. **[C]** [Querio — Multi-tenant embedded analytics architecture](https://querio.ai/articles/multi-tenant-embedded-analytics-architecture) — JWT + tenant_id pattern.
75. **[C]** [Embeddable — Multi-tenant DB architectures for embedded analytics](https://embeddable.com/blog/embedded-analytics-for-multi-tenant-database-architectures) — survey of patterns.
76. **[O]** [Snowflake docs — observability for apps](https://docs.snowflake.com/en/developer-guide/builders/observability) — runtime observability in SiS / Native Apps.
77. **[C]** [Qrvey — Multi-tenant deployment guide 2026](https://qrvey.com/blog/multi-tenant-deployment/) — independent multi-tenant patterns.
78. **[C]** [Atlan — Best semantic-layer tools 2026](https://atlan.com/know/best-semantic-layer-tools/) — Cube/dbt/Looker/Snowflake Semantic Views ranked.
79. **[C]** [Basedash — Best semantic-layer tools compared 2026](https://www.basedash.com/blog/best-semantic-layer-tools-compared-2026) — independent comparison.
80. **[C]** [Holistics — Snowflake BI tools 2026](https://www.holistics.io/blog/snowflake-bi-reporting-tools/) — 8-tool Snowflake-specific comparison.
81. **[C]** [Coefficient — Snowflake data visualization tools 2026](https://coefficient.io/snowflake/snowflake-data-visualization-tools) — 7 Snowflake-native tools.
82. **[C]** [Toucan Toco — Embedded analytics multi-tenancy & RLS 2026](https://www.toucantoco.com/en/blog/embedded-analytics-multi-tenancy-row-level-security-pricing) — survey of multi-tenant pricing.

---

**Report end.** Confidence: HIGH on platform-feature triangulations (≥3 sources each), MEDIUM on exact 2026 pricing (sources differ by ±20%, vendor pages partially fetch-blocked), HIGH on the architectural recommendation.
