# Changelog — data-science-research

All notable changes to this plugin are documented here. Versioning is semver; the version in
`.claude-plugin/plugin.json` and the marketplace catalog entry are kept in lockstep (CI fails on drift).

## 0.2.0 — 2026-06-08

Value-add build-out — deepened the plugin to the v0.2.0 standard. No agent/skill/command/template count change;
the additions are knowledge, scenarios, and a runnable tool.

- **Best-practices: 8 → 12** — added `split-before-you-touch-the-data`, `the-metric-must-match-the-decision`,
  `understand-missingness-before-imputing`, and `generate-hypotheses-dont-decide-significance`
  (the latter keeps the significance/inference seam pointing at `applied-statistics`).
- **Decision trees: → 5 Mermaid trees** in `knowledge/data-science-research-decision-trees.md`.
- **Scenarios bank: 2 → 5 field notes** — added `accuracy-lied-on-imbalanced-fraud` (metric choice),
  `mean-imputation-erased-the-signal` (missingness), and `deep-net-that-couldnt-beat-the-mean` (baseline-first).
  All `reviewed: false`, 9-field schema; `scenarios/README.md` index updated.
- **Runnable calculator** — `scripts/ds_calc.py` (stdlib only, Python 3.8+ — no numpy/pandas/scikit-learn).
  Three subcommands: `classification-metrics` (precision/recall/F1/accuracy from a confusion matrix, with an
  imbalance warning), `regression-metrics` (MAE/RMSE/R2 from paired y_true/y_pred, with a mean-baseline RMSE
  comparison), and `split-check` (train/val/test ratio sanity + class-balance / minority-count warnings).
  Each subcommand carries the house reminder it enforces (cross-validate; baseline first; split before you touch
  the data). ruff-clean (`F,E9,B,C4,I,UP`); `py_compile`-clean.

## 0.1.0 — 2026-06-08

Initial release. The exploratory-data-science & reproducible-research layer between the data layer and the
decision/production layers.

- **3 agents** — `exploratory-data-scientist` (data profiling/cleaning, EDA, hypothesis generation, visualization,
  communicating findings with uncertainty), `feature-and-modeling-engineer` (feature engineering, classical modeling —
  regression / trees / gradient boosting — model selection, leakage-safe cross-validation, metric choice), and
  `research-reproducibility-engineer` (notebook hygiene, pinned environments, seeds, data/version control, experiment
  tracking, reproducible pipelines). Each carries the full scenario-authoring frontmatter.
- **3 skills** — `eda-workflow`, `feature-engineering-and-modeling`, `reproducible-research`.
- **Knowledge bank** — `data-science-research-decision-trees.md`: Mermaid trees (EDA-before-modeling sequence,
  classical-model selection, leakage-safe evaluation / cross-validation) + a dated 2026 tooling map
  (pandas / scikit-learn / XGBoost / LightGBM / MLflow / DVC) (`[verify-at-build]`).
- **8 best-practices**, **3 commands** (`profile-and-explore`, `build-baseline-model`, `make-reproducible`),
  **2 templates** (EDA report, model-experiment record), **1 advisory hook**
  (`check-data-science-research-anti-patterns.sh`; `DS_STRICT=1` to make it blocking), and a **scenarios bank** (2 field notes).
- Seams: is-the-result-statistically-real → `applied-statistics`; productionize/serve/monitor → `ml-engineering`;
  data pipelines/warehouse → `data-platform`; PII/consent → `data-governance-privacy`. Requires `ravenclaude-core@>=0.7.0`.
