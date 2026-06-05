# Changelog — applied-statistics

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.6.0] — 2026-06-05

Value-add build-out for a **methodology / analytical vertical** ("is this difference/trend REAL?"). Adds the scenarios bank, one net-new Mermaid decision tree complementing the consolidated trees from PR #315, and a stdlib statistics calculator; honestly dispositions the code-runtime tier as N-A.

- **Scenarios bank** (`scenarios/`) — new directory + README + **4** dated, scope-tagged methodology-engagement scenarios (mirrors the marketplace 9-field schema, `product_version: "n/a"` for a non-code vertical):
  - `2026-06-05-segment-false-discovery-scare.md` — "we sliced it and 3 segments came back significant" → multiple-comparisons artifact; BH-FDR correction wiped them out.
  - `2026-06-05-underpowered-no-significant-difference.md` — "p > 0.05 so no effect" → underpowered null; report CI + MDE, not "no effect."
  - `2026-06-05-simpsons-paradox-conversion-reversal.md` — aggregate channel ranking reverses within device subgroups (confounding); standardize the mix.
  - `2026-06-05-ab-peeking-early-stop.md` — fixed-horizon test stopped at first p < 0.05 (peeking); directional only — seam handed to `experimentation-growth-engineering` for the sequential harness.
  - The `applied-statistician` agent gained the **scenario-retrieval inline prior**; the §8b "TODO (planned)" placeholder in `CLAUDE.md` is retired.
- **1 new Mermaid decision-tree knowledge file** — `knowledge/multiplicity-correction-decision-tree.md`: running >1 test, which correction? FWER (Bonferroni / Holm) vs FDR (Benjamini-Hochberg / Benjamini-Yekutieli), the family-wise false-positive arithmetic `1-(1-α)^m`, and the confirmatory-after-exploratory two-step. Complements (does not duplicate) the **already-present** parametric-vs-nonparametric / test-selection / regression / causal / time-series / A/B / sample-size / missing-data trees in `stats-test-selection-decision-trees.md` (PR #315). Holm 1979 / BH 1995 / BY 2001 cited.
- **Runnable calculator** `scripts/stat_calc.py` (stdlib only, Python 3.8+ — normal quantile/CDF via Acklam's rational approximation, so **no scipy/statsmodels dependency**) — four modes:
  - `samplesize` — two-proportion z-test (`--baseline`/`--mde`) or two-mean Cohen's-d (`--d`) n per group, with the Cohen's-h readout. Pooled-variance form (MetricGate/NCSS); the mean mode's z-approximation is flagged anticonservative vs exact noncentral-t.
  - `correct` — Bonferroni / Holm (step-down) / Benjamini-Hochberg (step-up) / Benjamini-Yekutieli adjusted p-values + the false-positive arithmetic + per-method reject/keep verdict.
  - `effectsize` — Cohen's d (two means) or Cohen's h (two proportions) with the small/medium/large benchmarks.
  - `ci` — Wilson (default) or Wald single-proportion confidence interval — the uncertainty band for the data-platform statistical-qa seam.
  - Ruff-clean (`python3 -m ruff check`), every formula cited in the docstring, and **verified against statsmodels / R reference values** (two-proportion n ≈ 8,158; Cohen's-d n=63/group at d=0.5; BH q-values; Wilson CI [0.0684, 0.1028] for 84/1000).

### Honestly N-A for an analytical vertical (documented, not forced)
The code-runtime tier (bundled MCP server, LSP, `bin/`, monitors, output-styles, themes, `settings.json`) is genuinely not applicable: the client's data and analysis runtime live outside the repo, and the agent is advisory (it emits snippets the consultant runs locally). Each is dispositioned with a one-line reason in `CLAUDE.md` §12 "Value-add completeness (build-out 2026-06-05)". The one runtime item with real value — a runnable calculator — **was** built (`scripts/stat_calc.py`). No MCP server was fabricated.

### Shared-file changes required (orchestrator-owned, NOT done in this build)
- `.repo-layout.json` `allowed_globs` — `plugins/*/scenarios/**`, `plugins/*/scripts/**`, `plugins/*/knowledge/**`, and `plugins/*/CHANGELOG.md` **already exist**; the new files match existing globs, so **no new glob is required**. (Confirmed against `.repo-layout.json` at build time.)
- `.claude-plugin/marketplace.json` — the catalog `version` + `description` for `applied-statistics` must be bumped `0.5.2` → `0.6.0` to mirror `plugin.json` (CI `validate-marketplace` fails on drift). **Not applied in this build** (marketplace.json edits were out of scope for the build session); the exact 1001-char description to mirror is in `plugin.json`.

## [0.5.2] and earlier

1 specialist agent (`applied-statistician`), 5 skills, 4 templates, 9 commands, 1 advisory anti-pattern hook, and a research-grounded knowledge bank (test-selection decision tree, consolidated method-selection trees, statistical pitfalls, experiment design & A/B testing, 2026 tooling tiers, causal-inference primer) plus a best-practices set. Answers "is this difference/trend/relationship statistically REAL?" for SMB consulting; seams with `data-platform` ("is the number correct?" vs "is it real?").
