# New-plugin candidates — research & roadmap (2026-06-15)

> Research output for the "identify 10 new plugins" task. The marketplace already
> ships ~99 plugins across the software-delivery chain, cloud, app-craft, data/AI,
> the Microsoft stack, and ~40 business/operations verticals — so genuine *gaps*
> are now narrow and specific. This doc enumerates 10 candidates that are **not**
> covered by an existing plugin, prioritizes them by **demand × technical
> feasibility × accuracy-risk**, and records the implementation approach for each.
>
> Two of these (the top two) are built as initial releases in the same PR; the
> rest are a sequenced backlog.

## How "gap" was determined

Every candidate below was checked against the full `plugins/` roster (and against
the closest-adjacent plugin's stated *seams*, since this marketplace deliberately
splits strategy/ops from engineering). A candidate is only listed if its core job
is owned by **no** existing plugin — not merely "mentioned as a seam." Where an
adjacent plugin exists, the boundary is stated explicitly so the new plugin
deepens rather than duplicates.

## Prioritization rubric

| Axis | Why it matters here |
|---|---|
| **Demand** | How often a consumer of an agent marketplace actually hits this need. |
| **Feasibility** | Can it be authored to this repo's quality bar (cited knowledge, decision trees, durable facts) without standing up new infrastructure? |
| **Accuracy-risk** | How volatile the domain's facts are. RFC/standard-grounded domains (email auth, geospatial formats, extension manifests) are *low*-risk; fast-moving SaaS-platform UIs/pricing are *high*-risk and need live web verification to stay honest (the repo's accuracy discipline). |

Lower accuracy-risk + high demand + high feasibility → build first.

## The 10 candidates (prioritized)

| # | Candidate | Demand | Feasibility | Accuracy-risk | Verdict |
|---|---|---|---|---|---|
| 1 | **email-deliverability-engineering** | High | High | Low (RFC-grounded) | **BUILD NOW** |
| 2 | **browser-extension-engineering** | Med-High | High | Low (MV3 spec) | **BUILD NOW** |
| 3 | **gis-geospatial-engineering** | Med-High | High | Low (OGC/PostGIS) | Next |
| 4 | **servicenow-itsm** | High | Med | High (platform UI/licensing) | Next (needs live verify) |
| 5 | **hubspot-operations** | High | Med | Med-High (platform) | Backlog |
| 6 | **jira-atlassian-admin** | High | Med | Med-High (platform) | Backlog |
| 7 | **shopify-app-engineering** | Med-High | Med | Med (APIs evolve) | Backlog |
| 8 | **trust-and-safety-operations** | Med | Med | Med (policy/reg shifts) | Backlog |
| 9 | **wordpress-cms-engineering** | Med | High | Low-Med | Backlog |
| 10 | **devrel-developer-experience** | Med | High | Low | Backlog |

### 1. email-deliverability-engineering — **BUILD NOW**

- **Purpose / value.** Get email to the inbox and keep it there: SPF, DKIM, DMARC
  (incl. the Google/Yahoo 2024 bulk-sender requirements — DMARC enforcement,
  one-click unsubscribe, ≤0.3% complaint rate), BIMI, MTA-STS + TLS-RPT, domain
  reputation, list hygiene, bounce/complaint feedback loops, and warmup. Every
  org that sends transactional or marketing email hits this and it is chronically
  under-served by generalist help.
- **Boundary.** `marketing-operations` owns *campaign strategy/content*; this owns
  the *sending-infrastructure + authentication + reputation* engineering.
  `devops-cicd`/cloud plugins own the DNS records' provisioning; this specifies
  *what records must exist and why*. `fintech-payments`/`api-engineering` own
  webhook plumbing; this owns ESP bounce/complaint webhook *semantics*.
- **Approach.** 2 agents (deliverability-architect, email-auth-engineer), skills
  for an auth audit (SPF/DKIM/DMARC/MTA-STS) and a deliverability incident
  triage, a cited knowledge bank (auth standards + the 2024 sender rules + a
  reputation-recovery decision tree). No runtime deps; pure standards knowledge.
- **Why first.** Highest demand among the gaps, lowest accuracy-risk (RFCs 7208 /
  6376 / 7489 / 8460 / 8461 + a single dated 2024-rules note), clean seams.

### 2. browser-extension-engineering — **BUILD NOW**

- **Purpose / value.** Build, ship, and maintain cross-browser extensions on
  Manifest V3: service-worker background scripts (and the MV2→MV3 lifecycle
  trap), content-script isolation + messaging, the permissions/host-permissions
  model and least-privilege review posture, storage, the Chrome Web Store / Edge
  Add-ons / Firefox AMO review pipelines, and the WebExtensions cross-browser
  delta (Chrome vs Firefox `browser.*` promises). A clear sibling to the existing
  `desktop-app-engineering` and `frontend-engineering` plugins.
