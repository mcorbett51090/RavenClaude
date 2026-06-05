# Changelog — process-improvement

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.2.0] — 2026-06-05

Value-add build-out against the full marketplace menu, mirroring the merged `veterinary-practice` recipe (scenarios + decision trees + stdlib calculator + a "Value-add completeness" table + CHANGELOG) and filling this plugin's commands/hooks gap. Net-new on top of PR #315 (which consolidated knowledge decision-trees + best-practices + templates).

- **Scenarios bank** (`scenarios/`) — new directory + README + **5** dated, scope-tagged, unverified engagement scenarios (marketplace 9-field schema, `product_version: "n/a"`): capability-study-fails-threshold (centering vs spread), control-chart tampering (common-cause over-adjustment), DMAIC stuck at Analyze (the proof-gate/statistics seam), control-plan-didn't-hold (orphaned owner), VSM wrong-constraint. Each carries an "Action for the next Black Belt" lesson and cited public sources.
- **New SPC-response decision-tree knowledge file** (`knowledge/spc-response-decision-trees.md`) — 2 Mermaid trees that **complement** PR #315's 7 *selection* trees rather than duplicate them: common-cause-vs-special-cause **response** (the anti-tampering gate, grounded in the WE/Nelson rules + Deming's funnel experiment) and capability-came-back-low (centering vs spread vs drift, with the stabilize-first guard).
- **Runnable calculator** `scripts/lss_calc.py` (stdlib only, Python 3.8+, ruff-clean) — four modes: `capability` (Cp/Cpk/Pp/Ppk + threshold bands + Cpk−Ppk drift gap), `sigma` (sigma level ↔ DPMO ↔ yield, printing **both** the long-term/1.5-shift and short-term conventions), `imr` (I-MR control-chart limits + a point-beyond-limit out-of-control scan), `copq` (Cost-of-Poor-Quality roll-up + recoverable-at-target). Formulas cited inline; an inverse-normal (Acklam) is implemented in stdlib to avoid a numpy/scipy dependency. Decision-support, not statistical certification — CIs/Gage R&R/significance route to `applied-statistics`. Verified against canonical values (DPMO 6210→4.0σ, DPMO 3.4→6.0σ long-term).
- **Commands/hooks gap filled** (the plugin previously had neither):
  - `commands/triage-capability-and-control.md` — the flagship `/process-improvement:triage-capability-and-control` command: control-then-capability triage (operational definition → chart selection → stability → capability → centering/spread/drift diagnosis → route inference to applied-statistics).
  - `hooks/flag-process-improvement-antipatterns.sh` + `hooks/hooks.json` — an advisory PostToolUse hook flagging capability-without-stability/spec context, sigma-without-shift-convention, solution-jumping, and a fix-without-a-control-plan. Advisory by default; `PROCESS_IMPROVEMENT_STRICT=1` makes it blocking. Proven against a known-bad fixture (3 findings, exit 2 under strict) and a known-good fixture (clean).
- **CLAUDE.md** — §5 knowledge bank gains the new tree; §7a scenarios bank flipped from TODO to enabled; new §7b (calculator), §11 (components/layout), §12 (Value-add completeness table), §13 (milestones); CGP §5 updated to reference the new tree/calculator/command/scenarios.

### Honestly N-A for a methodology vertical (documented, not forced)
The code-runtime tier (bundled/recommended MCP server, LSP, `bin/`, monitors, output-styles, themes, `settings.json`) is genuinely not applicable to a process-improvement advisory vertical — there is no code-aware backend or per-tenant API for the DMAIC/SPC/Lean craft to call, and the one live data need ("instrument a process so it can be measured") already routes to `data-platform`. Each is dispositioned with a one-line reason in `CLAUDE.md` §12. The runtime item with real value — a runnable calculator — **was** built. No MCP server was fabricated (per `docs/best-practices/bundled-mcp-servers.md`).

### Shared-file changes required (orchestrator-owned, NOT done here)
- `.claude-plugin/marketplace.json` `version` for `process-improvement` must bump `0.1.1` → `0.2.0` to mirror `plugin.json` (CI fails on drift). The catalog `description` may optionally be refreshed to match the new `plugin.json` description (kept < 1024 chars).
- `.repo-layout.json` `allowed_globs` already covers every new path (`plugins/*/scenarios/**`, `plugins/*/scripts/**`, `plugins/*/commands/**`, `plugins/*/hooks/**`, `plugins/*/CHANGELOG.md`, `plugins/*/knowledge/**`) — **no edit needed** (verified 2026-06-05).

## [0.1.1] — prior release

2 agents (`lean-six-sigma-blackbelt`, `process-analyst`), 6 skills, 5 templates, 21 best-practices, and a research-grounded knowledge bank (DMAIC/Lean toolkit, Six Sigma statistics & SPC, consolidated decision trees). A domain-neutral Lean Six Sigma process-improvement team. PR #315 consolidated the knowledge decision-trees, best-practices, and templates.
