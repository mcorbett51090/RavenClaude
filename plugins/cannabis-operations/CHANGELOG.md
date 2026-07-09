# Changelog — cannabis-operations

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.3.2] — 2026-07-09

### Fixed

- **Advisory anti-pattern hook now fires under Claude Code.** `hooks/flag-cannabis-operations-antipatterns.sh` read the target path only from `$CLAUDE_TOOL_FILE_PATH` (`$1`) — not a real Claude Code hook variable — so under Claude Code it received an empty path and silently no-op'd. Added the canonical stdin-JSON `.tool_input.file_path` fallback so the hook inspects the written file as intended. Advisory-only (no gate/behavior change beyond the hook actually running now). From the 2026-07-09 autonomous repo review (Decision 1).

## [0.3.1] — 2026-06-12

Version bump previously unlogged here (rolls up `0.2.0` → `0.3.1`); the change that set `0.3.1`:

- fix: repo-review fixes — gate tool-absence guard + broken antipattern regex (#422)

## [0.2.0] — 2026-06-05

Value-add build-out — applying the marketplace non-code-vertical recipe (proven by `veterinary-practice`) to a **regulated seed-to-sale / track-and-trace / compliance / retail vertical**. Adds the scenarios bank, two Mermaid decision-tree knowledge files, a runnable operations calculator, and cited KPI benchmarks; honestly dispositions the code-runtime tier as N-A.

- **Scenarios bank** (`scenarios/`) — **4** dated, scope-tagged engagement scenarios authored to the README's pre-existing schema (mirrors the marketplace 9-field schema, `product_version: "n/a"` for a non-code vertical): Metrc reconciliation break, 280E COGS-allocation gap, dispensary margin discount spiral, failed-lab-test yield hit. Each carries an "Action for the next consultant" lesson and cited public benchmarks, and respects the `state-specific`-don't-generalize rule (§3 #3).
- **2 new Mermaid decision-tree knowledge files** (the plugin previously had zero):
  - `cannabis-track-and-trace-discrepancy-decision-tree.md` — physical-vs-system (Metrc/BioTrack/LeafData) discrepancy triage: posting-lag vs diversion vs surplus, direction-of-gap logic, escalate-shortage / don't-delete-surplus, daily-cadence fix. Metrc/CRB-Monitor/Flowhub/Distru-cited.
  - `cannabis-testing-remediation-decision-tree.md` — failed compliance test: the microbial-remediable vs pesticide/heavy-metal-destroy asymmetry, the remediation economic test (only where the state permits resale of remediated product), and the harvest→saleable-yield model. CDPHE / Medicinal Genomics / Frontiers-cited.
- **Runnable calculator** `scripts/cannabis_calc.py` (stdlib only, Python 3.8+) — three modes: `effective-280e` (effective federal rate vs defensible-COGS share + §471 cost-study tax delta; encodes the April-2026 partial-rescheduling caveat), `inventory-turns` (turns + days-on-hand/DIO + cash trapped vs target), `saleable-yield` (cause-tagged fail rate → saleable yield + microbial remediate-vs-destroy verdict). Decision-support, not advice.
- **KPI glossary rewritten** (`knowledge/cannabis-kpi-glossary.md`) — from a stub into cited, dated benchmark tables (compliance / retail / financial) plus a **rescheduling-context** section (April-2026 medical-only Schedule III move; adult-use still Schedule I and under 280E) and market context. All trade/regulator/analyst-cited with retrieval dates and `[verify-at-use]` markers.

### Volatile-fact note (read before quoting 280E relief)
The April-2026 DOJ/DEA order rescheduled only **FDA-approved** and **state-licensed *medical*** marijuana to Schedule III; **recreational/adult-use, unlicensed activity, and synthetic THC remained Schedule I**, with a broader hearing set for June 29, 2026. **280E still applies to state-licensed adult-use operators.** Every 280E/rescheduling claim is `[verify-at-use]` against the operator's exact segment and the current federal posture, with the operator's CPA (§2, §3 #3).

### Honestly N-A for a non-code vertical (documented, not forced)
The code-runtime tier (code-aware MCP server, LSP, `bin/`, monitors, output-styles, themes, `settings.json`) is genuinely not applicable to a compliance/retail-ops advisory vertical. Each is dispositioned with a one-line reason in `CLAUDE.md` §9 "Value-add completeness (build-out 2026-06-05)". A Metrc/BioTrack MCP is specifically **EVALUATE-FIRST, never bundle** (per-license/authenticated/regulated-data, write-capable) — not fabricated, none recommended this round. The one runtime item with real non-code value — a runnable calculator — **was** built (`scripts/cannabis_calc.py`).

### Shared-file changes required (orchestrator-owned, NOT done here)
- `.repo-layout.json` `allowed_globs` must cover `plugins/*/scenarios/**` and `plugins/*/scripts/**` (both already exist for other plugins; confirm coverage — no NEW top-level dir is introduced).
- `.claude-plugin/marketplace.json` + `.claude-plugin/plugin.json` `version` bump `0.1.0` → `0.2.0`.

## [0.1.0] — initial release

4 agents (`cannabis-engagement-lead`, `seed-to-sale-compliance-specialist`, `dispensary-retail-operations-specialist`, `cannabis-finance-analyst`), 5 skills, 3 templates, 5 commands, 1 advisory hook, an 8-rule best-practices set, and a 4-file research-grounded knowledge bank. A compliance-and-retail-operations team for a licensed cannabis operator.
