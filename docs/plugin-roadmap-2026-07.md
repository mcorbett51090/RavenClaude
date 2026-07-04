# Plugin roadmap — 10 candidate plugins (2026-07)

> Research + prioritization for the next wave of RavenClaude plugins. Compiled 2026-07-04 by `claude` (scheduled routine). The marketplace already ships **131 plugins**; this doc identifies **10 genuinely uncovered gaps**, each verified against the existing catalog (no dedicated plugin exists for any of the ten), with a purpose/value note, an implementation approach, dependencies, and a priority.
>
> **Two of the ten are built in the accompanying PR** (P1 `med-spa-aesthetics`, P2 `craft-beverage-operations`). The remaining eight are scoped here as the backlog, ordered by priority.

---

## How the gaps were found

Enumerated all 131 `plugins/*` entries in `.claude-plugin/marketplace.json`, then grep-checked candidate keywords across every plugin's `*.md` / `*.json`. A candidate qualified as a gap only when **no dedicated plugin** covers it and the incidental keyword hits were in unrelated plugins (e.g. "HOA" appears inside `property-management`, "aesthetic" inside `web-design`/`salon-spa` — neither is a dedicated med-spa or community-association plugin).

Every candidate reuses one of two **proven, gate-passing templates** already in the repo, which is what makes them feasible:

- **SMB vertical-ops template** (3 agents, 4–5 skills, decision-tree knowledge bank + dated `*-reference-2026.md`, 5 best-practices, 2 templates, 2 commands) — e.g. `salon-spa-operations`, `restaurant-operations`, `veterinary-practice`. 8 of the 10 candidates use this.
- **Engineering-team template** (3–4 agents, skills, decision-tree knowledge bank, best-practices, templates, commands) — e.g. `ar-vr-xr-engineering`, `performance-engineering`. 2 of the 10 candidates use this.

All candidates depend on `ravenclaude-core@>=0.7.0` and add **no new top-level directories** (so `.repo-layout.json` needs no change) and **no runtime code** (markdown + JSON manifests only — no new CI risk).

---

## Prioritization rationale

Ranked on two axes:

- **Demand** — size of the addressable operator/practitioner base and how underserved it is by generic tooling.
- **Feasibility** — how cleanly the candidate maps onto an existing template (lower authoring risk, higher gate-pass confidence) and how little overlap it has with an existing plugin (overlap forces awkward seam-carving).

| # | Candidate | Template | Demand | Feasibility | Priority |
|---|---|---|---|---|---|
| 1 | **med-spa-aesthetics** | SMB vertical-ops | High (fast-growing sector) | High (zero overlap, clean fit) | **P1 — built** |
| 2 | **craft-beverage-operations** | SMB vertical-ops | High (large SMB category) | High (zero overlap) | **P2 — built** |
| 3 | **self-storage-operations** | SMB vertical-ops | High (large asset class) | High (zero overlap) | P3 |
| 4 | **community-association-management** | SMB vertical-ops | High (HOA/COA ubiquity) | Med (seam vs property-management) | P4 |
| 5 | **media-streaming-engineering** | Engineering-team | Med-High | High (zero overlap) | P5 |
| 6 | **urgent-care-operations** | SMB vertical-ops | Med-High | Med (seam vs medical-revenue-cycle) | P6 |
| 7 | **chaos-resilience-engineering** | Engineering-team | Med | Med (seam vs observability-sre) | P7 |
| 8 | **franchise-multi-unit-operations** | SMB vertical-ops | Med | Med (seam vs retail/restaurant) | P8 |
| 9 | **moving-relocation-operations** | SMB vertical-ops | Med | High (zero overlap) | P9 |
| 10 | **funeral-home-operations** | SMB vertical-ops | Med | High (zero overlap) | P10 |

The two built first (P1/P2) are the highest-demand candidates that **also** have zero overlap and the cleanest template fit — the combination that maximizes value-per-authoring-risk in an unattended build.

