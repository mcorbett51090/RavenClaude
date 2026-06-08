# Changelog — data-science-research

All notable changes to this plugin are documented here. Versioning is semver; the version in
`.claude-plugin/plugin.json` and the marketplace catalog entry are kept in lockstep (CI fails on drift).

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
