# Open-source CS Dashboard Implementations (2026-06-04)

Survey of publicly documented and open-source customer-success / partner-success / SaaS-retention dashboard implementations. Goal: extract reusable patterns (and anti-patterns) for our own CS/PSM dashboard work. Each entry was reached via web search; for the deeper-investigated entries I fetched the repo README or template page to confirm details. Where a fact came only from search-result summaries (not a direct repo fetch), I mark it `[search-summary]`.

A note on scope: there is **no widely-adopted, dedicated open-source clone of Gainsight/Planhat/Vitally**. The CS-dashboard space at the open-source layer is split into three categories, and the patterns below come from across all three:

1. **CRM / engagement suites** that ship a "dashboard" tab (Chatwoot, EspoCRM, SuiteCRM, CustomerOS).
2. **Analytics frameworks + dbt projects** that model the CS-relevant fact tables (jaffle-shop, mrr-playbook, attribution-playbook, ra_data_warehouse, customer-360-dbt, Lightdash templates, Hex/Evidence/Rill examples).
3. **Adjacent self-hosted signal collectors** (Formbricks for NPS/CSAT, PostHog for product usage, Beton Inspector for account scoring).

The synthesis pulls from all three layers.

---

## 1. CustomerOS (customeros/customeros)

URL: https://github.com/customeros/customeros · Stack: Go (91%) backend, TypeScript/React frontend, PostgreSQL + Neo4j (graph), GraphQL + gRPC, EventStore · License: Apache-2.0 (core), proprietary "ee" directory for enterprise features · Stars: ~116 · Last release: v0.63.56 (May 2025); 11,005 commits on "otter" branch · Accessed: 2026-06-04

### What's notable
- One of very few all-in-one B2B SaaS GTM platforms (CRM + CS) that is genuinely open source.
- Uses **Neo4j alongside PostgreSQL** specifically to model the customer graph (accounts ↔ contacts ↔ deals ↔ org hierarchy) — interesting choice that most CS tools don't make.
- Architecture is monorepo with clean split: `apps/` (launcher, settings), `auth/`, `components/` (UI libs), `core/` (shared libs), `server/` (DB+API).
- EventStore signals an event-sourced backend, which is unusual for CRM/CS but powerful for replaying customer-state over time.

### Patterns to steal
- **Graph DB for relationship-heavy CS data** is worth considering when account hierarchies (parent/child, partner-of-partner) matter — and they do for PSM.
- **Event-sourced customer state** means you can reconstruct "what did we know about this account on date X?" — useful for retrospective health-score backtesting.
- Monorepo with explicit `core/` shared lib and `components/` UI lib boundary keeps the FE/BE story clean even at >10K commits.

### Patterns to avoid
- "ee" directory pattern (open core with proprietary enterprise) creates the usual licensing tension; if we open-source, decide upfront whether we're truly OSS or open-core.
- Low star count (~116) despite huge commit volume suggests **discoverability/community problem** — building it is not enough; CS is a buyer-led market and devs aren't the buyer.

---

## 2. dbt-labs/mrr-playbook (formerly fishtown-analytics/mrr-playbook)

URL: https://github.com/dbt-labs/mrr-playbook · Stack: dbt + Snowflake (SQL-only) · Stars: 89 · Forks: 54 · License: not visibly stated in README excerpt · Status: **archived 2025-02-05, read-only** · Accessed: 2026-06-04

### What's notable
- The canonical worked example for modeling subscription revenue in dbt — referenced widely in the dbt blog post "Modeling subscription revenue."
- Project layout is the standard dbt three-tier: `data/` (seeds), `macros/`, `models/`.
- **Explicitly a "worked example, not a package"** — designed to be copied and adapted, not installed.

### Patterns to steal
- The **one-record-per-customer-per-month grain** with a `change_category` column (new / churn / expansion / contraction / reactivation) is the canonical MRR model and the foundation for any retention-cohort dashboard. Steal this exactly.
- Companion `attribution-playbook` (same org) gives the parallel pattern for marketing attribution — both share the "worked-example" framing.
- Seeds-based testing means you can run the full pipeline locally in seconds with no warehouse setup.