---

## The ten candidates

### P1 — med-spa-aesthetics `[BUILT]`

- **Purpose / value.** A medical-aesthetics practice (med spa) is a hybrid of a medical practice and a retail/service business — injectables, energy devices, skincare retail, memberships — and neither `salon-spa-operations` (non-medical) nor `dental-practice` nor `medical-revenue-cycle` fits it. The distinctive economics: the **consult is the conversion point**, treatment revenue rebooks on a **clinical cadence** (neuromodulators every ~3–4 months), and every service sits under a **scope-of-practice / medical-supervision** structure that is a medical-director/legal call, not an ops choice.
- **Implementation.** SMB vertical-ops template. 3 agents: `med-spa-operations-lead` (room/injector utilization, service mix across injectables/devices/skincare/memberships, device payback, pricing per provider-hour), `patient-coordinator-lead` (consult-to-treatment conversion, booking, no-show/deposit, cadence rebooking, membership), `aesthetics-compliance-advisor` (scope of practice, good-faith exam / supervision structure, consent & adverse-event protocols — flags to a licensed professional). 4 skills, decision-tree bank + `med-spa-reference-2026.md`, 5 best-practices, 2 templates, 2 commands.
- **Dependencies.** `ravenclaude-core@>=0.7.0`. No PII; no medical or legal determinations (flag-only).

### P2 — craft-beverage-operations `[BUILT]`

- **Purpose / value.** Winery / brewery / distillery — production + tasting-room DTC + three-tier distribution. Zero coverage (closest is `cannabis-operations`, a different regulatory and product world). The distinctive economics: **DTC margin beats wholesale but doesn't scale like it**, the **club/membership** is the recurring-revenue engine, **COGS-per-unit** hides in yield and packaging, capacity is **tanks/barrels/time**, and the **three-tier system + TTB/state licensing + excise** is a professional/legal call.
- **Implementation.** SMB vertical-ops template. 3 agents: `craft-beverage-operations-lead` (production planning, COGS/yield, tank/barrel capacity, channel margin mix), `tasting-room-and-club-manager` (tasting-room throughput/conversion, club revenue & churn, DTC, events), `beverage-distribution-compliance-advisor` (three-tier vs self-distribution economics, distributor relationships, TTB/state licensing & excise concepts — flags to a licensed professional). 4 skills, decision-tree bank + `craft-beverage-reference-2026.md`, 5 best-practices, 2 templates, 2 commands.
- **Dependencies.** `ravenclaude-core@>=0.7.0`. No PII; licensing/excise flagged, not decided.

### P3 — self-storage-operations

- **Purpose / value.** Self-storage is a large, fragmented asset class with distinctive operations: **unit-mix revenue management** (ECRI — existing-customer rate increases), occupancy vs street-rate trade-offs, **lien/auction** on delinquency, kiosk/automation and remote management, ancillary revenue (insurance/protection plans, retail). `property-management` covers residential/commercial *leasing* — not the revenue-management, delinquency-to-auction, and unit-mix mechanics of storage.
- **Implementation.** SMB vertical-ops template. 3 agents: `storage-operations-lead` (occupancy, unit-mix & street rate, ECRI, ancillary revenue), `revenue-and-delinquency-manager` (dynamic pricing, delinquency ladder, lien/auction workflow, discounts/promos), `facility-and-automation-advisor` (kiosk/remote ops, security, maintenance, multi-facility). Skills: unit-mix-and-street-rate, ecri-and-dynamic-pricing, delinquency-to-lien-workflow, ancillary-revenue. Lien/auction law and insurance-product rules flag to a professional.
- **Dependencies.** `ravenclaude-core@>=0.7.0`.

### P4 — community-association-management (HOA / COA)

