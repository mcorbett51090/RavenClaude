# Plugin roadmap — 10 candidate plugins (2026-06-18)

> Research output for the "identify 10 new plugins" routine. Every candidate below was
> checked against the **101 plugins already shipping** under `plugins/` and confirmed to be a
> genuine gap (not a rename of, or a thin overlap with, an existing plugin). Each entry states
> its purpose + value, an implementation approach, dependencies, and a feasibility/demand read.
>
> **Status:** candidate #1 (`developer-relations`) is **built in this PR**. Candidates #2–#10 are
> specced here as the prioritized backlog. This file is the durable artifact of steps 1–4 of the
> routine; the plugin is steps 5–6.

---

## How the gaps were found

The marketplace is already dense in three clusters — the software-delivery chain, the
data/AI stack, and business/operations verticals. The gaps fall in the seams: **developer-facing
craft that isn't pure backend/frontend/docs** (DevRel, browser extensions, CLI tooling),
**specialist engineering domains with no home** (geospatial, XR, bioinformatics, quant), and a
couple of **high-volume product surfaces** (WordPress/headless CMS, Shopify apps, email
deliverability) that today get answered only generically.

A candidate had to clear three bars: (1) **not already covered** — verified absent from the
plugin directory list; (2) **a coherent, bounded craft** with its own decision trees and
anti-patterns (not "a few tips bolted onto an existing plugin"); (3) **real, recurring demand**.

---

## The 10 candidates (prioritized)

| # | Plugin | Cluster | Demand | Feasibility | Priority |
|---|---|---|---|---|---|
| 1 | `developer-relations` | Developer-facing craft | High | High | **P0 — built here** |
| 2 | `browser-extension-engineering` | App craft | High | High | P0 |
| 3 | `cli-developer-tooling` | App craft | High | High | P0 |
| 4 | `shopify-app-engineering` | App craft / commerce | High | High | P1 |
| 5 | `wordpress-cms-engineering` | App craft / CMS | High | High | P1 |
| 6 | `email-engineering-deliverability` | App craft / messaging | Med-High | High | P1 |
| 7 | `geospatial-gis-engineering` | Specialist engineering | Med | Med | P2 |
| 8 | `quant-trading-engineering` | Specialist engineering | Med | Med | P2 |
| 9 | `ar-vr-spatial-engineering` | Specialist engineering | Med | Med | P3 |
| 10 | `bioinformatics-engineering` | Specialist engineering | Med | Med | P3 |

**Prioritization rationale.** Demand × feasibility, with a tie-break toward the cleanest boundary
(least overlap risk with existing plugins) and the lowest build risk against the marketplace's
CI gate suite. The three P0s are broad-demand, well-bounded, and — being largely advisory /
markdown-shaped — buildable to the gate bar in a single pass. The P1s are equally high-demand
but each leans on a vendor surface (Shopify, WordPress, an ESP) whose volatile specifics need
dated citations, so they carry a little more authoring overhead. The P2/P3 specialist domains are
genuine gaps with narrower (but loyal) audiences; they're sequenced last because their value is
deep-not-wide and their knowledge banks are heavier to ground.

`developer-relations` is built first because it has the **broadest cross-plugin synergy**
(it seams into `technical-writing-docs`, `api-engineering`, `product-management`, and
`marketing-operations` without duplicating any of them) and is **purely advisory** — no runtime
artifact (MCP/LSP/bin) is in scope, which is exactly the shape that builds cleanly to the gate
bar, like `applied-statistics` and `staffing-operations` before it.

---

## Candidate detail

### 1. `developer-relations` (DevRel) — **built in this PR**

- **Purpose / value.** The craft of growing and serving a *developer* audience: developer
  marketing that teaches rather than sells, the developer-onboarding funnel
  (awareness → activation → advocacy) and the metrics that actually track it, sample apps and
  demos that run as shipped, conference talks / CFP abstracts, and developer-community programs.