### Patterns to avoid
- Snowflake-only SQL flavor (limited reuse for Postgres/BigQuery teams without a port).
- Now-archived: dbt Labs themselves abandoned both playbooks rather than evolving them, which says something about how quickly hand-rolled MRR logic ages.

---

## 3. dbt-labs/jaffle-shop (+ jaffle-shop-classic)

URL: https://github.com/dbt-labs/jaffle-shop · Stack: dbt-core, multi-warehouse (BigQuery / Snowflake / Redshift / Databricks / Postgres) · Stars: 313 · Forks: 534 · License: open source (template repo) · Accessed: 2026-06-04

### What's notable
- The "hello world" of dbt and the most-forked CS-adjacent dbt project by far.
- Raw inputs: `customers`, `orders`, `order_items`, `products`, `supplies`, `stores`, `payments` (classic). Marts produce `dim_customers`, `fct_orders`, etc.
- Companion `jaffle_shop_mssql` proves the pattern ports to SQL Server.

### Patterns to steal
- **Staging → intermediate → marts** layering is the de-facto industry standard; any CS dashboard should adopt it rather than inventing its own.
- 534 forks means there's a huge corpus of community variants — search "jaffle" on GitHub for adaptations (churn, cohort, LTV) and shortcut design decisions.
- Template-repo pattern (one-click "Use this template") is the right onboarding UX for a CS-dashboard starter.

### Patterns to avoid
- Restaurant domain — every CS team has to re-skin it, and "jaffle" jargon has leaked into many production codebases that should have renamed their fact tables.

---

## 4. dbt-labs/attribution-playbook

URL: https://github.com/fishtown-analytics/attribution-playbook · Stack: dbt + Snowflake · License: open source · Accessed: 2026-06-04 · Status: archived alongside mrr-playbook

### What's notable
- Worked example of multi-touch attribution modeling — adjacent to CS in that it tells you *which channels acquired the customers you're now trying to retain*.

### Patterns to steal
- First-touch / last-touch / linear / time-decay attribution as separate models with the same grain (one row per touch per conversion) — reusable model for CS expansion-attribution too.

### Patterns to avoid
- Same Snowflake-lock-in and archived-status issues as mrr-playbook.

---

## 5. ndleah/customer-360-dbt

URL: https://github.com/ndleah/customer-360-dbt · Stack: dbt + PostgreSQL (with Databricks-compat refactor in progress) · Stars: ~3 · License: not visibly stated · Accessed: 2026-06-04

### What's notable
- Kimball-style 3-layer dbt project (staging / intermediate / marts) focused on unifying customer data.
- Implements **PII masking** at the staging layer and **source freshness validation** (transactions must be <1 day old).
- "Next Best Product Category" recommendation is a marts-layer model — interesting because it's where CS meets recommender systems.

### Patterns to steal
- **PII masking as a staging-layer concern** (not application-layer) is the right altitude — push privacy controls down to the data so every downstream consumer inherits them.
- **Source freshness as a hard test** (not a dashboard widget) — a stale source should *fail the pipeline*, not silently render stale numbers.
- `dim_contacts` as the central referential-integrity anchor.

### Patterns to avoid
- Very low community signal (3 stars) — not a battle-tested architecture; learn the patterns, don't depend on the code.

---

## 6. rittmananalytics/ra_data_warehouse

URL: https://github.com/rittmananalytics/ra_data_warehouse · Stack: dbt + BigQuery/Snowflake, with conditional source/ETL selection via vars · License: Apache-2.0 · Stars: 269 · Forks: 58 · Last release: v1.2.1 (Jan 2021) · Accessed: 2026-06-04