- **Boundary.** `frontend-engineering` owns app-grade React UI; this owns the
  *extension runtime + manifest + store* surface. `security-engineering` owns
  security *verdicts*; this owns the extension-specific least-privilege posture
  and escalates verdicts.
- **Approach.** 2 agents (extension-architect, extension-implementation-engineer),
  skills for a manifest/permissions audit and a store-submission readiness check,
  a knowledge bank (MV3 architecture + a permissions-minimization decision tree +
  a dated cross-browser capability note).
- **Why second.** High feasibility, low accuracy-risk (MV3 is a stable published
  spec), fills the obvious engineering-cluster sibling gap.

### 3. gis-geospatial-engineering — Next

- **Purpose.** Spatial data done right: coordinate systems/projections (EPSG,
  WGS84 vs Web Mercator), PostGIS spatial SQL + indexing (GiST), vector/raster
  formats (GeoJSON, GeoParquet, COG, vector tiles/MVT), and map rendering
  (MapLibre/Leaflet) at a selection level. Used across precision-ag, fleet,
  field-service, real-estate, public-sector — none of which own the GIS layer.
- **Boundary.** Deepens (does not replace) `database-engineering` (PostGIS is a
  spatial extension of the OLTP layer it already covers) and the verticals that
  *consume* maps. Approach: 2 agents + projection/format/index decision trees.
  Low accuracy-risk (OGC/EPSG standards are stable).

### 4. servicenow-itsm — Next (live-verify first)

- **Purpose.** ServiceNow platform/ITSM: the data model (CMDB, tables, ACLs),
  scripting (Business Rules, Script Includes, GlideRecord, Flow Designer),
  integration (IntegrationHub, REST/import sets), and ITIL process config
  (incident/problem/change/request). Large enterprise demand; no current plugin.
- **Accuracy-risk note.** ServiceNow releases (Xanadu/Yokohama-style names),
  licensing, and Now Assist AI shift fast — author with live `microsoft-learn`-
  style verification and dated capability notes, like `ai-coding-model-guidance`.

### 5. hubspot-operations — Backlog

- **Purpose.** HubSpot CRM/Marketing/Sales/Ops Hub admin + dev: properties,
  workflows, the associations data model, HubL/serverless, the v3 API, and
  RevOps config. `data-platform` references HubSpot only as a *source*; `salesforce`
  is the only CRM-platform plugin. Med-high accuracy-risk (platform evolves).

### 6. jira-atlassian-admin — Backlog

- **Purpose.** Jira/Confluence administration: JQL, workflow/scheme design,
  automation rules, ScriptRunner, and the Forge/Connect app surface.
  `project-management` owns *methodology*; this owns the *Atlassian platform*.

### 7. shopify-app-engineering — Backlog

- **Purpose.** Shopify *developer* surface: app architecture (embedded apps,
  App Bridge, Polaris), the Admin GraphQL API + webhooks, Shopify Functions,
  theme/Liquid, and the app-store review path. `ecommerce-dtc` owns *operations*;
  this owns the *build*.

### 8. trust-and-safety-operations — Backlog

- **Purpose.** Content moderation + platform integrity: policy taxonomy design,
  moderation workflows + queues, abuse/fraud signal design, appeals, and
  transparency reporting (DSA/-style). Growing demand; med accuracy-risk
  (regulation shifts). Seams to `data-governance-privacy`, `cybersecurity-grc`.

### 9. wordpress-cms-engineering — Backlog

- **Purpose.** WordPress/headless-CMS engineering: theme/block (Gutenberg)
  development, plugin development + hooks, the REST API + headless patterns,
  performance/caching, and security hardening. Distinct from `web-design`
  (brand/UX) and `frontend-engineering` (app-grade React).

### 10. devrel-developer-experience — Backlog

- **Purpose.** Developer relations + DX: developer-onboarding funnels, sample
  apps + SDK ergonomics, API docs *as a product* (pairs with
  `technical-writing-docs`/`api-engineering`), community + advocacy, and DX
  metrics (time-to-first-call, activation). Low accuracy-risk.

## Build status in this PR

- **email-deliverability-engineering** — built (initial v0.1.0): 2 agents,
  2 skills, knowledge bank, best-practices. Wired into `marketplace.json` and
  `docs/architecture.md`.
- **browser-extension-engineering** — built (initial v0.1.0): 2 agents,
  2 skills, knowledge bank, best-practices. Wired into `marketplace.json` and
  `docs/architecture.md`.
- Candidates 3–10 remain a sequenced backlog (this doc). Candidate 3
  (gis-geospatial-engineering) is the recommended next build — same low
  accuracy-risk profile as the two shipped here.

## Blockers / notes

- None blocked the two builds. The SaaS-platform candidates (4–7) deliberately
  sit lower in the queue: they carry **high accuracy-risk** (volatile platform
  releases/licensing/AI features) and per this repo's accuracy discipline must be
  authored with live web verification + dated, re-verify-at-use capability notes
  rather than from training knowledge. Building them unattended without that
  verification step would risk shipping confidently-wrong platform facts.
