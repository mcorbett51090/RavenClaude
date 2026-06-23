# Changelog — edtech-partner-success

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.12.2] — 2026-06-22

Version bump previously unlogged here; the change that set `0.12.2`:

- Repo review autonomous fixes + B1–B6 deferred items + dead-regex CI guard (#449)

## [0.12.1] — 2026-06-16

### Fixed

- **Renamed the `partner-success-manager` agent → `edtech-partner-success-manager`** to resolve a cross-plugin name collision with `ravenclaude-core`'s domain-neutral `partner-success-manager`. With both plugins enabled the two agents collided in Claude Code's subagent registry, making orchestrator routing non-deterministic. `ravenclaude-core` keeps the generic name (house rule #1); this plugin's specialist is now namespaced. Updated all in-plugin references (`works_with`, skill `primary_agent`, prose) — references to core's generic agent are unchanged. A new cross-plugin agent-name-uniqueness check in `scripts/check-frontmatter.py` prevents recurrence.

- **Migration:** if you invoke this agent by name, use `edtech-partner-success-manager`. The bare `partner-success-manager` now unambiguously refers to the `ravenclaude-core` agent.

## [0.12.0] — 2026-06-05

Value-add build-out — closes the remaining net-new gaps relative to the merged `veterinary-practice` recipe (scenarios bank + complementary decision trees + a runnable calculator), on top of the already-rich v0.11.1 surface (6 agents, 16 skills, 18-doc knowledge bank, 16 templates, 8 decision trees from PR #315). The code-runtime tier (bundled MCP / LSP / bin / monitors / styles / settings) is dispositioned **N-A** with reasons in `CLAUDE.md` §9b "Value-add completeness (build-out 2026-06-05)".

- **Scenarios bank enabled** (`scenarios/`) — new directory + README + **4** dated, scope-tagged, unverified engagement scenarios (mirrors the marketplace 9-field schema, `product_version: "n/a"`): low-seat-utilization renewal risk, implementation slipping past time-to-value, efficacy-data gap at renewal, expansion blocked by champion churn. Each carries an "Action for the next PSM" lesson + cited public benchmarks. The §8b "TODO (planned)" block in `CLAUDE.md` is **removed** (replaced by the live §8b). The four most-likely-to-benefit agents — `edtech-partner-success-manager`, `learning-analytics-analyst`, `success-playbook-designer`, `partner-profile-curator` — gained the **Scenario retrieval (priors)** inline-prior block. FERPA: scenarios carry no partner-identifying info, no student/family PII; synthetic identifiers only.
- **1 new Mermaid decision-tree knowledge file** (`knowledge/adoption-and-expansion-decision-trees.md`) holding **2 trees** that sit *one level deeper* than PR #315's 8 trees:
  - **Adoption intervention — which lever for a low-utilization read** (suppress / rostering pre-flight / adoption-sequencing / re-cascade train-the-trainer / use-case rescope / 4-hypothesis diagnostic) — hands declining cases down to the play-selection router.
  - **Expand or stabilize — gating an expansion motion** — operationalizes the 3-gate expansion model (top-quartile health AND demonstrable adoption AND organizational readiness) with the don't-sell discipline; "stabilize" is the honest default. Hands eligible-inside-window cases into the renewal-risk tree.
  - Checked carefully against `partner-success-decision-trees.md` + `partner-health-decline-which-play.md` so it does **not** duplicate the existing renewal/recovery/triage/cadence/escalation/AI/handoff/FERPA/play-selection trees. Wired into `learning-analytics-analyst` (adoption tree) + `success-playbook-designer` (expand-vs-stabilize) inline priors.
- **Runnable calculator** `scripts/psm_calc.py` (stdlib only, Python 3.8+, `ruff`-clean) — three modes: `utilization` (seat activation rate + dead-seat count + waste-proxy), `renewal-forecast` (book-level GRR/NRR projection from per-band counts/ARR/retention/expansion with a segment benchmark band), `ttv` (time-to-first-value vs. calendar-dead-zone check). Decision-support, not advice; FERPA: aggregate partner-level counts only, never PII. The plugin previously had no `scripts/` calculator.

### Honestly N-A for a non-code vertical (documented, not forced)
Bundled MCP server (CS platforms / SIS / rostering brokers are per-tenant / authenticated / PII-bearing → *recommend, evaluate-first*, never bundle, per `docs/best-practices/bundled-mcp-servers.md`; no server fabricated), LSP (no source language in a PSM advisory vertical), `bin/` / monitors / output-styles / themes / `settings.json` — each dispositioned with a one-line reason in `CLAUDE.md` §9b. The one runtime item with real non-code value — a runnable calculator — **was** built.

### Shared-file changes required (orchestrator-owned, NOT done here)
- `.repo-layout.json` `allowed_globs` already covers `plugins/*/scenarios/**` and `plugins/*/scripts/**` — no new globs needed (confirmed against the manifest).
- `.claude-plugin/marketplace.json` + `.claude-plugin/plugin.json` `version` bump `0.11.1` → `0.12.0` (both mirrors updated in this build-out).

## [0.11.1] and earlier

See `CLAUDE.md` §8a (knowledge-bank waves) and §8 (skills) for the milestone narrative: v0.1.0 initial release (6 agents, the PSM lane), v0.2.0 production-lesson knowledge layer, v0.3.0 foundational research layer, v0.4.0 vertical-depth layer, v0.4.1 operating-cadence layer, v0.4.2 capability-extension layer (5 knowledge + 4 skills + 6 templates), v0.5.0 stack-integration layer (Planhat/SFDC/Snowflake), and the 2026-06-04 enforcement-precedent / COPPA / ESSA / PE-ownership / CBT-readiness / AI-teammate knowledge wave plus the consolidated decision-trees file (PR #315). The authoritative version history is the `version` field + git history; this CHANGELOG starts its detailed entries at the v0.12.0 build-out.