- **Purpose / value.** HOA / condo-association management is distinct from rental property management: **board governance**, **assessments & reserve studies**, **covenant (CC&R) enforcement**, meetings/elections, and vendor management on behalf of a volunteer board. Huge installed base of associations; `property-management` targets owner/tenant leasing, not board fiduciary operations.
- **Implementation.** SMB vertical-ops template. 3 agents: `association-management-lead` (budget, assessments, reserve funding, vendor management), `governance-and-compliance-coordinator` (board meetings/elections, CC&R/covenant enforcement, notices), `homeowner-relations-manager` (violations, ARC requests, dues collections, communications). Reserve-study adequacy, fair-enforcement, and collections law flag to a professional.
- **Dependencies.** `ravenclaude-core@>=0.7.0`. Seam note vs `property-management` documented in both CLAUDE.md files.

### P5 — media-streaming-engineering

- **Purpose / value.** Video/audio delivery engineering — **encoding/transcoding** (codecs, ABR ladders), **packaging** (HLS/DASH/CMAF), **DRM**, **CDN** delivery, **live/low-latency** pipelines, and **QoE** (quality-of-experience) measurement. Zero coverage — `film-video-production` is production *operations*, not the streaming stack. Real demand from any product that ships video at scale.
- **Implementation.** Engineering-team template. 3 agents: `streaming-architect-lead` (delivery architecture, codec/ABR strategy, live vs VOD, cost/quality trade-offs), `encoding-and-packaging-engineer` (transcode pipelines, ABR ladders, HLS/DASH/CMAF, DRM integration), `delivery-and-qoe-engineer` (CDN, low-latency, playback QoE, buffering/startup metrics). Decision trees: codec choice, ABR-ladder design, live-latency tier, DRM tier. Reference file dated (codec/DRM/CDN landscape volatile, verify-at-use).
- **Dependencies.** `ravenclaude-core@>=0.7.0`. Seams to `performance-engineering`, `frontend-engineering` (player), `observability-sre`.

### P6 — urgent-care-operations

- **Purpose / value.** Urgent-care / retail-clinic operations: **door-to-door throughput**, provider staffing to demand curves, **payer mix** and occupational-health/employer contracts, point-of-care testing, and multi-site standardization. `medical-revenue-cycle` covers billing/claims; it does not cover the throughput, staffing-to-demand, and occ-health-contract economics of an urgent-care front line.
- **Implementation.** SMB vertical-ops template. 3 agents: `urgent-care-operations-lead` (throughput, staffing-to-demand, capacity, multi-site), `payer-and-occhealth-manager` (payer mix, employer/occ-health contracts, self-pay pricing), `clinical-flow-and-compliance-advisor` (patient flow, POCT, protocols, scope — flags to professional). Seam to `medical-revenue-cycle` for the billing tail.
- **Dependencies.** `ravenclaude-core@>=0.7.0`.

### P7 — chaos-resilience-engineering

- **Purpose / value.** Chaos engineering & resilience: **hypothesis-driven fault-injection experiments**, **game days**, blast-radius control, steady-state definition, and resilience patterns (retries, circuit breakers, bulkheads, graceful degradation). `observability-sre` covers detection/response and `performance-engineering` covers load; neither owns the *deliberate-failure-injection* discipline.
- **Implementation.** Engineering-team template. 3 agents: `resilience-architect-lead` (resilience patterns, failure-mode analysis, blast-radius design), `chaos-experiment-engineer` (experiment design, steady-state hypotheses, fault injection, game-day runbooks), `recovery-and-continuity-engineer` (failover, backup/restore drills, DR/RTO-RPO). Decision trees: what to inject, blast-radius gating, resilience-pattern selection.
- **Dependencies.** `ravenclaude-core@>=0.7.0`. Seams to `observability-sre`, `performance-engineering`, `cloud-native-kubernetes`.

### P8 — franchise-multi-unit-operations

