# Changelog — experimentation-growth-engineering

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.3.1] — 2026-06-22

Version bump previously unlogged here; the change that set `0.3.1`:

- Repo review autonomous fixes + B1–B6 deferred items + dead-regex CI guard (#449)

## [0.3.0] — 2026-06-05

Value-add build-out against the full menu. Net-new on top of PR #315 (which consolidated the knowledge decision-trees, `best-practices/`, and `templates/`): a **scenarios bank**, a **runnable A/B-test design calculator**, one **new topic-specific decision tree**, and a runtime-tier disposition table. Every menu item is dispositioned (built or recorded N-A with reason); see [`CLAUDE.md`](CLAUDE.md) § "Value-add completeness (build-out 2026-06-05)".

### Added

- **scenarios/ bank (4 field notes).** `peeking-early-stop-false-positive` (lock the readout / go sequential — exhortation doesn't hold), `underpowered-test-mde-miss` (a flat result from an underpowered test is "couldn't see it," not "no effect"), `srm-from-redirect-bot-filter` (SRM gates the metric; find the arm-asymmetric step, don't tune it away), `guardrail-regression-latency-vs-conversion` (a primary win with a tripped guardrail is a trade, not a win). README + the 9-field marketplace scenario schema; surfaced behind the mandatory unverified-scenario preamble.
- **Runnable calculator** — [`scripts/experiment_calc.py`](scripts/experiment_calc.py) (stdlib only, Python 3.8+; `ruff`-clean). Four modes: `sample-size` (per-arm N + duration for a target MDE), `mde` (smallest detectable effect at a fixed sample — the underpowered-test check), `power` (achieved power of a planned/run test), `srm` (chi-square sample-ratio-mismatch trustworthiness gate). It is a **calculator, not a data source** — the user supplies every input. **Design-time only:** it sizes the apparatus and runs the SRM gate; the significance / "is the lift real" verdict is deferred to `applied-statistics` (CLAUDE.md §3 #1). z-quantiles via the Acklam rational approximation and the chi-square SF via incomplete-gamma — both stdlib-only (no scipy). Numerically verified against known critical values (χ²=10.83 ⇔ p=0.001; ~31k/arm for 5%→5.5% at 80% power).
- **New decision tree** — [`knowledge/ship-iterate-kill-guardrail-decision-tree.md`](knowledge/ship-iterate-kill-guardrail-decision-tree.md): a standalone Mermaid tree that drills into the **guardrail-breach trade** (reliability gates are non-tradeable → iterate; business guardrails are tradeable only as an explicit, logged business decision). Complements — does not duplicate — the high-level "Ship, iterate, or kill" node already in [`knowledge/experimentation-growth-engineering-decision-trees.md`](knowledge/experimentation-growth-engineering-decision-trees.md). Uses the `# … decision tree` / `## When this applies` standalone convention (not the canonical `## Decision Tree:` SVG-rendered prefix), so it adds no committed-SVG / generator-regen burden — same convention as the veterinary-practice standalone trees.
- **CLAUDE.md** — new §5 (scenarios bank & runnable tooling) and the value-add completeness disposition table.

### Decisions (recorded, not built)

- **No bundled MCP server.** Feature-flag / experimentation / analytics MCP servers exist (LaunchDarkly, GrowthBook, Unleash, Flagsmith have community/first-party servers) but every one is **per-tenant + authenticated + write-capable** (an org API key = a secret; flag flips/experiment edits are write verbs) — failing the doctrine's zero-config + read-only bundling bar (`docs/best-practices/bundled-mcp-servers.md`). Disposition: **recommend-not-bundle / evaluate-first**, gated through `ravenclaude-core/security-reviewer`. No `mcpServers` entry, no invented server.
- **No LSP config.** This is a methodology/apparatus advisory vertical, not a single-language code domain — there is no source language for an LSP server to index (contrast `backend-engineering`, which ships `.lsp.json`).
- **No `bin/`, monitors, output-styles, settings defaults, or themes** — none clears the "groundable + broadly valuable, doesn't duplicate an existing surface" bar. The single stdlib `scripts/experiment_calc.py` covers the runnable need.
- **Skills/hooks/commands/templates coverage held sufficient** — 5 skills, 4 commands, 4 templates, 1 advisory hook already cover the surface; the new scenarios + calculator + tree extend reach without a new agent (team-growth-as-knowledge house rule).
- **No NOTICE.md** — nothing third-party is bundled (the script is original + stdlib-only; all sources are cited inline, not vendored).

### Verify-at-use

- Feature-flag/experimentation platform landscape (LaunchDarkly as point flag solution; Statsig acquired by OpenAI for $1.1B; Flagsmith/Unleash open-source; sequential testing / CUPED availability) — version- and market-volatile; re-confirm at use.
- The peeking false-positive *inflation magnitude* and any always-valid/sequential boundary math are `applied-statistics`' to quantify precisely — marked `[verify-at-use]` in the scenario.
- Guardrail / non-inferiority discipline references (Kohavi/Tang/Xu) are `[unverified — training knowledge]` pointers, not this-session citations.

## [0.2.x] — earlier

3-agent experimentation & growth-engineering team (experimentation-architect, feature-flag-engineer, product-analytics-instrumentation-engineer): 6 skills, a decision-tree knowledge bank, 12 best-practices, 4 templates, 4 commands, 1 advisory hook. Seams: significance → applied-statistics, hypothesis/outcome → product-management, rollout → devops-cicd, pipelines → data-platform.