### What's notable
- Most ambitious of the open-source dbt CS frameworks — **20+ pre-integrated SaaS sources** (HubSpot, Salesforce, Xero, Stripe, Asana, Jira, Mailchimp, Segment, Mixpanel, Intercom, Google/Facebook Ads).
- Three-layer model: `stg_*` (source) → `int_*` (integration/merge/dedupe) → `wh_*` (warehouse marts).
- Six subject-area marts: Finance, CRM, Subscriptions, Projects, Marketing, Product.

### Patterns to steal
- **`stg_ / int_ / wh_` prefix convention** is more disciplined than the bare `staging/intermediate/marts` folder pattern — the prefix follows the model name even when it's referenced elsewhere.
- **Conditional source via dbt vars** so the same downstream model can switch between Fivetran-shaped, Airbyte-shaped, or Stitch-shaped sources — this is the right abstraction for a multi-customer dashboard.
- Subject-area marts (not "everything in `marts/`") make ownership and stewardship obvious.

### Patterns to avoid
- **No customer-health scoring logic** despite the breadth of sources — the framework gives you the building blocks but stops short of the actual CS metric, which is the hardest part.
- v1.2.1 in Jan 2021 = effectively dormant. Five years of dbt evolution since.

---

## 7. Chatwoot (chatwoot/chatwoot)

URL: https://github.com/chatwoot/chatwoot · Stack: Ruby on Rails + Vue.js, PostgreSQL · License: MIT (note: their actual license is more complex; verify before depending) · Stars: 25K+ class · Accessed: 2026-06-04

### What's notable
- Open-source omnichannel support desk (Intercom/Zendesk alternative) with a **built-in dashboard** showing total messages, response times, resolution times.
- Custom Attributes feature lets you store account-level CS data alongside conversations — the data model is conversation-centric but extensible.
- Pre-Chat Forms for collecting structured user context.

### Patterns to steal
- **Custom Attributes pattern** for extensibility: a typed key/value store on the core Account/Contact model so consumers can add CS-specific fields (renewal date, CSM owner, ARR) without forking schema.
- Response time / resolution time / first-response time as the support-side health signals — the canonical CSAT-adjacent metrics.
- Embeddable widget pattern lets the same dashboard surface inside a customer's own portal.

### Patterns to avoid
- Conversation-grain is wrong for CS dashboards (we need account-grain). Don't try to bend Chatwoot into a CS platform; integrate alongside it.

---

## 8. Formbricks (formbricks/formbricks)

URL: https://github.com/formbricks/formbricks · Stack: TypeScript (98%), Next.js, React, Prisma, Auth.js, TailwindCSS · License: AGPL-3.0 (core) + Enterprise · Stars: ~12.3K · Forks: ~2.3K · Latest release: 5.0.2 (May 2026) · Accessed: 2026-06-04

### What's notable
- Self-hosted survey platform with **dedicated NPS / CSAT / CES question types** and **built-in analytics dashboards that calculate scores automatically and track trends over time** `[search-summary]`.
- In-app, website, link, and email survey distribution — covers all CS feedback collection channels.
- User-targeting (which surveys fire for which segments) is no-code.

### Patterns to steal
- **NPS/CSAT/CES as first-class question types with automatic scoring** — don't store NPS as a free-form 0-10 number, encode the question type so the dashboard math is centralized.
- AGPL-3.0 license is the right call for a self-hosted platform that wants to deter SaaS-clones without locking out genuine self-hosters.

### Patterns to avoid
- Prisma + Next.js full-stack means the analytics dashboard is tightly coupled to the application DB — harder to reuse the score logic in a warehouse-based CS dashboard.

---

## 9. getbeton/inspector ("Beton Inspector")

URL: https://github.com/getbeton/inspector · Stack: Next.js + TypeScript, Supabase (PostgreSQL with RLS), Zustand + React Query · License: AGPL-3.0 · Stars: ~31 · Last release: v0.0.1 (Feb 2026) · Accessed: 2026-06-04