- **Purpose / value.** Franchisor/franchisee and multi-unit operations: **royalty/fee economics**, **brand-standard compliance & field consulting**, unit-economics roll-ups, franchise development, and multi-unit P&L. `retail-store-operations` and `restaurant-operations` are single-concept operators; the franchise layer (franchisor–franchisee relationship, FDD concepts, field-consulting cadence) is uncovered.
- **Implementation.** SMB vertical-ops template. 3 agents: `franchise-operations-lead` (unit-economics roll-up, royalty/fee model, multi-unit P&L), `brand-standards-and-field-consulting-manager` (audits, field-consulting cadence, standard compliance), `franchise-development-advisor` (development pipeline, FDD/franchise-sale concepts — flags to professional). Seam to `restaurant-operations`/`retail-store-operations` for single-unit mechanics.
- **Dependencies.** `ravenclaude-core@>=0.7.0`. FDD/franchise-law concepts flagged, not decided.

### P9 — moving-relocation-operations

- **Purpose / value.** Moving-company operations: **survey-to-estimate accuracy** (binding vs non-binding), crew/truck dispatch and utilization, **claims & valuation** (released vs full-value protection), and interstate (DOT/FMCSA) vs local compliance. `fleet-logistics` covers fleet asset ops and `field-service-management` covers dispatch generically; the estimate-accuracy → claims → valuation chain specific to household-goods moving is uncovered.
- **Implementation.** SMB vertical-ops template. 3 agents: `moving-operations-lead` (crew/truck utilization, job costing, seasonal capacity), `estimating-and-sales-manager` (survey-to-estimate, binding vs non-binding, conversion), `claims-and-compliance-advisor` (valuation/claims, DOT/FMCSA vs local — flags to professional).
- **Dependencies.** `ravenclaude-core@>=0.7.0`.

### P10 — funeral-home-operations

- **Purpose / value.** Funeral-home / mortuary operations: **at-need vs pre-need** case management, merchandise/service package economics, **FTC Funeral Rule** disclosure concepts, and facility/vehicle/staff scheduling. A real, underserved SMB category; `senior-care-operations` and `hospice-referral-sales` are adjacent but neither covers funeral-home case and merchandise operations. Sensitive domain — the plugin is operations/financial decision-support only, flags all regulatory/consumer-protection calls to a professional, and stores no decedent/family PII.
- **Implementation.** SMB vertical-ops template. 3 agents: `funeral-home-operations-lead` (case volume, merchandise/package mix, facility/vehicle/staff scheduling), `preneed-and-family-services-manager` (pre-need funding, at-need conversion, aftercare), `funeral-compliance-advisor` (FTC Funeral Rule disclosure concepts, general-price-list structure — flags to professional).
- **Dependencies.** `ravenclaude-core@>=0.7.0`. No PII; regulatory calls flagged.

---

## Strong alternates (not in the top 10, noted for a later pass)

`computer-vision-engineering` and `recommender-systems-engineering` (both partially shadowed by `ml-engineering`/`search-relevance-engineering`), `credit-union-community-bank-operations`, `catering-operations`, `pest-control-operations`, and platform-admin verticals mirroring `salesforce` (`servicenow-development`, `hubspot-operations`, `netsuite-administration`, `workday-hris-administration`). These were ranked below the top 10 on either higher overlap or thinner demand, but are viable future candidates.

---

## Blockers / notes

- **No hard blockers hit** during research or the P1/P2 build. GitHub PR creation uses the sanctioned MCP path (`gh`/direct-API are unavailable in this environment, per `CLAUDE.md`).
- **Scope honesty:** all ten to full quality in one unattended run would dilute the repo's citation/cross-reference bar, so P1/P2 are built completely (gate-passing) and P3–P10 are scoped here as the backlog. Each backlog item is a known-good template instantiation — the authoring risk is low, the work is volume.
- Every built/planned plugin is **operations or engineering decision-support**, stores **no PII**, and **flags** (never decides) legal/tax/clinical/regulatory questions — consistent with the marketplace's standing scope discipline.

_Last reviewed: 2026-07-04 by `claude` (scheduled routine)._
