# Changelog — process-improvement

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.3.0] — 2026-08-17

Gold-standard harden. Three real defects from a verified audit of the plugin (both agents already scored 28/30 on the repo's agent-quality-rubric, the advisory hook already fired correctly in both directions under stock bash 3.2, and `lss_calc.py` was already numerically correct on all four modes — so the finding was **missing measurement**, not broken behaviour).

### Added

- **Control-chart constants, §3a of [`knowledge/six-sigma-statistics-and-spc.md`](knowledge/six-sigma-statistics-and-spc.md).** §3 recommended Xbar-R / Xbar-S as the majority-case chart and then shipped no d2/A2/D3/D4 or c4/A3/B3/B4, so a reader who followed the recommendation could not actually draw the chart — the advice was aspirational rather than executable. Both tables now ship for n = 2–10, with the Xbar/R/S limit formulas, the `sigma-hat = R-bar/d2` link back to the Cp/Cpk section, and the I-MR n=2 derivation of the 2.66 and 3.267 the calculator hard-codes. **A wrong control-limit constant is worse than an absent one** — it moves the line a plant reacts to and looks exactly like a correct number — so the values were *recomputed*, not recalled: d2/d3 by numerical integration of the range distribution of n standard normals, c4 exactly from `sqrt(2/(n-1))·Γ(n/2)/Γ((n-1)/2)`. 17 of 18 rows reproduced the published ASTM E2587 / AIAG table to 3 decimals; the single difference (D4 at n=3) is the published tables' own rounding convention, and that convention is stated inline so a reader reconciling against Minitab/JMP is not left guessing.
- **Gate 218 — `scripts/check-lss-calc.py`.** `lss_calc.py` is the plugin's only executable and had **zero** CI coverage anywhere in the repo: no gate, no workflow, no test, while every number it prints (a capability index, a sigma level, a control limit, a COPQ recovery figure) goes straight into a tollgate deck. The gate drives all four advertised modes against hand-checkable values (3.4 DPMO → 6.00σ long-term / 4.50σ short-term; 5,7,5,7,5,7 → X-bar 6.0000, MR-bar 2.0000, I limits 6 ± 2.66×2; 120k+80k+40k COPQ = 240,000 = 4.80% of 5M), so a reviewer can audit the **expectation** and not merely re-run the implementation against itself. `--self-test` proves teeth on six real arithmetic mutants (both I-MR constants, an inverted Cpk, a wrong Cp denominator, a re-based 1.5σ shift, a dropped COPQ category) and asserts the unmutated control stays clean; `--must-fail` plants a wrong D4 and the gate asserts it fails **closed at exit 2**, not at a non-blocking 1.

### Fixed

- **Gate 30 now covers this plugin's hook.** `scripts/audit-gates.sh` Gate 30 proves both directions (fires on an anti-pattern, silent on a clean file) for eleven sibling plugins' advisory hooks and omitted `hooks/flag-process-improvement-antipatterns.sh` entirely — so the one hook this plugin ships was the one hook nothing measured. Added with the same fires/silent fixture pair the other eleven use.
- **The duplicated operational-definition rule is consolidated.** `best-practices/` shipped the same Measure-phase rule twice — `operational-definition-before-you-measure.md` and `operational-definition-of-the-metric.md`, the latter's own Provenance section conceding it "covers the same gate". Two files for one rule means a citation can name either, and a later edit fixes only one. The duplicate's genuinely unique material (the four-element fill-in template, the worked cycle-time example, the attribute-agreement caveat) was **merged into** the surviving canonical rule before deletion, so nothing was lost, and the one inbound cross-reference was repointed.
- **The best-practices index count is no longer stale.** `best-practices/README.md` advertised "17 rules" over a table of 21 rows. Now 20, matching both the table and the file count after the consolidation above.

## [0.2.2] — 2026-08-14

### Changed

- Dropped hand-maintained artifact-count literals from the plugin description (D1). The roster enumerates itself; Gate 206 forbids the digit.

## [0.2.1] — 2026-07-09

### Fixed

- **Advisory anti-pattern hook now fires under Claude Code.** `hooks/flag-process-improvement-antipatterns.sh` read the target path only from `$CLAUDE_TOOL_FILE_PATH` (`$1`) — not a real Claude Code hook variable — so under Claude Code it received an empty path and silently no-op'd. Added the canonical stdin-JSON `.tool_input.file_path` fallback so the hook inspects the written file as intended. Advisory-only (no gate/behavior change beyond the hook actually running now). From the 2026-07-09 autonomous repo review (Decision 1).

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