### What's notable
- Explicitly positioned as the **open-source alternative to Pocus and Common Room** — both proprietary "product-led sales" / account-scoring tools.
- Scores accounts on three axes simultaneously: **Account Health**, **Expansion Potential**, **Churn Risk**, all on a 0–100 scale with grade buckets (M100, M75, M50, M25, M10).
- ~40 API routes; 20+ behavioral signal detectors (trial conversion intent, power user emergence, feature adoption velocity).
- Pulls from PostHog + CRM as the two data sources.

### Patterns to steal
- **Three scores, not one.** Health, expansion, and churn are *different* questions with different signals — a single composite score blurs them. Steal the multi-score model.
- **Grade buckets (M100/M75/M50/M25/M10)** on top of the raw 0-100 score: dashboards become categorical at the visual layer while the underlying math stays continuous.
- **Behavioral signal detectors as named, individually testable units** ("power user emergence", "trial conversion intent") rather than a monolithic scoring function. Each detector is independently tunable.
- Row-level security via Supabase as the multi-tenant boundary — saves writing per-query tenant filters.

### Patterns to avoid
- v0.0.1, 31 stars, single-contributor pattern = pre-production. Borrow ideas, not code.
- AGPL-3.0 may be too restrictive if we want a permissive ecosystem.

---

## 10. PostHog Customer Health Tracking (public playbook)

URL: https://posthog.com/handbook/cs-and-onboarding/health-tracking (403 on fetch; details from `[search-summary]`) · Stack: PostHog data warehouse + ClickHouse + Postgres + HubSpot + Stripe · Accessed: 2026-06-04

### What's notable
- **Published, public CS playbook** describing how PostHog itself does health tracking — a rare artifact because most CS teams treat their scoring as proprietary.
- Overall health score computed **out of 10** based on weighted factors `[search-summary]`.
- Consolidates HubSpot + Stripe + ClickHouse + Postgres as source-of-truth for each account.
- Uses Vitally as the destination CS tool (note: PostHog is OSS, but their *CS surface* uses commercial software).

### Patterns to steal
- **Publish your scoring methodology.** Transparency about the formula is a hiring/sales asset and makes the dashboard credible internally.
- **0-10 score** (not 0-100) is friendlier to humans, harder to over-precision-tune.
- Public PostHog/Pocus case study describes the integration pattern: warehouse → reverse-ETL → CS tool.

### Patterns to avoid
- PostHog themselves chose not to self-build the CS tool layer — even an OSS-native company bought Vitally. Lesson: the dashboard is the *tip* of the CS stack; data plumbing is the iceberg.

---

## 11. Dynatrace CustomerSuccess (dynatrace-oss/CustomerSuccess)

URL: https://github.com/dynatrace-oss/CustomerSuccess · Stack: Dynatrace-specific (Grail data engine, DQL query language, JSON dashboard format) · License: Apache-2.0 · Stars: 34 · Forks: 7 · Accessed: 2026-06-04

### What's notable
- Three solutions: **Tenant Review** (config audit), **Platform Adoption Dashboard** (40 tiles), **Software Obsolescence Management** (lifecycle tracking).
- 40 tiles covering active users, app adoption rankings, workflow health, AI usage, DQL analytics, lifecycle cohorts.
- **Explicitly read-only / safe / local-analysis** — the dashboard inspects but never modifies.

### Patterns to steal
- **"Read-only by contract" as a dashboard property** — encode safety into the dashboard's design statement, not just docs. Reduces blast radius and unblocks adoption.
- **40-tile dashboard** is a strong existence-proof that a CS dashboard can be tile-rich without being incoherent, *if* tiles are organized by adoption phase (lifecycle cohorts).
- JSON-importable dashboard format means dashboards are versionable, reviewable, diff-able artifacts.

### Patterns to avoid
- Dynatrace-only (DQL, Grail) — not portable.
- Vendor-specific OSS rarely cross-pollinates; 34 stars after years.

---

## 12. Hex Customer Health Dashboard Template

URL: https://hex.tech/templates/kpi-dashboards/customer-health-dash/ (403 on fetch; details from `[search-summary]`) · Stack: Hex (SQL + Python notebooks) · License: free template, copy to your workspace · Accessed: 2026-06-04

