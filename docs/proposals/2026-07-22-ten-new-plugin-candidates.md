# Ten new-plugin candidates for RavenClaude — research, prioritization, and initial build

**Date:** 2026-07-22 · **Author:** scheduled research routine · **Status:** proposal + P0 builds landed

## Method

Enumerated the 167 plugins already in `.claude-plugin/marketplace.json` and looked for
**genuine gaps** — domains with clear demand for a coding/ops agent team that no existing
plugin already owns. Each candidate below was checked against the closest existing plugins to
confirm it is *distinct* (the marketplace's house rule #1: every plugin has a defensible
boundary, and every description names the neighbours it is **not**). Candidates were then
ranked by **user demand × technical feasibility × distinctness**.

The marketplace skews toward a coding-agent audience, so engineering candidates were weighted
slightly higher than pure vertical/ops candidates of equal demand.

## The 10 candidates

| # | Plugin | Purpose & value | Closest existing (why distinct) | Tier |
|---|--------|-----------------|---------------------------------|------|
| 1 | **design-systems-engineering** | Build and maintain a design system: design tokens, component-library architecture, theming, Storybook/docs, Figma→code, versioning & publishing (semver, changesets), governance & adoption. | `frontend-engineering` builds *apps*; `accessibility-engineering` is *compliance*; `web-design` is *site design*. None owns the **system** that feeds them all. | **P0** |
| 2 | **web-scraping-data-extraction** | Design robust, ethical scrapers & extraction pipelines: crawl architecture, resilient parsing, anti-bot reality, rate/robots/ToS & legal posture, scheduling, change-detection, structured-output pipelines. | `data-orchestration`/`data-streaming` move data that *already exists*; `backend-engineering` is generic. Nobody owns **acquiring** web data. | **P0** |
| 3 | **synthetic-test-data-engineering** | Generate synthetic & test data that is realistic and PII-safe: referential integrity, distribution matching, data masking/subsetting, seeding, privacy (k-anon, DP basics). | `data-governance-privacy` sets *policy*; `qa-test-automation` writes *tests*. Neither **generates** the data. | **P1** |
| 4 | **contract-testing-engineering** | Consumer-driven contract testing (Pact), provider verification, API mocking/virtualization, schema & backward-compat gating in CI. Postman MCP available in-session. | `qa-test-automation` is broad E2E; `api-engineering` designs APIs. Contract testing between services is its own discipline. | **P1** |
| 5 | **customer-onboarding-implementation** | Run implementation/onboarding projects: kickoff → configuration → data migration → go-live → time-to-value; onboarding playbooks, success plans, handoff to CS. | `customer-success-analytics` measures health post-live; `project-management` is generic. The **implementation** motion is distinct. | **P2** |
| 6 | **partnerships-alliances** | Build & run a partner program: channel/tech/co-sell partnerships, partner tiers & enablement, deal registration, co-marketing, partner-sourced pipeline. | `sales-revops`/`sales-engineering` own *direct* sales. Indirect/partner GTM is uncovered. | **P2** |
| 7 | **competitive-intelligence** | Stand up a CI function: win/loss analysis, battlecards, competitor landscape & positioning, market-monitoring cadence, sales enablement of intel. | `product-management` touches strategy; `marketing-operations` runs campaigns. Structured CI is uncovered. | **P2** |
| 8 | **trade-compliance-customs** | Import/export compliance: HTS/Schedule-B classification, country-of-origin & valuation, export controls (EAR/ITAR basics), denied-party screening, customs entry & recordkeeping. | `freight-forwarding-sales` sells freight; `supply-chain-planning` plans supply; `procurement-sourcing` buys. Regulatory trade compliance is uncovered. | **P2** |
| 9 | **investor-relations** | Public-company / growth-stage IR: earnings cycle & scripts, guidance & consensus management, shareholder & analyst comms, Reg FD discipline, IR site & disclosure cadence. | `startup-fundraising` is the *private raise*; `finance`/`treasury-management` own the numbers. Ongoing IR is uncovered. | **P3** |
| 10 | **podcast-production-operations** | Run a podcast as a business: production workflow, distribution/RSS/platforms, audience growth, monetization (ads/CPM, sponsorships, memberships), measurement. | `film-video-production` & `streaming-media-engineering` are video/tech; `creator-economy-operations` is generic creator biz. Podcast ops is uncovered. | **P3** |

