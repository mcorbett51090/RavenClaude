# Changelog — architecture-aec

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.2.1] — 2026-06-12

Version bump previously unlogged here; the change that set `0.2.1`:

- fix: repo-review fixes — gate tool-absence guard + broken antipattern regex (#422)

## [0.2.0] — 2026-06-05

Value-add build-out for a **non-code (AEC) vertical** — adds the scenarios bank, a new Mermaid delivery-method + estimate-class decision-tree knowledge file, and a runnable project-economics calculator; honestly dispositions the code-runtime tier as N-A. Complements the consolidated knowledge decision-trees, best-practices, and templates already present (PR #315).

- **Scenarios bank** (`scenarios/`) — new directory + README + **4** dated, scope-tagged engagement scenarios (mirrors the marketplace 9-field schema, `product_version: "n/a"` for a non-code vertical): RFI/submittal backlog → schedule slip, change-order creep → margin erosion, design-coordination clash → rework, delivery-method (CMAR/DB/DBB) selection. Each carries an "Action for the next consultant" lesson and cited public benchmarks.
- **1 new Mermaid decision-tree knowledge file** (`knowledge/aec-delivery-and-estimate-decision-tree.md`) complementing the consolidated trees in `aec-decision-trees.md`: **Tree A** routes project-delivery-method selection (Design-Bid-Build vs Design-Build vs CMAR) from the owner's risk-allocation priorities; **Tree B** gates a cost number on its AACE estimate class (5→1) and class-sized contingency before it drives a decision. Mastt/Terrapin/UNLV/AACE-cited with retrieval dates.
- **Runnable calculator** `scripts/aec_calc.py` (stdlib only, Python 3.8+) — three modes: `evm` (earned-value CPI/SPI/EAC project health + the CPI<0.90-by-20% fee-recovery trigger), `change-order` (CO % of contract against the ~5-15% bands + margin erosion from absorbed/unbilled work), `chargeable-area` (gross↔usable efficiency/loss-factor translation for a fee or test-fit). Decision-support, not licensed advice; ruff-clean.

### Honestly N-A for a non-code vertical (documented, not forced)
The code-runtime tier (code-aware MCP server, LSP, `bin/`, monitors, output-styles, themes, `settings.json`) is genuinely not applicable to a practice-and-project advisory vertical. Each is dispositioned with a one-line reason in `CLAUDE.md` § "Value-add completeness (build-out 2026-06-05)". The one runtime item with real non-code value — a runnable calculator — **was** built (`scripts/aec_calc.py`). BIM/PM live-data tools (Revit, Procore, Autodesk Construction Cloud) are per-tenant/authenticated and out of scope to bundle.

### Shared-file changes required (orchestrator-owned, NOT done here)
- `.repo-layout.json` `allowed_globs` already covers `plugins/*/scenarios/**`, `plugins/*/scripts/**`, and `plugins/*/knowledge/**` — confirm coverage; no edit needed.
- `.claude-plugin/marketplace.json` + `.claude-plugin/plugin.json` `version` bump `0.1.2` → `0.2.0`.

## [0.1.0] — initial release

4 agents (`aec-engagement-lead`, `design-architect`, `construction-documents-specialist`, `aec-project-analyst`), 5 skills, 3 templates, 5 commands, 1 advisory hook, an 8-rule best-practices set, and a research-grounded knowledge bank (KPI glossary, practice economics, practice context, consolidated decision trees). A practice-and-project team for an architect or small AEC firm.
