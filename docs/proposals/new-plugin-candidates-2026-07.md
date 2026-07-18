# New plugin candidates — gap analysis (2026-07-18)

Research pass to identify **10 new plugins** for the RavenClaude marketplace that are
not yet implemented, prioritized by demand × technical feasibility, with an
implementation approach for each.

## Method

The marketplace already ships **167 plugins** spanning the software-delivery chain,
the three major clouds, app craft, data & AI, the Microsoft stack, and ~90 business
and vertical operations plugins. "Demand" here is inferred from a **coverage-gap
analysis against those 167** — the functions and verticals a plugin-of-teams
marketplace would be expected to cover but does not — rather than from external
telemetry or a live feature-request queue (we have no such queue to cite; claiming
one would be unfounded). Each candidate below was checked against the plugin roster
(`ls plugins/`) and confirmed absent, and against the existing agent registry for
name collisions.

Feasibility is high across the board: every candidate is a **knowledge-and-judgment**
team (agents + skills + a cited knowledge bank), matching the established plugin
shape. None requires a new MCP integration or external credential to be useful, so
none is gated on infrastructure. Volatile figures (rates, thresholds, regulatory
specifics) are handled the way every existing plugin handles them — retrieval-dated
and `[verify-at-use]`, never asserted as current fact.

## The 10 candidates

| # | Plugin | What it is | Why it's a gap | Priority |
|---|---|---|---|---|
| 1 | **partnerships-alliances** | Partner/channel/alliance GTM team — partner tiering, co-sell motions, MDF programs, partner-sourced pipeline, ecosystem strategy, QBRs. | `sales-revops`, `sales-engineering`, `developer-relations` exist, but none owns the **partner/channel** motion (indirect revenue, co-sell, alliances). | **P0** |
| 2 | **corporate-development-ma** | Corp-dev / M&A team — deal sourcing & thesis, valuation (DCF/comps/precedents), due diligence, deal structuring, and post-merger integration (PMI). | `startup-fundraising`, `finance`, `treasury-management` exist; none covers **buy-side M&A** end-to-end. | **P0** |
| 3 | **executive-operations** | Chief-of-staff / exec-ops team — operating cadence, OKR cascade, board & exec-staff prep, decision memos, priority triage. | No plugin owns the **chief-of-staff** function that runs the operating system of a leadership team. | P1 |
| 4 | **facilities-management** | Corporate facilities / workplace ops — CMMS & maintenance, space & occupancy planning, lease administration, vendor/soft-services management. | `property-management` (residential landlord) and `commercial-real-estate` (investment) exist; neither is **corporate FM / workplace**. | P1 |
| 5 | **learning-and-development** | Corporate L&D — instructional design (ADDIE/backward design), skills taxonomy, LMS/LXP program ops, learning measurement (Kirkpatrick). | `people-operations-hr` covers the HR lifecycle and `edtech-partner-success` is K-12/EdTech GTM; neither is **corporate L&D / instructional design**. | P1 |
| 6 | **knowledge-management** | Enterprise KM — taxonomy & information architecture, findability, wiki/KB governance, KCS for support, knowledge-decay control. | `technical-writing-docs` owns docs authoring; nothing owns **enterprise KM discipline** (taxonomy, KCS, findability). | P1 |
| 7 | **investor-relations** | Public-company IR — earnings cycle, guidance policy, the equity story, analyst/shareholder engagement, disclosure discipline (Reg FD-aware). | `startup-fundraising` is private-market raising; public-company **IR** is a distinct function. | P2 |
| 8 | **hoa-community-association-management** | HOA / COA management — reserve studies & funding, assessments & budgets, covenant enforcement, board governance & meetings, vendor management. | `property-management` is unit-level landlording; **community-association governance** is a distinct vertical. | P2 |
| 9 | **pest-control-operations** | Pest-control field-service vertical — recurring-service route density, technician productivity, pesticide/applicator compliance, plan mix & retention. | `field-service-management` is horizontal; **pest control** has distinct recurring-revenue + regulated-chemical economics. | P2 |
| 10 | **synthetic-data-engineering** | Synthetic-data team for AI/ML & privacy — generation method selection, fidelity-vs-privacy tradeoff, disclosure risk, downstream utility evaluation. | `data-governance-privacy`, `ml-engineering`, `ai-rag-engineering` exist; none owns **synthetic-data generation & evaluation**. | P2 |

