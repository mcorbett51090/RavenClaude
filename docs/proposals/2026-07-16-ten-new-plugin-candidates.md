# Ten New Plugin Candidates for RavenClaude

**Date:** 2026-07-16
**Author:** scheduled routine (autonomous research + build run)
**Status:** #1 built in this run (`ai-agent-engineering`); #2–#10 specced for follow-up.

## Prior art

This is a follow-up to [`2026-07-15-ten-new-plugin-candidates.md`](2026-07-15-ten-new-plugin-candidates.md), which built **`prompt-engineering`** and **`database-reliability-engineering`** and left a vertical backlog whose top next-builds were `home-health-agency-operations` and `warehouse-wms-operations`. Those remain valid and are **not** re-derived here — see that doc for their full briefs. This pass adds one **net-new engineering** plugin the 07-15 slate did not surface — **`ai-agent-engineering`** — because the AI cluster gained a *prompt* owner but still had no owner for *building agents themselves*, the natural sibling gap and an equally high-demand 2026 topic. The candidate table below is this pass's own slate; where it overlaps the 07-15 backlog (home health), treat the earlier doc's brief as canonical.

## Method

Enumerated the existing catalog (`.claude-plugin/marketplace.json`, **166 plugins** at run start) and scanned `plugins/` for dedicated directories and agent coverage. Candidates below were confirmed **absent** by keyword scan (`plugins/` dir names + `agents/*.md` bodies) — none of the ten collide with an existing plugin. Each was scored on **user demand** (how often the domain shows up as a real ask) × **technical feasibility** (can it be built to the marketplace's gate standard as concept-first agents + skills + knowledge + templates, without external runtime deps).

The marketplace already has extremely broad coverage (engineering craft, all major clouds, the Microsoft stack, data/AI, and ~90 industry verticals), so the genuine gaps are (a) one hot **engineering** discipline that the AI cluster hasn't carved out yet, and (b) a set of **industry verticals** with real operational depth that simply weren't built yet.

## The ten candidates (prioritized)

| # | Plugin | Cluster | Purpose / value | Demand | Feasibility | Priority |
|---|---|---|---|---|---|---|
| 1 | **ai-agent-engineering** | Data & AI | Building production **agentic systems** — agent-vs-workflow triage, single/multi-agent, framework selection, tool/context/memory design, guardrails, agent evals. The AI cluster has RAG, prompts, LLM-eval, and Claude-apps but **nothing on building agents themselves** — the #1 AI-engineering topic of 2026. | Very high | High | **P0 — built this run** |
| 2 | **home-health-agency-operations** | Healthcare vertical | Medicare-certified home-health & home-care agency ops — OASIS assessments, PDGM episode management, plan-of-care/485, aide scheduling & EVV, intake/referrals, survey readiness. Distinct from `hospice-referral-sales` (sales only) and `senior-care-operations` (facility-based). | High | High | P1 |
| 3 | **church-congregation-operations** | Nonprofit/community vertical | Congregation/ministry operations — membership & pastoral care, giving/tithing & fund accounting, volunteer & small-group coordination, events & facilities, ChMS workflows (Planning Center-style). A large, entirely uncovered vertical. | High | High | P1 |
| 4 | **urgent-care-clinic-operations** | Healthcare vertical | Walk-in/urgent-care clinic ops — patient throughput & door-to-door time, occupational-health & employer contracts, POCT/lab, coding for E/M + procedures, multi-site staffing. Distinct from `medical-revenue-cycle` (billing engine) and the specialty-clinic plugins. | High | High | P1 |
| 5 | **political-campaign-operations** | Public-sector/advocacy vertical | Electoral campaign & advocacy ops — voter file & targeting, field/canvassing & phone/text programs, FEC/state compliance & disclosure, fundraising (small-dollar + events), GOTV. Non-partisan operational scaffolding. Adjacent to but distinct from `public-sector-govtech` and `nonprofit-fundraising`. | Medium-high | Medium (compliance nuance) | P2 |
| 6 | **coworking-space-operations** | Real-estate/services vertical | Coworking & flex-space ops — membership tiers & billing, desk/room booking & occupancy, community & events, access control, broker/enterprise deals. Distinct from `commercial-real-estate` (transactions) and `property-management` (residential/multifamily). | Medium | High | P2 |
| 7 | **feature-flag-progressive-delivery-engineering** | Engineering craft | Progressive delivery — flag lifecycle & tech-debt, canary/blue-green/ring rollouts, experiment-vs-ops flags, kill switches, targeting rules. `experimentation-growth-engineering` covers experiment *design*; `devops-cicd` covers pipelines — neither owns flag/rollout engineering as a discipline. | Medium-high | High | P2 |
| 8 | **synthetic-test-data-engineering** | Data & AI | Synthetic & anonymized test-data generation — referential-integrity-preserving fixtures, PII de-identification/masking, differential-privacy synthesis, seeding for tests & demos. `qa-test-automation` uses test data; `data-governance-privacy` sets policy — neither builds the generation engine. | Medium | High | P3 |
| 9 | **cinema-movie-theater-operations** | Hospitality/entertainment vertical | Movie-theater ops — showtime & screen scheduling, distributor settlement & film rental terms, concessions margin, loyalty/subscriptions, staffing to showtimes. An uncovered live-venue vertical adjacent to `event-management` and `hotel-hospitality-operations`. | Medium | High | P3 |
| 10 | **golf-country-club-operations** | Hospitality/membership vertical | Golf & private-club ops — tee-sheet & pace-of-play, membership dues & minimums, F&B/pro-shop, agronomy/course-maintenance calendar, events/outings. Distinct from `hotel-hospitality-operations` and `fitness-studio-gym-operations`. | Medium | High | P3 |

## Prioritization rationale

- **P0 (build first): `ai-agent-engineering`.** Highest demand of the set and the clearest *engineering* gap — the marketplace's AI cluster (`ai-rag-engineering`, `prompt-engineering`, `llm-evaluation-engineering`, `claude-app-engineering`, `ai-coding-model-guidance`, `ai-red-teaming`) covers retrieval, prompts, eval, Claude-apps, and red-teaming but has **no plugin for building agentic systems** — the single most-requested AI-engineering topic in 2026. Clean, non-overlapping boundary (build-the-agent vs retrieval-behind-a-tool vs single-call-prompt vs general-eval). **This is the one built in this run.**
- **P1 (verticals with the strongest demand + clean seams): #2–#4.** Home health, congregations, and urgent care are large, operationally-rich verticals with **zero** current coverage and unambiguous boundaries against neighboring plugins — high value, low overlap risk, straightforward to build to the concept-first standard.
- **P2 (#5–#7):** Real demand but each carries a wrinkle — campaign ops has compliance nuance that must be handled carefully (non-partisan, disclosure-accurate); coworking is smaller TAM; feature-flag engineering must be scoped tightly against `experimentation-growth-engineering` and `devops-cicd`.
- **P3 (#8–#10):** Solid additions with clean seams but lower relative demand than the above; good candidates for a later batch.

## Implementation approach (shared pattern)

Every candidate follows the established marketplace anatomy (verified against `quantum-computing-engineering` and the vertical plugins):

- `.claude-plugin/plugin.json` (name/version/description/keywords, `requires: ravenclaude-core@>=0.7.0`) **+ a matching entry appended to `.claude-plugin/marketplace.json`** (version must match — CI gate).
- `CLAUDE.md` (team constitution: roster, routing, house opinions, anti-patterns, CGP, output contracts, skills/knowledge/templates index, escalation seams) and `README.md`.
- **2–4 agents**, each with the full scenario-authoring frontmatter (`audience`, `works_with`, `scenarios[intent/trigger_phrase/outcome/difficulty]`, `quickstart`), an explicit least-privilege `tools:` allowlist, and a `description` **≤ 300 chars** — all three gated by `scripts/check-frontmatter.py`.
- **3 skills** (a triage/decision skill + two doing skills), **2 knowledge docs** (a decision tree + a dated patterns/reference doc with retrieval-date discipline), **2 templates**.
- **Dependencies:** none beyond `ravenclaude-core`; these are concept-first advisory teams (no external runtime). `jq`/`python3` already present for the gates.

## Blockers / notes

- **Scope of an autonomous run.** Building all ten to the marketplace's quality bar (each ~10–14 files passing ~10 CI gates) is more than one run should attempt without shipping half-built plugins that fail CI. This run builds **#1 fully** and specs the rest here; #2–#10 are follow-up PRs.
- **`marketplace.json` metadata prose is stale independent of this change** — its `metadata.description` still says "144 domain plugins" while the catalog holds 166→167. Not touched here (it isn't maintained per-plugin and isn't gated); flagging for a separate cleanup.
- **Campaign-ops (#5)** needs a deliberate non-partisan, compliance-accurate stance before build — noted so it isn't built casually.
