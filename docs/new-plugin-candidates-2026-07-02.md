# New plugin candidates — research, prioritization & build (2026-07-02)

Research pass over the RavenClaude marketplace (**121 plugins** at time of writing) to identify
a fresh batch of **10 high-demand, technically-feasible plugin gaps** and build them out.

This continues the cadence of the prior candidate docs
([`new-plugin-candidates-2026-07-01`](new-plugin-candidates-2026-07.md) shipped
`incident-response-dfir`; `network-engineering` merged in parallel). None of the 10 picks below
collide with anything already built or with each other. Two picks (**robotics**, **AR/VR/XR**)
also appeared on the prior roadmap — treated here as consensus gaps, now built rather than
deferred.

## Method

1. Enumerated the current roster (`ls plugins/` + `.claude-plugin/marketplace.json`) — 121
   plugins across engineering specialties, cloud/data/ML, and ~50 industry verticals.
2. Mapped the white space along the two axes the marketplace already splits on —
   **engineering disciplines** and **business/vertical operations** — keeping only domains with a
   large operator base and a *durable* knowledge core distinct from the nearest existing plugin.
3. Discarded anything an existing plugin already owns (residential brokerage is **not**
   `commercial-real-estate`; the independent repair shop is **not** `automotive-dealership`; the
   settlement/title party is **not** `mortgage-lending`; higher-ed admin is **not** `k12`).
4. Scored survivors on **user demand** × **technical feasibility** (how groundable the domain is
   without a live external system).

## The 10 candidates

