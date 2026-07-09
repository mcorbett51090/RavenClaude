# bioinformatics-engineering

> The **genomics-pipeline-engineering layer** for Claude Code — the team that answers *"which workflow engine, reference, and compute, and how do we build a reproducible, validated genomics pipeline?"* and builds the pipelines that produce trustworthy variants, expression matrices, and cell atlases. Two agents: the **bioinformatics-workflow-architect** (chooses the engine + reference + tool chain + compute + reproducibility approach) and the **genomics-pipeline-engineer** (implements, scales, and validates the pipeline).

Part of the [RavenClaude](../../README.md) marketplace. Extends `ravenclaude-core`.

## What it does

| You ask | It returns |
|---|---|
| "Nextflow/nf-core, Snakemake, WDL+Cromwell, or CWL for our pipeline?" | A decision-tree-driven engine choice + why it fits the assay/team/scale + the conditions that would flip it |
| "GRCh38 or T2T-CHM13, and which aligner/variant-caller?" | A reference-build decision (with the coordinate-contract hazard named) + an aligner (BWA-MEM2/minimap2/STAR/Salmon) + variant-caller (GATK/DeepVariant) chain matched to the assay |
| "Design the WGS germline workflow." | A per-sample step graph (QC → align → dedup → BQSR? → call) + the cohort joint-genotyping step + the reference & accessory files + QC gates |
| "Build this pipeline in Nextflow and make it reproducible." | Per-step processes, per-process containers (Docker → Apptainer), pinned versions + a lockfile, and captured provenance |
| "This is too slow/expensive on 500 samples." | Scatter/gather parallelism, right-sized resources from profiling, spot on the fault-tolerant steps, and a runtime + cost before/after |
| "Prove our variant calls are accurate." | A GA4GH hap.py run against a GIAB truth set: precision/recall/F1 by variant type in the confident regions, plus the regressions it surfaces |

**Two rules it never breaks:** *the reference build is a coordinate contract* (the build + its matching accessory files are one set — never mix coordinates), and *benchmark against a truth set or don't claim accuracy* (a GIAB/hap.py concordance number, never "looks fine").

## What's inside

- **2 agents** — `bioinformatics-workflow-architect` (chooses engine + reference + tool chain + compute + reproducibility approach + validation truth set) and `genomics-pipeline-engineer` (implements the steps, containerizes/pins, scales with scatter/gather + spot, and validates against GIAB/hap.py).
- **3 skills** — `choose-bioinformatics-pipeline-and-stack`, `design-genomics-analysis-workflow`, `implement-and-scale-bioinformatics-pipeline`.
- **2 knowledge files** — a Mermaid bioinformatics-pipeline decision tree (engine + reference-build + compute sub-choices + trade-off tables) and a 2026 genomics-workflow-patterns reference (file-format contracts, germline/RNA-seq/single-cell step orders, reproducibility, scaling/cost, GIAB/hap.py validation, tooling map).
- **2 templates** — an analysis-plan spec and a pipeline-validation report.

## Where it sits in the genomics stack

```
bioinformatics-engineering (HERE)  →  build a REPRODUCIBLE, VALIDATED genomics pipeline  ("compute the right variants/expression")
ml-engineering          →  train / serve models on the outputs      ("model the biology, generically")
clinical-trials         →  trial operations / regulatory / protocol  ("are we ALLOWED to, and under what protocol")
data-platform           →  warehouse / BI the results land in        ("store & serve the numbers")
data-orchestration      →  schedule & run the pipelines              ("what runs it, when, safely")
```

This plugin is the **pipeline-engineering layer**: it chooses the engine/reference/compute and builds the reproducible, benchmarked pipeline. It stays clear of the *downstream modeling* (`ml-engineering`), the *trial/regulatory* work (`clinical-trials`), and the *warehouse/BI* the results land in (`data-platform`).

## Tooling stance

Concept-first (the scientific question drives the architecture; nf-core-before-bespoke; the reference-as-coordinate-contract; reproducibility designed in; scatter/gather scaling; truth-set validation), fluent across the workflow engines (**Nextflow/nf-core**, **Snakemake**, **WDL+Cromwell/miniwdl**, **CWL**), the aligners/callers (**BWA-MEM2, minimap2, STAR, Salmon, GATK best practices, DeepVariant**), RNA-seq/single-cell (**DESeq2/edgeR, Cell Ranger, Scanpy/Seurat**), containers (**Docker, Apptainer/Singularity, Bioconda**), and validation (**GIAB, GA4GH hap.py**). Tool versions, reference-build accessory files, and cloud pricing carry retrieval dates — re-verify before pinning in a client deliverable.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install bioinformatics-engineering@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.