## Prioritization rationale

- **P0 — build now.** `design-systems-engineering` and `web-scraping-data-extraction` are the
  two highest on **demand × feasibility × distinctness**. Both are squarely in the coding-agent
  wheelhouse (high demand from the marketplace's core audience), have crisp boundaries against
  existing plugins, and are fully buildable from durable, non-volatile knowledge (patterns and
  trade-offs, not fast-moving vendor specifics).
- **P1 — build next.** `synthetic-test-data-engineering` and `contract-testing-engineering`
  round out the testing/data-engineering surface; both are distinct and in-demand, with
  contract-testing benefiting from the in-session Postman MCP.
- **P2 — business/ops with clear boundaries.** `customer-onboarding-implementation`,
  `partnerships-alliances`, `competitive-intelligence`, `trade-compliance-customs` fill real
  GTM/ops gaps. `trade-compliance-customs` is regulated, so it needs the retrieval-dated /
  verify-at-use discipline the compliance plugins already use.
- **P3 — niche but uncovered.** `investor-relations` and `podcast-production-operations` are
  lower-demand but genuinely uncovered and cheap to build well.

## Implementation approach (shared)

Every plugin follows the established marketplace pattern (see `AGENTS.md` §"Adding a new plugin"):

- `.claude-plugin/plugin.json` (`name`, `version`, `description`, `requires: ravenclaude-core`),
  `README.md`, `CLAUDE.md` (team constitution importing core), plus an entry appended to
  `.claude-plugin/marketplace.json` and a row in `docs/architecture.md` §Status.
- **Agents** (2–3): each carries the full gated frontmatter schema (`description` ≤300 chars,
  explicit `tools:` allowlist, `audience`, `works_with`, `scenarios` with
  intent/trigger_phrase/outcome/difficulty, `quickstart`).
- **Skills** (3): a `SKILL.md` each with a procedure, worked example, and guardrails; the
  `N skills` claim in the description must equal the real count (claim-checker gate).
- **Knowledge bank** (2 docs): a Mermaid decision tree + a dated reference; agents traverse the
  tree before naming an answer (Capability Grounding Protocol).
- **Dependencies:** `ravenclaude-core@>=0.7.0` only. No external runtime deps. Volatile facts
  (vendor pricing, regulatory thresholds) carry a retrieval date + verify-at-use.

## Dependencies & risks per candidate

- **design-systems-engineering** — none beyond core. Risk: overlap with `frontend-engineering`
  mitigated by the "system vs app" boundary stated in the description.
- **web-scraping-data-extraction** — none beyond core. Risk: legal/ethics; the plugin is
  advisory and leads every scraper decision through robots/ToS/rate posture, never
  detection-evasion for abuse.
- **synthetic-test-data / contract-testing** — none beyond core; contract-testing can use the
  Postman MCP when present but does not require it.
- **trade-compliance-customs / investor-relations** — regulated/disclosure-sensitive; explicitly
  *not legal/financial advice*, retrieval-dated, verify-at-use.

## Progress on initial builds

- ✅ **design-systems-engineering** (P0) — built: 2 agents, 3 skills, 2-doc knowledge bank.
- ✅ **web-scraping-data-extraction** (P0) — built: 2 agents, 3 skills, 2-doc knowledge bank.
- ⏭️ **P1–P3 (8 remaining)** — specified above; recommended as follow-up PRs, one per plugin, in
  tier order. Each is independently buildable from this proposal.

## Blockers

None encountered building the P0 tier. The remaining 8 are deferred by scope (a single run
builds the two highest-priority plugins to full gate-passing quality rather than 10 shallow
ones); they are fully specified here for follow-up.