### What's notable
- Public template covering churn rate, at-risk segments, retention forecasting, all interactively.
- Companion **Customer Churn Prediction** template uses ML on behavioral + engagement + support data.
- Companion **Customer Lifetime Value Dashboard** template.

### Patterns to steal
- **Three companion templates** (Health, Churn Prediction, LTV) that share a data model — modular dashboard architecture where each view answers one question.
- "Forecast retention" as a first-class panel, not just a historical chart.
- ML-augmented prediction as an *optional* layer, not a precondition.

### Patterns to avoid
- Hex is closed-source — you can copy the template into a Hex workspace but not export the methodology fully into your own stack. Borrow the *structure*, not the code.

---

## 13. Lightdash demo-training + lightdash-templates

URL: https://github.com/lightdash/lightdash-templates and https://github.com/lightdash/lightdash-demo-training · Stack: Lightdash (Agentic BI on dbt) · License: Lightdash is open-source (MIT for core) · Accessed: 2026-06-04

### What's notable
- demo-training data model: **ACCOUNTS (Companies), DEALS (Sales Pipeline), USERS (Individual Contacts), TRACKS (Product Usage)** — the four canonical CS entities in one schema `[search-summary]`.
- Templates organized by data type / domain (e.g. bigquery-usage-tracking).
- BI-as-code via YAML + dbt — same model definitions everywhere.

### Patterns to steal
- **Four-entity canonical schema (Accounts / Deals / Users / Tracks)** as the universal CS join key set. Anything you can answer in CS, you can answer with joins across these four.
- **YAML + dbt for the semantic layer** means metric definitions live in Git, reviewable as PRs.
- Templates as YAML files you drop into your dbt project — clean reuse model.

### Patterns to avoid
- Lightdash-specific YAML schema means lock-in to their tool, even though the underlying dbt is portable.

---

## 14. Rill Examples (rilldata/rill-examples)

URL: https://github.com/rilldata/rill-examples · Stack: Rill (YAML + SQL, BI-as-code with semantic layer) · License: open source · Accessed: 2026-06-04

### What's notable
- Monorepo of example projects. CS-relevant ones: **rill-app-engagement**, **rill-cost-monitoring**, **rill-partner-filtered-dashboards** (directly relevant to PSM).
- YAML defines dimensions/measures/time-grains; SQL defines the underlying queries.
- `rill start` builds the project from data source to dashboard in one command.

### Patterns to steal
- **rill-partner-filtered-dashboards** is the closest open-source artifact to a PSM-style dashboard — worth a deep read for the filter/scope-by-partner pattern.
- Semantic-layer-first design (YAML for the *meaning*, SQL for the *retrieval*) means metric names are stable even when the underlying SQL changes.
- One-command bootstrap matters for adoption.

### Patterns to avoid
- Rill's adoption is still small relative to Superset/Metabase; betting the dashboard on Rill is a tool-risk decision.

---

## 15. Apache Superset (SaaS startup use case + embedded dashboards)

URL: https://superset.apache.org · Stack: Python/Flask, React frontend, multi-warehouse · License: Apache-2.0 · Stars: 60K+ class · Accessed: 2026-06-04

### What's notable
- Most-deployed open-source BI tool for SaaS startups; published use-case describes a daily-updated SaaS dashboard tracking **burn/runway, DAU/MAU stickiness, support-ticket distribution by category, acquisition funnel by source, multi-touch attribution** in a single view `[search-summary]`.
- Real-world deployment cited: ~€50K/year saved vs Tableau for 40 seats; embedded dashboard for Pro+ customers monetized the Pro tier.

### Patterns to steal
- **One dashboard per persona** (CFO sees burn/runway; CSM sees stickiness/support-tickets) — same data, different lens. This is the canonical "role-based dashboard" pattern.
- **Embedded customer-facing dashboards as a monetization lever** (Pro tier gets their own real-time usage view inside the product) — direct application for our partner/customer self-service portal.
- 40+ visualization types out of the box; plug-in architecture for custom viz.

