# New plugin candidates — research & prioritization (2026-07-21)

> **Status:** research deliverable for the scheduled "identify + build 10 new plugins" routine.
> **Method:** enumerated the existing 167-plugin roster (`plugins/`), reasoned about coverage gaps across the marketplace's four clusters (software-delivery, cloud, data/AI, business/product verticals), and cross-checked each candidate's keywords against every plugin `README.md` to confirm it is a genuine gap rather than an incidental mention.
> **Outcome of this run:** the top 2 technical-gap candidates were built to gate-passing standard (`subscription-billing-engineering`, `recommendation-systems-engineering`). The remaining 8 are specced here for follow-up builds.

---

## Why these are gaps (verification)

The marketplace already covers an enormous surface. Each candidate below was checked to be **distinct** from the nearest existing plugin, with the seam stated explicitly. Incidental term matches (e.g. "we recommend…", "monthly subscription" in a vertical's pricing note) were discounted — a gap means there is no *dedicated* plugin owning the domain.

| Nearest existing plugin(s) | Why the candidate is still distinct |
|---|---|
| `pricing-monetization` (pricing *strategy*), `fintech-payments-engineering` (payment *rails*) | Neither owns the **recurring-billing system** — Stripe Billing, metering, proration, dunning, revrec, tax. |
| `ml-engineering` (broad MLOps), `search-relevance-engineering` (search) | Neither owns **recommender systems** — candidate-gen → ranking → re-rank, embeddings, cold-start, recsys eval. |
| `mobile-engineering` (client push receipt), `email-engineering` (email channel) | Neither owns the **multi-channel notification platform** — orchestration across push/SMS/in-app/email, preferences, delivery. |
| `computer-vision-engineering`, `technical-writing-docs` | Neither owns **intelligent document processing** — OCR, layout parsing, extraction, human-in-the-loop review. |
| `ml-engineering`, `llm-evaluation-engineering` | Neither owns **data-labeling operations** — label schema, annotation QA, inter-annotator agreement, active learning. |
| `regulatory-compliance` (KYC *policy*), `auth-identity` (login) | Neither owns **IDV integration engineering** — Persona/Onfido/Stripe Identity, liveness, document verification. |
| `marketing-operations` (the *function*) | Doesn't own **running an agency** — client services, retainers/SOWs, media buying, utilization/margin. |
| `renewable-energy` (generation projects) | Doesn't own **regulated utility operations** — grid/outage, AMI metering, rate cases, SAIDI/SAIFI. |
| `freight-forwarding-sales`, `fleet-logistics` | Neither owns **airline/airport operations** — crew legality, OCC, MRO, SMS, IROPS recovery. |
| `network-engineering` (enterprise network) | Doesn't own **carrier OSS/BSS** — provisioning/activation, order mgmt, mediation/rating, NOC. |

---

## The 10 candidates

### P1 — `subscription-billing-engineering`  ✅ built this run
**Purpose/value.** The recurring-billing system layer for SaaS: model plans/tiers/add-ons, implement usage-based & metered billing, get proration/upgrades/downgrades right, run dunning & involuntary-churn recovery, reconcile webhooks idempotently, and keep revenue recognition + sales tax/VAT correct. This is the single most-requested "money plumbing" gap for product teams — every SaaS hits it, and getting proration or webhook idempotency wrong loses real revenue.
**Implementation approach.** 2 agents (`billing-systems-architect`, `billing-implementation-engineer`); skills for plan/price modeling, metering & usage-based billing, and dunning/recovery; knowledge docs with a Mermaid billing-model decision tree + a webhook/idempotency & revrec reference; templates for a billing-integration runbook and a proration/upgrade test matrix.
**Dependencies.** `ravenclaude-core@>=0.7.0`. Seams: payment rails → `fintech-payments-engineering`; pricing strategy → `pricing-monetization`; revrec accounting → `finance`; tax compliance → `regulatory-compliance`.
**Feasibility.** High — well-documented public domain (Stripe Billing, RFC-style webhook patterns).

### P2 — `recommendation-systems-engineering`  ✅ built this run
**Purpose/value.** The recsys layer: turn behavioral/interaction data into a candidate-generation → ranking → re-ranking pipeline, choose collaborative-filtering vs content vs hybrid vs two-tower, handle cold-start, evaluate offline (recall@k, nDCG) *and* online (A/B), and serve within latency. Distinct from generic MLOps and from search relevance.
**Implementation approach.** 2 agents (`recsys-architect`, `recsys-implementation-engineer`); skills for approach selection, offline+online evaluation, and cold-start/serving; knowledge docs with a Mermaid approach-selection tree + an eval-metrics & serving reference; templates for a recsys design doc and an eval report.
**Dependencies.** `ravenclaude-core@>=0.7.0`. Seams: training infra/feature store → `ml-engineering`; keyword/semantic search → `search-relevance-engineering`; experiment design → `experimentation-growth-engineering` / `applied-statistics`.
**Feasibility.** High.

### P3 — `notifications-messaging-engineering`
**Purpose/value.** The multi-channel notification platform: orchestrate push (APNs/FCM), SMS (Twilio/SNS), in-app, and email as one system — user preferences & quiet hours, templating/localization, delivery guarantees (retry, idempotency, dedupe), digesting/batching, and deliverability per channel.
**Implementation approach.** 2 agents (notification-platform-architect, notification-delivery-engineer); skills for channel-strategy, preference/consent modeling, delivery reliability; knowledge docs (channel-selection tree + delivery-semantics reference); 2 templates.
**Dependencies.** `ravenclaude-core`. Seams: email deliverability → `email-engineering`; device push receipt → `mobile-engineering`; queues/workers → `backend-engineering`.
**Feasibility.** High.

### P4 — `document-processing-engineering` (IDP)
**Purpose/value.** Intelligent document processing: OCR, PDF/layout parsing, field extraction (LLM + layout models), classification, confidence thresholds + human-in-the-loop review, and accuracy evaluation. High demand as teams automate invoices/contracts/forms.
**Implementation approach.** 2 agents (idp-architect, extraction-engineer); skills for pipeline design, extraction-and-validation, HITL review design; knowledge docs (technique-selection tree + accuracy/eval reference); 2 templates.
**Dependencies.** `ravenclaude-core`. Seams: vision models → `computer-vision-engineering`; LLM extraction prompts → `claude-app-engineering`; storage → cloud plugins.
**Feasibility.** Medium-high.

### P5 — `data-annotation-labeling`
**Purpose/value.** ML data-labeling operations: label schema & guidelines, tooling (Label Studio/CVAT/Argilla), quality (gold sets, inter-annotator agreement, adjudication), active learning, LLM-assisted pre-labeling, and workforce management.
**Implementation approach.** 2 agents (labeling-ops-lead, annotation-quality-engineer); 3 skills; knowledge docs (tooling tree + IAA/quality reference); 2 templates.
**Dependencies.** `ravenclaude-core`. Seams: model training → `ml-engineering`; eval sets → `llm-evaluation-engineering`.
**Feasibility.** Medium.

### P6 — `identity-verification-idv`
**Purpose/value.** KYC/IDV integration engineering: Persona/Onfido/Stripe Identity, document verification, liveness/selfie, sanctions/PEP screening integration, reusable KYC, fallback/step-up flows. Distinct from compliance policy and from login.
**Implementation approach.** 2 agents (idv-architect, idv-integration-engineer); 3 skills; knowledge docs (vendor/flow-selection tree + verification-signals reference); 2 templates.
**Dependencies.** `ravenclaude-core`. Seams: KYC/AML policy → `regulatory-compliance`; authentication → `auth-identity`; fraud → `trust-and-safety`.
**Feasibility.** Medium.

### P7 — `marketing-agency-operations`
**Purpose/value.** Running a marketing/creative agency: client services, retainers/SOWs, scoping & pricing, media buying, campaign delivery, utilization/margin, and client reporting. Business-vertical gap (the *function* is `marketing-operations`).
**Implementation approach.** 2 agents (agency-operations-lead, client-services-manager); 3 skills; knowledge (retainer/pricing tree + agency-economics reference); 2 templates.
**Dependencies.** `ravenclaude-core`. Seams: the marketing function → `marketing-operations`; PM → `project-management`.
**Feasibility.** Medium.

### P8 — `energy-utilities-operations`
**Purpose/value.** Regulated electric/gas/water utility operations: grid/outage management, AMI/smart metering, rate cases, demand response, DER/interconnection, reliability metrics (SAIDI/SAIFI), and regulatory compliance. Distinct from `renewable-energy` (generation projects).
**Implementation approach.** 2 agents (utility-operations-lead, grid-reliability-analyst); 3 skills; knowledge (reliability/rate-case reference + a decision tree); 2 templates.
**Dependencies.** `ravenclaude-core`. Seams: generation → `renewable-energy`; ESG → `esg-sustainability-reporting`.
**Feasibility.** Medium (regulatory specifics volatile + jurisdictional → retrieval-dated).

### P9 — `aviation-airline-operations`
**Purpose/value.** Airline/airport operations: crew scheduling & legality, flight ops/OCC, MRO/maintenance, safety management systems (SMS), IROPS recovery, turnaround, slots.
**Implementation approach.** 2 agents (flight-operations-lead, crew-and-maintenance-planner); 3 skills; knowledge (SMS + IROPS references + a decision tree); 2 templates.
**Dependencies.** `ravenclaude-core`. Seams: logistics → `fleet-logistics`.
**Feasibility.** Medium-low (specialized, safety-regulated → advisory framing).

### P10 — `telecom-carrier-operations`
**Purpose/value.** CSP/carrier OSS/BSS: service provisioning/activation, order management, network inventory, mediation/rating/billing, NOC ops, SLA, number management. Distinct from enterprise `network-engineering`.
**Implementation approach.** 2 agents (oss-bss-architect, service-provisioning-engineer); 3 skills; knowledge (OSS/BSS reference + a decision tree); 2 templates.
**Dependencies.** `ravenclaude-core`. Seams: enterprise network → `network-engineering`; billing patterns → `subscription-billing-engineering` (P1).
**Feasibility.** Medium-low.

---

## Prioritization rationale

**Ranking axis 1 — consumer fit.** The marketplace's installed base skews developer/technical (the software-delivery, cloud, and data/AI clusters are the deepest). Technical-gap plugins (P1–P6) therefore outrank the business verticals (P7–P10) on expected demand.

**Ranking axis 2 — gap cleanliness.** P1 and P2 own a domain with a *strong, single, unambiguous seam* to an existing plugin (billing vs payment-rails; recsys vs search/MLOps). Clean seams make the plugin easy to route to and hard to duplicate — the two best-scoped builds.

**Ranking axis 3 — feasibility.** P1–P3 rest on well-documented public domains (Stripe Billing, recsys literature, notification platforms), so they can be built to the repo's citation-grounded bar without speculative claims. The verticals (P8–P10) carry volatile/jurisdictional specifics that must be retrieval-dated and framed advisory — higher authoring cost per unit of confidence.

**Result:** build **P1 → P2** this run; P3–P6 next (technical, high feasibility); P7–P10 as vertical follow-ups.

**Scope note (blocker, stated honestly).** Each plugin in this marketplace is a substantial, multi-file, CI-gated artifact (agents with full scenario-authoring frontmatter, knowledge banks, best-practices, templates, three registry updates, and five CI gates). Building all 10 to that bar in a single unattended run would risk shipping gate-failing or thin content. The responsible increment is to build the two highest-priority candidates *correctly and green*, and leave the remaining eight fully specced above for follow-up PRs.
