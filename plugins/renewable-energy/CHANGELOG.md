# Changelog — renewable-energy

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.2.0] — 2026-06-05

Value-add build-out for a **pure non-code vertical** — adds the scenarios bank, three new Mermaid decision-tree knowledge files (complementing PR #315's consolidated set), and a runnable project-economics calculator; honestly dispositions the code-runtime tier as N-A.

- **Scenarios bank** (`scenarios/`) — new directory + README + **5** dated, scope-tagged engagement scenarios (mirrors the marketplace 9-field schema, `product_version: "n/a"` for a non-code vertical): interconnection-queue upgrade shock, PPA-vs-merchant offtake, ITC-vs-PTC election, storage-add to capture curtailment, capacity-factor underperformance. Each carries an "Action for the next consultant" lesson and cited public benchmarks with retrieval dates.
- **3 new Mermaid decision-tree knowledge files** (complementing PR #315's feasibility-screen / IRR-below-hurdle / storage-dispatch-use-case trees):
  - `renewables-itc-vs-ptc-decision-tree.md` — ITC vs. PTC election, with the capacity-factor/CapEx crossover, bonus-adder layering, the load-bearing PV arithmetic, and the post-OBBBA begin-construction / placed-in-service eligibility window. ICF/Crux/IRS-cited.
  - `renewables-ppa-vs-merchant-decision-tree.md` — PPA vs. merchant vs. hybrid offtake as a financeability-before-price decision (the structure sets the cost of capital and leverage, which swamp the headline price). LevelTen/pv-tech-cited.
  - `renewables-add-storage-decision-tree.md` — add storage or not (the *whether*, before #315's dispatch-use-case *which*), with the net-of-round-trip-efficiency/degradation/ITC test. NREL/Crux/CAISO-cited.
- **Runnable calculator** `scripts/renewables_calc.py` (stdlib only, Python 3.8+, ruff-clean) — four modes: `lcoe` (levelized cost of energy), `capacity-factor` (annual energy → CF + decomposition reminder), `itc-vs-ptc` (mutually-exclusive election + verdict/margin), `simple-payback` (net-cost-after-incentives screen). Decision-support, not tax/legal/engineering/financial advice.

### Accuracy discipline
All volatile figures (LCOE ~$50/MWh modeled, capacity factor ~24% benchmark, solar PPA ~$61.67/MWh Q4 2025, ITC 30% base / PTC per-kWh, BESS ~$334/kWh 4-hour, round-trip efficiency 85–95%, degradation first-year step + ~0.5–0.7%/yr) were web-researched, dated, and `[verify-at-use]`-marked. Policy/incentive figures are flagged **jurisdiction- and year-specific** — the ITC/PTC eligibility window was materially reshaped by OBBBA (2025), and the binding tax determination is tax counsel's, not the team's.

### Honestly N-A for a non-code vertical (documented, not forced)
The code-runtime tier (code-aware MCP server, LSP, `bin/`, monitors, output-styles, themes, `settings.json`) is genuinely not applicable to a project-development advisory vertical. Each is dispositioned with a one-line reason in `CLAUDE.md` § "Value-add completeness (build-out 2026-06-05)". The one runtime item with real non-code value — a runnable calculator — **was** built (`scripts/renewables_calc.py`). Bundling an MCP is explicitly declined per `docs/best-practices/bundled-mcp-servers.md` (renewables live data is per-tenant/authenticated/paywalled; no first-party server is verified to exist).

### Shared-file changes (orchestrator-owned, NOT done here)
- `.repo-layout.json` `allowed_globs` already covers `plugins/*/scenarios/**` and `plugins/*/scripts/**` (confirmed — no new globs required).
- `.claude-plugin/marketplace.json` `version` bump `0.1.2` → `0.2.0` to mirror `.claude-plugin/plugin.json` (CI fails on drift).

## [0.1.x] — PR #315

Consolidated knowledge decision-trees (`renewables-decision-trees.md` gained the feasibility-screen, IRR-below-hurdle, and storage-dispatch-use-case Mermaid trees), added `best-practices/`, and a 4th template.

## [0.1.0] — initial release

4 agents (`renewables-engagement-lead`, `solar-project-developer`, `grid-interconnection-specialist`, `energy-finance-analyst`), 5 skills, 3 templates, 5 commands, 1 advisory hook, an 8-rule best-practices set, and a 4-file research-grounded knowledge bank. A project-development team for a solar/storage developer, EPC, or asset owner.