### Patterns to avoid
- Superset's permission model is notoriously fiddly at scale; budget integration time.

---

## 16. Metabase (metabase/metabase)

URL: https://github.com/metabase/metabase · Stack: Clojure + JavaScript, multi-warehouse · License: AGPL-3.0 (core) + commercial editions · Stars: 38K+ class · Accessed: 2026-06-04

### What's notable
- Easiest-onboarding open-source BI tool; published blog series "Automating growth and customer insights in SaaS businesses."
- Embeddable via iframe or React SDK; quote: **"Dashboard modifications can be reduced from 2 days of engineering time to 2 hours of Customer Success time"** `[search-summary]` — direct evidence that giving CSMs dashboard-edit ability is high-ROI.
- Tracks ARR, MAU, NPS, churn risk, support metrics in standard saved-question + filter pattern.

### Patterns to steal
- **CSMs as dashboard editors, not just consumers** — this changes the economics of CS analytics. Build for this from day one (permission model, audit trail, undo).
- 5-minute setup means the dashboard isn't gated on data-team bandwidth.

### Patterns to avoid
- AGPL-3.0 + commercial fork tension means features lag the cloud version; verify before relying on a specific capability in OSS.

---

## 17. Evidence.dev (evidence-dev/evidence + evidence-dev/template)

URL: https://github.com/evidence-dev/evidence and https://github.com/evidence-dev/template · Stack: SQL + Markdown, code-based BI (Svelte under the hood) · License: open source · Accessed: 2026-06-04

### What's notable
- **Dashboards as Markdown files with embedded SQL** — the entire dashboard is a `.md` file in Git.
- `npm install && npm run sources && npm run dev` to bootstrap locally.
- VS Code extension + GitHub Codespaces support.

### Patterns to steal
- **Dashboard-as-code at the Markdown level** is the strongest version-control story of any tool in this report. Every dashboard change is a PR with a diff a human can read.
- Same toolchain for writing docs and writing dashboards reduces context-switching cost.
- Codespaces-ready setup is the right onboarding bar.

### Patterns to avoid
- Smaller community than Metabase/Superset; fewer pre-built CS examples to copy from.

---

## 18. Streamlit Customer Churn Dashboards (community examples)

URLs: https://customer-churn-prediction-rg.streamlit.app/ and https://customer-churn-analysis-dashboard.streamlit.app/ · Stack: Streamlit + scikit-learn + SHAP · License: varies per repo · Accessed: 2026-06-04

### What's notable
- Two distinct community-deployed apps: one is an **EDA + KPI dashboard split**, the other does **ML-based churn prediction with SHAP value explanations** `[search-summary]`.
- Multi-page Streamlit pattern: Home / Predict / Data / Dashboard / History.

### Patterns to steal
- **EDA tab + KPI tab split** is a clean way to satisfy both the "tell me what's happening" and "let me explore" use cases without one mode contaminating the other.
- **SHAP values on top of churn predictions** so the dashboard explains *why* an account is flagged — this is the only thing that makes ML-driven CS scoring actionable for a CSM.
- Multi-page nav with History tab (prediction provenance) is a nice audit feature.

### Patterns to avoid
- Streamlit apps don't scale to large concurrent users without effort; fine for an internal CS team, not for a customer-facing portal.
- Most community Streamlit churn apps use **telecom-industry public datasets** — don't generalize the feature importances; they're domain-specific.

---

## 19. Hightouch + dbt Reverse-ETL pattern (referenced architecture)

URL: https://www.getdbt.com/blog/dbt-and-hightouch-are-putting-transformed-data-to-work · Stack: warehouse (Snowflake/BigQuery) + dbt + Hightouch (reverse-ETL) → Zendesk/Gainsight/Totango · License: pattern, not code · Accessed: 2026-06-04

