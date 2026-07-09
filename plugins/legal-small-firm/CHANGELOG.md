# Changelog — legal-small-firm

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.2.2] — 2026-07-09

### Fixed

- **Advisory anti-pattern hook now fires under Claude Code.** `hooks/flag-legal-small-firm-antipatterns.sh` read the target path only from `$CLAUDE_TOOL_FILE_PATH` (`$1`) — not a real Claude Code hook variable — so under Claude Code it received an empty path and silently no-op'd. Added the canonical stdin-JSON `.tool_input.file_path` fallback so the hook inspects the written file as intended. Advisory-only (no gate/behavior change beyond the hook actually running now). From the 2026-07-09 autonomous repo review (Decision 1).

## [0.2.1] — 2026-06-12

Version bump previously unlogged here; the change that set `0.2.1`:

- fix: repo-review fixes — gate tool-absence guard + broken antipattern regex (#422)

## [0.2.0] — 2026-06-05

Value-add build-out — the non-code-vertical recipe applied to small-firm legal practice management. Adds the scenarios bank, a net-new (complementary) Mermaid decision-tree knowledge file, a runnable practice-economics + trust-reconciliation calculator, and cited KPI benchmarks; honestly dispositions the code-runtime tier as N-A.

- **Scenarios bank** (`scenarios/`) — new directory + README + **4** dated, scope-tagged engagement scenarios (mirrors the marketplace 9-field schema, `product_version: "n/a"` for a non-code vertical): realization-rate recovery, intake conflict/fit miss, IOLTA three-way reconciliation gap, utilization/capacity squeeze. Each carries an "Action for the next consultant" lesson and cited public benchmarks; none contains client confidences or legal advice.
- **1 new Mermaid decision-tree knowledge file** that **complements** PR #315's consolidated `legal-practice-decision-trees.md` (it covers fee structure / A/R collection / billing-rate review) — **does not duplicate or contradict it**:
  - `legal-intake-and-trust-decision-trees.md` — two net-new upstream trees: **conflict-checked intake** (take/decline/escalate; conflict check on ALL parties first) and **IOLTA / trust-account handling** (the three-way reconciliation: bank = book = sum of client ledgers). ABA Model Rule 1.15/1.7/1.9 + Clio-cited; every state-specific rule marked `[verify-at-use]`.
- **Runnable calculator** `scripts/legal_calc.py` (stdlib only, Python 3.8+) — four modes: `realization` (the cascade: utilization/realization/collection + effective hourly rate), `matter-profit` (matter/attorney profitability vs the Rule of Thirds 3×-cost threshold), `utilization` (billable ratio + delegable-vs-attorney-only non-billable split), `trust-recon` (three-way IOLTA reconciliation check; exit 1 on FAIL). Decision-support, not legal/ethics/financial advice — a FAIL routes to the attorney, never a finding of misconduct. Ruff-clean, py_compile-clean.
- **KPI glossary enriched** (`knowledge/legal-practice-kpi-glossary.md`) — added cited, dated benchmark tables: the realization cascade (Clio 2025: util ~38% / real ~88% / coll ~93%), lockup days, revenue/lawyer (solo ~$83k / small ~$157k), the Rule of Thirds (comp/overhead/profit ≈ 1/3 each; ≥3× cost-of-employment threshold; overhead-runs-45–50% caveat), and the trust-accounting control. All Clio/LeanLaw/CARET/ABA-cited with retrieval dates and `[verify-at-use]` marks on volatile/state-specific facts.

### Honestly N-A for a non-code vertical (documented, not forced)
The code-runtime tier (code-aware MCP server, LSP, `bin/`, monitors, output-styles, themes, `settings.json`) is genuinely not applicable to a practice-operations advisory vertical. Each is dispositioned with a one-line reason in `CLAUDE.md` § "Value-add completeness (build-out 2026-06-05)". The one runtime item with real non-code value — a runnable calculator — **was** built (`scripts/legal_calc.py`).

### Shared-file changes required (orchestrator-owned, NOT done here)
- `.repo-layout.json` `allowed_globs` already covers `plugins/*/scenarios/**` and `plugins/*/scripts/**` (confirmed — no new globs needed).
- `.claude-plugin/marketplace.json` + `.claude-plugin/plugin.json` `version` bump `0.1.2` → `0.2.0` (both mirrors; not done here per constraints).

## [0.1.0] — initial release

4 agents (`legal-engagement-lead`, `litigation-specialist`, `contracts-drafting-specialist`, `legal-operations-analyst`), 5 skills, 3 templates, 5 commands, 1 advisory hook, an 8-rule best-practices set, and a 4-file research-grounded knowledge bank. A practice-operations team for a solo or small-firm attorney — matters on realization, drafting as attorney decision-support, conflict-checked intake, and the practice P&L.