| # | Plugin | Purpose & value | Nearest existing (why distinct) |
|---|--------|-----------------|---------------------------------|
| 1 | `residential-real-estate-brokerage` | Residential agent/team/brokerage ops: listings, buyer/seller representation, transaction coordination, commission splits, lead-to-close pipeline. | `commercial-real-estate` (income-property underwriting — a different asset class & deal model). |
| 2 | `auto-repair-shop-operations` | Independent auto-repair / body-shop ops: service-advisor estimating, bay/technician workflow, parts, effective labor rate, comeback rate, RO lifecycle. | `automotive-dealership` (franchise sales + F&I + fixed-ops-at-scale — a different economic model). |
| 3 | `salon-spa-operations` | Salon / spa / barbershop ops: booking & no-show control, chair/booth-rent vs commission economics, retail attach, rebooking, service-menu pricing. | none — net-new SMB personal-services vertical. |
| 4 | `fitness-studio-gym-operations` | Gym / boutique-studio / wellness ops: membership growth & retention (churn, LTV), class scheduling & instructor utilization, ancillary revenue. | none — net-new. |
| 5 | `title-escrow-settlement` | Title & escrow / settlement services: title search & exam, commitment/curative, escrow & closing, CD/settlement statement, recording, wire-fraud control. | `mortgage-lending` (loan origination — settlement/title is a distinct party & workflow). |
| 6 | `childcare-early-education` | Childcare / daycare / preschool center ops: enrollment & waitlist, ratios & licensing compliance, tuition & subsidy billing, staffing, family comms. | `k12-school-administration` (public-school compliance & academics — early-childhood ops are distinct). |
| 7 | `higher-education-administration` | College/university administration: enrollment management & yield, financial aid, retention/student success, registrar, accreditation. | `k12-school-administration` (K-12) & `edtech-partner-success` (vendor CS — this is the institution's own admin). |
| 8 | `travel-agency-tour-operations` | Travel agency / tour operator ops: itinerary design, supplier & commission management, booking (GDS/BSP), group & FIT trips, service recovery. | `hotel-hospitality-operations` (a single lodging property — the agency sells across suppliers). |
| 9 | `robotics-autonomous-systems-engineering` | Robotics/autonomy engineering: ROS 2 architecture, motion planning & control, perception/state-estimation, sim-to-real, safety. | `embedded-iot-engineering` (firmware/device layer — robotics adds the autonomy/planning/perception stack). |
| 10 | `ar-vr-xr-engineering` | AR/VR/XR / spatial-computing engineering: headset & WebXR targets, interaction (hands/controllers/gaze), spatial rendering & perf budgets, comfort/safety. | `game-development` & `frontend-engineering` (XR adds spatial-tracking, comfort, device-perf discipline neither owns). |

## Implementation approach (shared)

Every plugin follows the **established domain-plugin shape** (exemplars: `optometry-eyecare-practice`,
`construction-general-contractor`):

- `.claude-plugin/plugin.json` + `README.md` + `CLAUDE.md` + `CHANGELOG.md`
- `agents/` — **3 agents** (a lead + two function specialists) with the full scenario-authoring
  frontmatter schema (`audience`, `works_with`, `scenarios[]`, `quickstart`), each `description`
  ≤ 300 chars; agent `name`s are domain-prefixed to stay globally unique.
- `skills/` — **4** SKILL.md capability files.
- `knowledge/` — a Mermaid **decision-tree** file + a **dated 2026 reference** (retrieval-dated,
  verify-at-use) so volatile figures never masquerade as durable facts.
- `best-practices/` — a README + **5** durable principle notes.
- `templates/` — **2** operator artifacts; `commands/` — **2** slash commands.
- **No bundled hooks / MCP / Python** in this batch — keeps the CI gate surface minimal; advisory
  hooks can follow in a later version bump.

Dependencies: each declares `requires: ravenclaude-core@>=0.7.0`. No external services, no secrets.
Each is added to `.claude-plugin/marketplace.json` and the `docs/architecture.md` Status table.

## Prioritization rationale

**Tier 1 — build first (highest demand × feasibility; large SMB base, durable ops knowledge, close
structural analogues to mirror):** `residential-real-estate-brokerage`, `auto-repair-shop-operations`,
`salon-spa-operations`, `fitness-studio-gym-operations`.

**Tier 2 — build next (strong demand, slightly deeper compliance/knowledge cores):**
`title-escrow-settlement`, `childcare-early-education`, `higher-education-administration`,
`travel-agency-tour-operations`.

**Tier 3 — build last (high value, most technical/volatile cores → authored most carefully):**
`robotics-autonomous-systems-engineering`, `ar-vr-xr-engineering`.

## Build status

**All 10 built and wired** in this PR (roster 121 → 131). Every plugin ships the full
domain-plugin shape: 3 agents, 4 skills, 2 knowledge files (4 Mermaid decision trees + a dated
2026 reference), best-practices/README + 5 rules, 2 templates, 2 commands, plus
`plugin.json` / `README.md` / `CLAUDE.md` / `CHANGELOG.md` — 23 files each, 230 new files total.

## Build log

- ✅ `residential-real-estate-brokerage` — agents: residential-brokerage-lead, listing-and-transaction-coordinator, buyer-agent-advisor.
- ✅ `auto-repair-shop-operations` — agents: auto-repair-shop-lead, service-advisor-estimator, technician-workflow-manager.
- ✅ `salon-spa-operations` — agents: salon-spa-operations-lead, front-desk-booking-manager, stylist-chair-economics-advisor.
- ✅ `fitness-studio-gym-operations` — agents: fitness-studio-operations-lead, membership-retention-manager, class-schedule-coach-ops.
- ✅ `title-escrow-settlement` — agents: title-escrow-lead, title-examiner, closing-settlement-coordinator.
- ✅ `childcare-early-education` — agents: childcare-center-lead, enrollment-and-family-manager, classroom-ratio-compliance-advisor.
- ✅ `higher-education-administration` — agents: higher-ed-administration-lead, enrollment-management-strategist, student-success-advisor.
- ✅ `travel-agency-tour-operations` — agents: travel-agency-operations-lead, itinerary-and-booking-specialist, supplier-and-commission-manager.
- ✅ `robotics-autonomous-systems-engineering` — agents: robotics-architect-lead, ros-motion-planning-engineer, perception-and-autonomy-engineer.
- ✅ `ar-vr-xr-engineering` — agents: xr-architect-lead, xr-interaction-engineer, spatial-rendering-engineer.

### Gate results (this branch)

- `check-frontmatter.py` — **pass** (strict-YAML, scenario schema, all 30 new agent descriptions ≤300 chars, names globally unique).
- `check-marketplace-claims.py --structural-only` — **pass** (required files, ≤1024-char descriptions, architecture.md rows present). *(The full count-check surfaces only pre-existing `"46 skills"` boilerplate drift on established plugins — self-healed post-merge, skipped on PR CI; none of the 10 new plugins are count-inconsistent.)*
- `check-md-links.py` — **pass** (every relative link resolves).
- `prettier --check .` — **pass** (exit 0). JSON version parity marketplace↔plugin.json — **pass**. Layout allow-list — **pass** (all 230 new files match).

### Blockers

None. No hooks/scripts/MCP were bundled in this batch (keeps the CI gate surface minimal);
advisory hooks and per-plugin dashboards can follow in later version bumps.