- **Implementation.** 2 doing-agents (`devrel-strategist`, `developer-advocate`), 5 skills,
  a 4-doc knowledge bank with Mermaid decision trees (the DevRel funnel + metrics, a
  content-format / channel selection tree), 7 best-practices, 4 templates, 4 commands, 1 advisory
  hook (vanity-metric + market-at-developers + placeholder-secret smells), a scenarios bank.
- **Dependencies.** `ravenclaude-core@>=0.7.0`. Advisory only — no MCP/LSP/bin (all N-A, same as
  `applied-statistics`). Seams (not overlaps): `technical-writing-docs` owns the docs *artifact*;
  this owns the developer-*audience* growth; `api-engineering` owns the API contract; `product-management`
  owns what-to-build; `marketing-operations` owns the non-developer funnel.

### 2. `browser-extension-engineering`

- **Purpose / value.** Manifest V3 extensions across Chrome / Edge / Firefox / Safari: the
  service-worker lifecycle, content scripts and isolated worlds, the permissions/host-permissions
  model and least-privilege review, message passing, `storage` sync vs local, cross-browser via
  `webextension-polyfill`, and the store-review + publishing pipeline (the #1 reason extensions
  get rejected).
- **Implementation.** 3 agents (extension-architect, extension-implementation-engineer,
  extension-store-and-review-specialist), knowledge bank with an MV2→MV3 migration tree and a
  permissions-minimization tree, a packaging/signing template per store.
- **Dependencies.** `ravenclaude-core`. Seams: `frontend-engineering` (the UI surface),
  `auth-identity` (extension OAuth), `security-engineering` (CSP, permission review).

### 3. `cli-developer-tooling`

- **Purpose / value.** Building CLIs and developer tools people don't fight: argument parsing
  and config precedence (flag > env > file > default), TTY vs piped output, exit-code discipline,
  `--json` machine modes, shell completions, distribution (npm / Homebrew / cargo / single binary),
  plugin architectures, and consent-gated telemetry.
- **Implementation.** 2–3 agents (cli-architect, cli-implementation-engineer, distribution-and-release).
  Knowledge: a distribution-channel decision tree, a "12-factor CLI" best-practices set.
- **Dependencies.** `ravenclaude-core`. Seams: `backend-engineering`, `devops-cicd` (release),
  `technical-writing-docs` (the `--help` and man pages as docs).

### 4. `shopify-app-engineering`

- **Purpose / value.** Building Shopify *apps* (distinct from `ecommerce-dtc`, which is store
  operations): app extensions, Polaris/App Bridge, the GraphQL Admin API + rate-cost model,
  webhooks + HMAC verification, the Billing API, checkout extensibility, and Shopify app review.
- **Implementation.** 3 agents (shopify-app-architect, shopify-integration-engineer,
  shopify-review-and-billing-specialist). Knowledge: GraphQL-cost budgeting tree, embedded-vs-standalone tree.
- **Dependencies.** `ravenclaude-core`. Seams: `ecommerce-dtc` (merchant ops), `fintech-payments-engineering`
  (billing/webhooks patterns), `api-engineering` (the Admin API consumption).

### 5. `wordpress-cms-engineering`

- **Purpose / value.** The single most-deployed CMS, with no home today: block (Gutenberg) and
  theme development, the plugin API + hooks, headless WordPress (REST / WPGraphQL), performance
  and caching, security hardening, and multisite.
- **Implementation.** 3 agents (wp-architect, block-and-theme-engineer, headless-and-performance-engineer).
  Knowledge: headless-vs-traditional tree, a hardening checklist.
- **Dependencies.** `ravenclaude-core`. Seams: `frontend-engineering` (headless front end),
  `web-design`, `security-engineering`.

### 6. `email-engineering-deliverability`

- **Purpose / value.** Transactional + lifecycle email that actually lands: SPF / DKIM / DMARC /
  BIMI, domain reputation and warmup, ESP integration (SES / SendGrid / Postmark / Resend),
  template rendering across the client matrix (Outlook!), list hygiene + suppression, and
  bounce/complaint handling.
