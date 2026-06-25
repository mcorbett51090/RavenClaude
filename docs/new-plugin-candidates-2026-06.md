# New plugin candidates — gap analysis (2026-06-25)

Research pass to identify plugins the RavenClaude marketplace does **not** yet ship.
At the time of writing the catalog held **119 plugins**; this doc proposes 10 new ones,
prioritizes them by *user demand × technical/authoring feasibility*, and records the
build approach + dependencies for each so the backlog is actionable.

## Method

1. Enumerated all 119 plugin names from `.claude-plugin/marketplace.json` and clustered
   them (software-delivery chain, cloud, app craft, data/AI, Microsoft stack, and ~50
   business/industry verticals).
2. Hunted for **genuine, well-bounded gaps** — a candidate only counts if no existing
   plugin already owns its craft. Each candidate below names the nearest existing
   plugins and the **seam** that keeps it distinct (the marketplace's "don't let them
   drift toward each other" rule).
3. Scored each on **demand** (size of the audience / frequency of the ask) and
   **feasibility** (how cleanly the craft decomposes into 3 agents + skills + a
   decision-tree knowledge bank, and how stable the domain facts are).

## The 10 candidates

| # | Plugin | Type | Demand | Feasibility | Nearest existing → seam |
|---|--------|------|--------|-------------|--------------------------|
| 1 | **fitness-studio-operations** | vertical | High | High | restaurant/retail-store-ops are different verticals; accounting-bookkeeping (books), marketing-operations (campaigns) |
| 2 | **technical-seo-engineering** | engineering | High | High | performance-engineering (runtime perf), frontend-engineering (rendering), marketing-operations (content/keywords) |
| 3 | **salon-spa-operations** | vertical | High | High | accounting-bookkeeping, marketing-operations, people-operations-hr |
| 4 | **streaming-media-engineering** | engineering | Med-High | Med | film-video-production (creative), data-streaming-engineering (Kafka), frontend-engineering (player UI) |
| 5 | **childcare-early-education-operations** | vertical | Med-High | High | k12-school-administration (schools, not daycare), people-operations-hr |
| 6 | **brewery-craft-beverage-operations** | vertical | Med | Med | restaurant-operations (taproom F&B), manufacturing-operations (generic process), procurement-sourcing |
| 7 | **hoa-community-association-management** | vertical | Med | High | property-management (rental property, not owner-governed associations), legal-small-firm |
| 8 | **travel-tourism-operations** | vertical | Med | Med | event-management (events, not itineraries), hotel-hospitality-operations (the property side) |
| 9 | **self-storage-operations** | vertical | Med | High | property-management (residential/commercial leasing), retail-store-operations |
| 10 | **robotics-engineering** | engineering | Med | Med-Low | embedded-iot-engineering (firmware, not motion/perception), ml-engineering (training, not real-time control) |

### Demand/feasibility prioritization rationale

- **Tier 1 (build first): #1, #2, #3.** Each pairs a large, underserved audience with a
  craft that decomposes cleanly into a 3-agent team with a stable decision-tree core.
  Fitness studios and salons/spas are two of the largest small-business segments with
  *no* current plugin, and technical SEO is a perennial high-frequency engineering ask
  that the existing perf/frontend/marketing plugins each touch but none owns.
- **Tier 2 (next): #5, #7, #9.** High feasibility (clean, rules-driven domains) but
  somewhat narrower audiences than Tier 1. Childcare has heavy licensing/ratio rules
  that map well to decision trees; HOA and self-storage are well-bounded ops verticals.
- **Tier 3 (later / more research): #4, #6, #8, #10.** Higher authoring cost or
  faster-moving / more fragmented domains. Streaming-media and robotics need careful
  seam discipline against several adjacent engineering plugins; brewery and travel span
  production + compliance + distribution that need scoping before a 3-agent cut is safe.

## Per-candidate build approach & dependencies

All candidates follow the marketplace's standard plugin anatomy and **require
`ravenclaude-core@>=0.7.0`** (the team constitution, Capability Grounding & Structured
Output Protocols). None introduces a new top-level directory, so `.repo-layout.json`
needs no new globs — the existing `plugins/*/**` patterns cover them. Each ships:
`.claude-plugin/plugin.json`, `CLAUDE.md`, `README.md`, `CHANGELOG.md`, 3 agents (full
scenario-authoring frontmatter, ≤300-char descriptions, globally-unique names), 4–5
skills, a 2-file knowledge bank (Mermaid decision trees + dated 2026 reference), 6–8
best-practices, 2–3 templates, 2–3 commands, and 1 advisory `PreToolUse` hook.

1. **fitness-studio-operations** — Agents: `fitness-studio-operations-lead`,
   `member-retention-analyst`, `class-and-instructor-ops-lead`. Decision trees: pricing
   model (recurring vs class-pack vs drop-in), at-risk-member detection. Core KPI:
   retention/churn and revenue-per-member. No external deps beyond core.
2. **technical-seo-engineering** — Agents: `technical-seo-lead`,
   `crawl-indexation-engineer`, `core-web-vitals-engineer`. Decision trees: "crawl
   problem vs index problem", "noindex vs robots-disallow vs canonical". Highest-risk
   workflow: site-migration redirect mapping.
3. **salon-spa-operations** — Agents: `salon-spa-operations-lead`,
   `booking-and-retention-analyst`, `service-menu-and-pricing-strategist`. Decision
   trees: commission vs booth/chair rental vs hybrid; empty-chair (demand vs scheduling).
   Core KPI: rebooking rate + retail attachment.
4. **streaming-media-engineering** — Agents: media-pipeline-architect,
   transcoding/packaging engineer, playback/QoE engineer. Decision trees: HLS vs DASH +
   DRM selection, per-title vs CBR/VBR encoding ladder. Deps: FFmpeg/Shaka/ExoPlayer
   knowledge (facts move fast — dated reference essential).
5. **childcare-early-education-operations** — Agents: center-operations-lead,
   enrollment-and-tuition-analyst, compliance-and-ratios-lead. Decision trees:
   staff-to-child ratio by age band, licensing-incident response. Heavy regulated-facts
   → dated reference with a "rules vary by jurisdiction" banner.
6. **brewery-craft-beverage-operations** — Agents: production-and-batch-lead,
   taproom-and-distribution-lead, compliance-and-excise-lead. Trees: self-distribution
   vs 3-tier, batch-scaling. Deps: TTB/excise facts (dated, jurisdictional).
7. **hoa-community-association-management** — Agents: association-operations-lead,
   reserves-and-budget-analyst, governance-and-compliance-lead. Trees: reserve-funding
   adequacy, covenant-enforcement escalation.
8. **travel-tourism-operations** — Agents: trip-and-itinerary-architect,
   supplier-and-booking-ops-lead, margin-and-yield-analyst. Trees: package vs FIT,
   supplier-risk/cancellation. Deps: GDS/OTA landscape (dated).
9. **self-storage-operations** — Agents: facility-operations-lead,
   revenue-management-analyst, delinquency-and-lien-lead. Trees: dynamic street-rate vs
   existing-tenant-rate-increase, delinquency→lien/auction timeline (jurisdictional).
10. **robotics-engineering** — Agents: robotics-systems-architect, motion-planning-and-
    control-engineer, perception-and-slam-engineer. Trees: ROS2 vs bespoke middleware,
    sensor-fusion stack. Higher authoring cost; defer until Tier 1/2 land.

## Build status (this PR)

- **Built to full bar:** #1 fitness-studio-operations, #2 technical-seo-engineering,
  #3 salon-spa-operations (Tier 1).
- **Specced backlog (this doc):** #4–#10. Each is ready to build to the same template;
  Tier 2 (#5, #7, #9) recommended next.

This staged delivery favors three complete, gate-passing, domain-accurate plugins over
ten shallow stubs — consistent with the marketplace's quality bar (every agent must
carry the scenario-authoring schema and pass `check-frontmatter.py`, and every plugin
must survive a consumer's `/plugin marketplace update`).
