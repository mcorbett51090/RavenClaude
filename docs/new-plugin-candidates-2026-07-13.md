# New-plugin research & buildout — 2026-07-13

> Scheduled-routine deliverable: research 10 net-new plugins for the RavenClaude
> marketplace, prioritize them, and build the highest-priority ones. This doc is
> the research + prioritization record; the buildout ships in the same PR.
>
> **Last reviewed:** 2026-07-13 · **Author:** automated routine (Claude Code on the web)

## Method

The marketplace already ships **154 plugins** spanning engineering disciplines,
industry verticals, and knowledge-work functions. The prior wave (2026-07-09,
PR #603) landed all ten of that cycle's candidates — `ai-red-teaming`,
`technical-seo-engineering`, `self-storage-operations`, `funeral-home-operations`,
`grants-management`, `bioinformatics-engineering`, `waste-recycling-operations`,
`audio-dsp-engineering`, `digital-twin-engineering`,
`museum-cultural-institution-operations` — so this cycle had to find **genuinely
new gaps**.

Each candidate was checked against the full `plugins/*` roster by keyword
(`urgent-care`, `community-association` / `HOA`, `chaos`, `moving` /
`relocation`, `home-health`, `tax-firm`, `catering`, `investor-relations`,
`pricing` / `monetization`, `learning-development`) — **all twelve keyword
probes returned zero dedicated plugins** — and, where a near-neighbor existed, a
boundary was drawn against it (e.g. urgent-care vs `medical-revenue-cycle`'s
billing focus; community-association vs `property-management`'s residential
leasing; chaos-resilience vs `observability-sre`'s monitoring; moving vs
`fleet-logistics`'s generic telematics).

Feasibility note: every candidate is a **knowledge/advisory plugin** in the house
pattern (2 agents on a *decide/architect* vs *build/run* seam + a decision-tree
knowledge bank + skills + templates). None requires a bundled MCP server or
runtime, so all ten are buildable to the marketplace's shipping bar within this
routine. Several were pre-scoped in the 2026-07-04 roadmap backlog
(`community-association-management` P4, `urgent-care-operations` P6,
`chaos-resilience-engineering` P7, `moving-relocation-operations` P9) and are
promoted here.

## The 10 candidates

| # | Plugin | Category | Gap it fills | Nearest neighbor (boundary) |
|---|---|---|---|---|
| 1 | `urgent-care-operations` | Vertical | Walk-in/episodic care center ops — door-to-door throughput, provider staffing to demand curves, payer/occ-med contracting, POCT, ancillary (x-ray/labs), split-flow | `medical-revenue-cycle` (billing/AR), `behavioral-health-practice` (clinical), `medical-revenue-cycle` for coding |
| 2 | `community-association-management` | Vertical | HOA/COA board-fiduciary ops — assessments & reserve studies, CC&R/covenant enforcement, meetings/elections, vendor management for a volunteer board | `property-management` (owner/tenant leasing), `commercial-real-estate` (asset investment) |
| 3 | `chaos-resilience-engineering` | Eng | Fault injection, game days, failure-mode analysis, steady-state hypotheses, blast-radius control, resilience SLOs | `observability-sre` (monitoring/on-call), `performance-engineering` (throughput), `qa-test-automation` (functional) |
| 4 | `moving-relocation-operations` | Vertical | Moving-company ops — cube-sheet estimating, crew/truck dispatch, DOT/FMCSA tariff & valuation, claims, local vs interstate vs corporate relo | `fleet-logistics` (generic telematics), `field-service-management` (dispatch), `freight-forwarding-sales` (freight) |
| 5 | `home-health-agency-operations` | Vertical | Medicare-certified home health — PDGM episode economics, OASIS accuracy, CMS Conditions of Participation, LUPA thresholds, referral/intake, visit utilization | `hospice-referral-sales` (hospice sales), `senior-care-operations` (facility care), `medical-revenue-cycle` (billing) |
| 6 | `tax-firm-operations` | Vertical | Tax-prep/advisory practice — busy-season capacity, engagement/pricing mix (1040 vs advisory), extension strategy, IRS e-file/PTIN/Circular 230, review workflow | `accounting-bookkeeping` (books/close), `wealth-management-ria` (investment advice), `finance` (corporate) |
| 7 | `catering-events-operations` | Vertical | Off-premise catering & commercial food service — event costing/BEO, production capacity, staffing ratios, rentals, food-cost %, proposal-to-execution | `restaurant-operations` (on-premise dining), `event-management` (event production), `hotel-hospitality-operations` (banquets) |
| 8 | `investor-relations` | Function | Public-company IR — earnings cycle, guidance, Reg FD, shareholder targeting, sell-side coverage, the IR calendar, perception studies | `startup-fundraising` (private/VC rounds), `finance` (FP&A/close), `product-management` |
| 9 | `pricing-monetization-strategy` | Function | Product/SaaS pricing — value metric, packaging/tiering, price-model choice (seat/usage/hybrid), willingness-to-pay research, discounting discipline, price change rollout | `sales-revops` (quota/comp/pipeline), `product-management` (roadmap), `finance` (unit economics) |
| 10 | `learning-development-operations` | Function | Corporate L&D — skills taxonomy, program design (70-20-10), needs analysis, LMS/LXP, measurement (Kirkpatrick), compliance training, onboarding curricula | `people-operations-hr` (HR generalist), `edtech-partner-success` (EdTech vendor), `developer-relations` (external community) |

## Prioritization rationale

Ranked by **user demand × technical feasibility**. All ten are feasible (same
house pattern, no runtime); the axis that separates them is demand + strategic
fit + how clean the seam is against the nearest existing plugin (a messy seam
raises authoring risk and confuses routing).

- **P0 — build first (highest demand, cleanest seam):**
  1. `urgent-care-operations` — one of the fastest-growing care-delivery formats; the marketplace has ~12 healthcare-practice verticals but none for the walk-in/episodic-throughput model. High demand, well-documented operating economics (door-to-door time, provider-hour productivity, payer mix).
  2. `community-association-management` — HOA/COA management is a large, fragmented industry; `property-management` covers residential *leasing*, not board *fiduciary* operations (reserves, CC&R enforcement, elections). Clean, well-bounded gap already scoped as roadmap P4.
  3. `chaos-resilience-engineering` — resilience/chaos engineering is a mainstream reliability discipline in 2026; `observability-sre` covers *detecting* failure, not *deliberately inducing* it to prove resilience. Broad engineering reuse.
  4. `moving-relocation-operations` — clean SMB vertical with a crisp regulatory spine (DOT/FMCSA tariff, valuation, released-vs-full-value liability) and zero overlap; roadmap P9.

- **P1 — build next (real demand, slightly narrower or seam-sensitive):**
  5. `home-health-agency-operations` — large Medicare-funded sector with distinctive economics (PDGM, OASIS, LUPA); seam vs `hospice-referral-sales` and `senior-care-operations` must be drawn carefully.
  6. `tax-firm-operations` — broad SMB reach, but the seam vs `accounting-bookkeeping` needs a clear "busy-season practice vs year-round books" boundary.
  7. `catering-events-operations` — solid vertical; seam vs `restaurant-operations` and `event-management` is real but drawable (off-premise production + BEO economics).

- **P2 — build to complete the set (narrower or higher seam risk):**
  8. `investor-relations` — genuine function gap (public-company IR ≠ private fundraising), but a narrower audience than the verticals above.
  9. `pricing-monetization-strategy` — high-value and broadly wanted, but overlaps `sales-revops`, `product-management`, and `finance` at the edges, so the seam-carving is the main authoring risk.
  10. `learning-development-operations` — real function gap, but the seam vs `people-operations-hr` must be explicit to avoid routing ambiguity.

## Implementation approach (per plugin) & dependencies

Each plugin follows the shipping house pattern and requires
`ravenclaude-core@>=0.7.0` (no other runtime dependency):

- `.claude-plugin/plugin.json` (semver `0.1.0`), `CLAUDE.md` (team constitution),
  `README.md`.
- **2 agents** on a *decide/architect* vs *build-run/implement* seam, each with the
  gated scenario-authoring frontmatter schema and a ≤300-char routing description.
- **2 knowledge docs** — a Mermaid decision tree + a dated `*-patterns-2026`
  reference (confidence-marked; volatile facts carry retrieval dates).
- **3 skills** (`choose/design/run`-shaped) and **2 templates**.
- Central registration: `marketplace.json` entry, `docs/architecture.md` Status
  row, README count (self-healed by `scripts/check-marketplace-claims.py --fix`).

Per-plugin agent seams and the regulated/flag-to-a-professional surfaces:

- **urgent-care-operations** — `urgent-care-operations-lead` (throughput/split-flow, provider staffing to the demand curve, ancillary services, multi-site) + `urgent-care-revenue-and-payer-specialist` (payer & occ-med contracting, visit-level economics, self-pay/transparency, coding accuracy handed to `medical-revenue-cycle`). Clinical decisions and coding/billing determinations flag out.
- **community-association-management** — `association-management-lead` (budget, assessments, reserve funding, vendor management, meetings) + `governance-and-covenant-specialist` (board governance/elections, CC&R enforcement, collections ladder). Reserve-study adequacy, fair-enforcement, and collections law flag to a professional.
- **chaos-resilience-engineering** — `resilience-architect` (steady-state hypotheses, failure-mode analysis, blast-radius design, resilience SLOs, GameDay program) + `chaos-experiment-engineer` (fault-injection tooling, experiment automation, safety/abort, production-vs-staging). Nothing runs against a live system without a stated blast-radius + abort.
- **moving-relocation-operations** — `moving-operations-lead` (estimating/cube sheet, crew & truck dispatch, capacity, local vs long-distance vs corporate relo) + `moving-compliance-and-claims-specialist` (DOT/FMCSA tariff & valuation, released-vs-full-value liability, claims, licensing). Tariff/licensing/liability flag as regulated, not legal advice.

## Progress

**Built in the accompanying PR (P0):** `urgent-care-operations`,
`community-association-management`, `chaos-resilience-engineering`,
`moving-relocation-operations` — each to the shipping house pattern (2 agents,
2-doc knowledge bank, 3 skills, 2 templates), registered in `marketplace.json`
and `docs/architecture.md`, with the README count self-healed.

**Backlog (P1–P2, scoped here for a following cycle):**
`home-health-agency-operations`, `tax-firm-operations`,
`catering-events-operations`, `investor-relations`,
`pricing-monetization-strategy`, `learning-development-operations`.

See the PR for the final gate results. Blockers, if any, are recorded in the PR
description.