### What's notable
- Not an open-source dashboard, but the **canonical reference architecture** for "model in warehouse, activate in CS tool" — the pattern almost every modern CS team converges on.
- dbt computes the health score in SQL; Hightouch syncs the score to whatever surfaces the CSM lives in.

### Patterns to steal
- **Score lives in the warehouse, not in the CS tool.** The CS tool is a *consumer* of the score. This is the most important architectural call in modern CS analytics.
- Reverse-ETL lets you change CS tools without rewriting your scoring logic.

### Patterns to avoid
- Hightouch is closed-source SaaS; the OSS equivalent (Grouparoo, since acquired by Airbyte) is much less mature `[search-summary]`. Plan for vendor switching cost.

---

## 20. keon/awesome-customer-success (curated resource list)

URL: https://github.com/keon/awesome-customer-success · License: CC0-1.0 · Stars: 22 · Forks: 12 · Accessed: 2026-06-04

### What's notable
- Curated list of CS resources. Open-source pointers in the list: **Beton Inspector** (revenue intelligence, OSS Pocus alt), **Discourse** (customer communities), **Quackback** (feedback platform with voting boards, public roadmaps, changelogs).

### Patterns to steal
- The list itself confirms the sparseness of the OSS CS ecosystem — most "tools" in the list are commercial.
- **Quackback's three-feature combo** (feedback voting + public roadmap + changelog) is a tight CS-feedback-loop pattern worth replicating.

### Patterns to avoid
- 22 stars / 16 commits — sparse maintenance. Use as a starting point, not a reference.

---

## Synthesis — top 5 patterns we should adopt

1. **Score in the warehouse, activate in the CS surface.** (Hightouch + dbt pattern, PostHog, ra_data_warehouse.) The health score is a SQL artifact, not a CS-tool artifact. This means we can swap dashboards, swap CS tools, swap visualization layers, and the scoring logic stays. Every multi-mature CS team converges on this; we should start here.

2. **Multi-axis scoring, not a single composite.** (Beton Inspector's Health + Expansion + Churn trio; Hex's three-template family of Health / Churn Prediction / LTV.) A single 0-100 health score blurs distinct questions. We should compute Health, Expansion Potential, and Churn Risk as separate scores with separate signal weights, then *optionally* combine for an executive view.

3. **Account/Deal/User/Track as the four-entity canonical schema.** (Lightdash demo-training.) Every CS question reduces to a join across these four. Building the dashboard model around this set (with PSM as a fifth, partner-scoped layer) gives us a stable semantic layer that survives tool changes.

4. **Dashboards-as-code in Git** with the canonical `staging/ → intermediate/ → marts/` dbt layering. (jaffle-shop, ra_data_warehouse, customer-360-dbt, Evidence.dev.) Version-control the dashboards, code-review the metric definitions, run them as artifacts in CI. The non-OSS CS tools that don't do this (Gainsight, Planhat) are precisely the ones CSMs complain are unmaintainable.

5. **Role-based one-dashboard-per-persona, not feature-complete generic dashboards.** (Superset SaaS use case; Metabase blog; Dynatrace 40-tile dashboard.) CFO, CSM, Product, PSM see *different views of the same data*, not different data. Build the semantic layer once, expose per-role surfaces. Quote-worthy: "Dashboard modifications can be reduced from 2 days of engineering time to 2 hours of Customer Success time" (Metabase) — this is the ROI argument for letting CSMs edit, which requires a stable semantic layer underneath.

## Synthesis — top 5 anti-patterns we should avoid

1. **Building a Gainsight clone.** There is no widely-adopted OSS Gainsight/Planhat alternative despite years of demand. CustomerOS, Beton Inspector, and others have <150 stars combined. The CS-platform buyer is the CRO/CCO, not the developer, and OSS distribution doesn't reach them. **Don't build the whole platform; build the warehouse layer + one strong surface.**

2. **Single composite health score, weighted by gut feel.** (The Custify/Vitally blog-post pattern: "50% usage, 20% adoption, 15% support, 10% NPS, 5% payment.") The weights are unfalsifiable, the formula is opaque to CSMs, and nobody can act on a 67/100. Use multi-axis scores with named, individually-testable signal detectors (Beton Inspector pattern).