- **Implementation.** 2–3 agents (email-deliverability-engineer, email-template-engineer,
  lifecycle-automation-engineer). Knowledge: an auth-failure diagnosis tree, a deliverability triage tree.
- **Dependencies.** `ravenclaude-core`. Seams: `marketing-operations` (campaign strategy),
  `backend-engineering` (the send pipeline), `data-governance-privacy` (consent).

### 7. `geospatial-gis-engineering`

- **Purpose / value.** Spatial data and maps: PostGIS, coordinate reference systems / projections
  (the #1 source of silent bugs), vector + raster, vector tiles (MVT), geocoding + routing,
  spatial indexing, GeoJSON, and the client stack (Mapbox GL / MapLibre / Leaflet / deck.gl).
- **Implementation.** 2–3 agents (geospatial-data-engineer, mapping-frontend-engineer).
  Knowledge: a CRS/projection decision tree, a tiling-strategy tree.
- **Dependencies.** `ravenclaude-core`. Seams: `database-engineering` (PostGIS as OLTP),
  `data-platform`, `frontend-engineering`.

### 8. `quant-trading-engineering`

- **Purpose / value.** The *engineering* of systematic/quant trading systems (distinct from
  `wealth-management-ria`, which is advisory): backtesting without look-ahead/survivorship bias,
  market-data handling, order/execution management, risk limits and kill switches, and
  time-series correctness. Explicitly *not* trade advice.
- **Implementation.** 2–3 agents (quant-research-engineer, execution-and-risk-engineer).
  Knowledge: a backtest-bias checklist, an order-lifecycle tree.
- **Dependencies.** `ravenclaude-core`. Seams: `applied-statistics` (is the edge real?),
  `data-streaming-engineering` (market-data feeds), `regulatory-compliance`.

### 9. `ar-vr-spatial-engineering`

- **Purpose / value.** XR / spatial computing (distinct from `game-development`'s general gameplay
  focus): Unity/Unreal XR + WebXR + visionOS, hand/eye tracking, spatial anchors, the hard
  performance budgets (frame-time = comfort), and locomotion/comfort to avoid motion sickness.
- **Implementation.** 2 agents (xr-architect, xr-interaction-engineer). Knowledge: a platform-choice
  tree, a comfort/locomotion decision tree.
- **Dependencies.** `ravenclaude-core`. Seams: `game-development`, `mobile-engineering`, `performance-engineering`.

### 10. `bioinformatics-engineering`

- **Purpose / value.** Sequence-analysis pipelines: FASTQ/BAM/VCF, alignment + variant calling,
  workflow managers (Nextflow / Snakemake), reference-genome management, and the reproducibility
  discipline that the field lives or dies by.
- **Implementation.** 2–3 agents (bioinformatics-pipeline-engineer, genomics-data-engineer).
  Knowledge: a workflow-manager decision tree, a reproducibility checklist.
- **Dependencies.** `ravenclaude-core`. Seams: `data-science-research`, `clinical-trials`,
  `ml-engineering` (downstream modeling).

---

## Blockers / honesty notes

- **Scope.** Ten full plugins at this marketplace's quality + CI-gate bar (scenario-authoring
  schema on every agent, dated/cited knowledge banks, md-link integrity, prettier, marketplace-claims
  parity) is not achievable in a single unattended run without shipping shallow, gate-failing
  stubs. The honest split delivered here: **all 10 researched + prioritized** (steps 1–4) and
  **#1 built to completeness and verified against the gates** (steps 5–6). #2–#10 are a ready
  backlog — each one is a follow-on PR.
- **Re-verify before building each P1+.** The vendor-surface candidates (Shopify, WordPress, ESPs)
  carry volatile API specifics; their knowledge banks must be authored with retrieval dates and a
  re-verify-at-use rider, per the marketplace's claim-grounding discipline.