## Per-candidate implementation approach

All ten follow the established plugin contract (`AGENTS.md` §"Adding a new plugin"):
`.claude-plugin/plugin.json` + `README.md` + `CLAUDE.md` (team constitution with numbered
house opinions), 2–3 agents each carrying the scenario-authoring frontmatter + explicit
`tools:` allowlist, 3–4 skills with mirrored `commands/`, a `knowledge/` bank with at
least one Mermaid decision tree + a dated reference, 6–8 `best-practices/`, 1–2 `templates/`,
and one advisory `PostToolUse` hook. `requires: ravenclaude-core@>=0.7.0`. No new
dependencies beyond `jq`/`python3` (already present). Each ships domain-specific
house opinions — e.g.:

- **partnerships-alliances** — "partner-sourced ≠ partner-influenced pipeline; attribute honestly"; "a partner tier is a set of obligations, not a logo wall"; "co-sell dies without a named rep-to-rep motion."
- **corporate-development-ma** — "the thesis precedes the model; a deal with no thesis is a spreadsheet looking for a victim"; "synergies are a plan with an owner and a date, not a line item"; "integration risk is priced pre-signing or paid post-close."
- **executive-operations** — "the cadence is the product; a decision with no owner and no date is a discussion"; "surface the one thing that changes the answer, not the status deck."
- **facilities-management** — "deferred maintenance is a loan at a punitive rate"; "space is a portfolio; utilization before expansion."
- **learning-and-development** — "design backward from the on-the-job behavior, not the content"; "completion is an activity metric, not a learning outcome."
- **knowledge-management** — "findability before more content; a doc nobody finds is decay"; "taxonomy is a product with an owner, not a one-time workshop."
- **investor-relations** — "guidance is a policy, not a number"; "the equity story is one sentence or it isn't a story"; "disclose symmetrically (Reg FD-aware) — cite + date every market figure."
- **hoa-community-association-management** — "underfunded reserves are a deferred special assessment"; "enforce covenants consistently or don't enforce them."
- **pest-control-operations** — "route density is the margin; a recurring plan is worth more than the ticket"; "applicator compliance is not optional and is state-specific."
- **synthetic-data-engineering** — "fidelity and privacy trade off — name the operating point"; "prove downstream utility on the real task, not a distribution plot."

## Prioritization rationale

Ranked on **demand (breadth of applicability) × feasibility (authoritative content
without external infra) × gap-cleanliness (no overlap with an existing plugin)**:

- **P0 — build first: `partnerships-alliances`, `corporate-development-ma`.** Both are
  horizontal (broad B2B applicability, not a narrow vertical), sit on a mature,
  well-documented body of practice that can be authored authoritatively, and fill a
  clean gap no existing plugin touches. Highest value-per-build.
- **P1 — `executive-operations`, `facilities-management`, `learning-and-development`,
  `knowledge-management`.** Horizontal and clearly missing, slightly narrower audience
  than the P0 pair.
- **P2 — `investor-relations`, `hoa-community-association-management`,
  `pest-control-operations`, `synthetic-data-engineering`.** Valuable but narrower
  (public-company-only, single verticals, or a specialist AI niche); build after the
  broader-demand tiers.

## Build status (this PR)

Building all ten to the marketplace's quality bar (each ~25+ files, every agent
gate-checked for the scenario schema, tools allowlist, and description cap) is a
multi-session effort. This PR delivers the **two P0 plugins complete and
gate-passing** — [`partnerships-alliances`](../../plugins/partnerships-alliances/)
and [`corporate-development-ma`](../../plugins/corporate-development-ma/) — plus this
roadmap for the remaining eight (P1/P2), which are specified above and ready to build
in follow-up PRs.