3. **Tool-specific dashboards** (Dynatrace DQL, Hex notebooks, Lightdash YAML extensions). The dashboards are great until you want to migrate. Anything proprietary to a tool's metadata format is technical debt. Evidence.dev's Markdown-as-dashboards is the cleanest example of the right altitude.

4. **Conversation-grain or event-grain for an account dashboard.** (Chatwoot-style.) CS dashboards live at account-grain (or partner-grain for PSM). If your fact table is at message/event grain, every panel becomes a `GROUP BY account_id` boilerplate, and slow. Model the dim/fact tables at account-grain from the start.

5. **Snowflake-only or Postgres-only SQL.** (mrr-playbook, customer-360-dbt.) Locks out adopters and makes the project hard to port later. Use dbt's adapter abstraction or write dialect-agnostic SQL from day one. The number of dormant Snowflake-only OSS dbt projects in this survey is telling.

---

## Sources ledger

Direct repository / template fetches (confirmed in this session 2026-06-04):

- https://github.com/customeros/customeros — CustomerOS architecture, license, commit volume
- https://github.com/fishtown-analytics/mrr-playbook — dbt MRR worked example (archived 2025-02-05)
- https://github.com/dbt-labs/jaffle-shop — canonical dbt example
- https://github.com/rittmananalytics/ra_data_warehouse — multi-source SaaS dbt framework
- https://github.com/ndleah/customer-360-dbt — Kimball-style dbt customer-360
- https://github.com/dynatrace-oss/CustomerSuccess — Dynatrace CS dashboards
- https://github.com/getbeton/inspector — Beton Inspector (OSS Pocus alt)
- https://github.com/formbricks/formbricks — Formbricks NPS/CSAT platform
- https://github.com/keon/awesome-customer-success — curated list
- https://github.com/rilldata/rill-examples — Rill example projects
- https://github.com/lightdash/lightdash-templates — Lightdash YAML templates (partial; README excerpt only)

Search-summary sources (not directly fetched, surfaced via WebSearch result snippets — flagged inline with `[search-summary]`):

- PostHog public health-tracking playbook (`posthog.com/handbook/cs-and-onboarding/health-tracking` — returned 403 on direct fetch)
- Hex Customer Health Dashboard template (`hex.tech/templates/kpi-dashboards/customer-health-dash/` — returned 403)
- Hex Customer Churn / CLV templates
- Streamlit community churn-prediction apps (`customer-churn-prediction-rg.streamlit.app`, `customer-churn-analysis-dashboard.streamlit.app`)
- Apache Superset SaaS startup use cases (TVL Managed Superset blog)
- Metabase customer success / embedded analytics docs
- Evidence.dev template repo (https://github.com/evidence-dev/template)
- Lightdash demo-training entity model
- Chatwoot dashboard features
- dbt Labs + Hightouch reverse-ETL architecture blog
- Gainsight / Vitally / Custify / Planhat marketing pages (used only as sources for prevalent score-formula patterns, marked anti-pattern)
- Show HN: FirstDistro (early-warning SaaS churn system, Dec 2025 — commercial, not OSS)
- Quackback feedback platform (referenced via awesome-customer-success list)

Notable absences (searched but found nothing material):

- No dedicated open-source "Gainsight clone" with substantial adoption.
- No widely-used open-source PSM (Partner Success Management) dashboard — `rilldata/rill-examples/rill-partner-filtered-dashboards` is the closest artifact and is small.
- No mature open-source customer-health-score dbt package (the playbooks are worked examples, not packages, and the most ambitious framework — `ra_data_warehouse` — explicitly does not include health scoring).
- The "open-source customer success" search-space is dominated by support desks (Chatwoot, Helpy), NPS/CSAT collectors (Formbricks, Open NPS), and dbt examples — not by integrated CS dashboards. This is itself a finding.
