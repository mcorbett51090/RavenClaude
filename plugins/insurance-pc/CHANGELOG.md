# Changelog — insurance-pc

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.2.0] — 2026-06-05

Value-add build-out — extends the P&C plugin to the marketplace value-add menu for a **non-code vertical** (underwriting, rating, claims, reserving, distribution), mirroring the merged `veterinary-practice` recipe. Adds a scenarios bank, two new topic-specific Mermaid decision-tree knowledge files (complementing the consolidated `pc-decision-trees.md` from PR #315), a runnable underwriting calculator, and a cited/dated KPI-glossary enrichment; honestly dispositions the code-runtime tier as N-A.

- **Scenarios bank** (`scenarios/`) — new directory + README + **4** dated, scope-tagged engagement scenarios (mirrors the marketplace 9-field schema, `product_version: "n/a"` for a non-code vertical): combined-ratio deterioration diagnosis, underwriting line-of-business mix correction, claims cycle-time & LAE reduction, renewal-retention leak. Each carries an "Action for the next consultant" lesson and cited public benchmarks (III/Triple-I, CAS, NAIC, Bain, agency-survey sources).
- **2 new Mermaid decision-tree knowledge files** (complement, do not duplicate, PR #315's `pc-decision-trees.md`):
  - `pc-reserving-method-decision-tree.md` — which loss-reserving method per cohort (chain ladder vs Bornhuetter-Ferguson vs expected-loss-ratio), the maturity/a-priori/process-change gates, the paid-vs-incurred cross-check, and the case/IBNR/ultimate components. CAS-cited.
  - `pc-claims-leakage-and-lae-decision-tree.md` — controlling leakage, LAE (DCC vs AO), and cycle time without squeezing valid indemnity; the frequency-vs-severity gate and the controllable-metric set. CAS/Huggins/Founder-Shield-cited.
- **Runnable calculator** `scripts/pc_calc.py` (stdlib only, Python 3.8+; `ruff`-clean, `py_compile`-clean, executable) — four modes: `combined-ratio` (loss/expense + attritional/cat split + margin), `rate-indication` (loss-ratio-method indicated change with optional credibility weighting), `loss-ratio` (frequency vs severity decomposition of a loss-ratio move), `reserve-runoff` (prior-year adverse/favorable development). Decision-support for a credentialed actuary, not a filed rate (§2).
- **KPI glossary enriched** (`knowledge/pc-kpi-glossary.md`) — replaced the thin stub with cited, dated benchmark tables (industry & by-line combined ratios 2025, cat load, LAE/DCC/AO, PLR & rate-indication formulas, retention/persistency benchmarks) plus a US state/NAIC regulatory-context section. All sourced with retrieval dates and `[verify-at-use]` marks on volatile facts.

### Honestly N-A for a non-code vertical (documented, not forced)
The code-runtime tier (code-aware MCP server, LSP, `bin/`, monitors, output-styles, themes, `settings.json`) is genuinely not applicable to an underwriting-and-claims advisory vertical. Each is dispositioned with a one-line reason in `CLAUDE.md` § "Value-add completeness (build-out 2026-06-05)". The one runtime item with real non-code value — a runnable calculator — **was** built (`scripts/pc_calc.py`).

### Shared-file changes required (orchestrator-owned, NOT done in this build-out)
- `.claude-plugin/marketplace.json` + `.claude-plugin/plugin.json` `version` bump `0.1.2` → `0.2.0` (CI fails on drift).
- `.repo-layout.json` `allowed_globs` already covers `plugins/*/scenarios/**` and `plugins/*/scripts/**` — no new globs needed.

## [0.1.0] — initial release

4 agents (`underwriting-lead`, `pc-underwriter`, `claims-specialist`, `actuarial-pricing-analyst`), 5 skills, 3 templates, 5 commands, 1 advisory hook, an 8-rule best-practices set, and a research-grounded knowledge bank. An underwriting-and-claims team for a P&C carrier, MGA, or agency analyst.
