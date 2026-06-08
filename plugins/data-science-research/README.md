# Data Science Research

The **data-science-research** plugin — the exploratory-data-science and reproducible-research craft: the analysis layer *between* raw data and a defensible result. It profiles and cleans data, explores it, engineers features and fits classical models, evaluates them honestly (cross-validation, the right metric, no leakage), and makes the whole thing reproducible — distinct from the data pipeline, the significance call, and production serving.

## Agents

- **`exploratory-data-scientist`** — The first look: data profiling (shape, types, missingness, cardinality, distributions), cleaning decisions, visualization, leakage-candidate and target-definition checks, hypothesis generation, and communicating findings *with* their uncertainty. Produces the descriptive picture, not the significance verdict.
- **`feature-and-modeling-engineer`** — Features and classical models: feature engineering (leakage-aware), a baseline to clear, regression / trees / gradient boosting, model selection, a leakage-safe cross-validation harness, and the metric chosen from the decision. Owns the honest score, not the productionizing.
- **`research-reproducibility-engineer`** — The reproducibility spine: notebook hygiene, pinned environments, seeds, data/version control, experiment tracking, and converting a run-once notebook into a scripted, re-runnable pipeline. Makes "it works on my machine" into "it works on anyone's."

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install data-science-research@ravenclaude
```

## Seams

- **Is the effect statistically real (p-values, confidence intervals, power, multiple comparisons)** → `applied-statistics`; this team generates the hypothesis and the descriptive picture, they rule on significance.
- **Serving, monitoring, retraining, the production feature store** → `ml-engineering`; we build and evaluate the model, they productionize it.
- **The data pipeline, ingestion, the warehouse table the analysis reads** → `data-platform`; we read the table, they build and fix the pipeline that produces it.
- **PII, consent, row-level access in the dataset** → `data-governance-privacy` + `ravenclaude-core/security-reviewer`; we defer to their policy before touching sensitive columns.
- **The narrative polish of a written-up finding** → `technical-writing-docs`; we produce the analysis, they polish the report.

Inherits `ravenclaude-core` protocols (Capability Grounding + Structured Output). Requires `ravenclaude-core@>=0.7.0`. Designed to be installed alongside `applied-statistics`, `ml-engineering`, and `data-platform`.
