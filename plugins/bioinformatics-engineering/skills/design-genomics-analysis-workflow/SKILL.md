---
name: design-genomics-analysis-workflow
description: From a scientific question, an assay, and a sample design, derive the concrete genomics analysis workflow — the per-sample step graph (QC, trimming, alignment, dedup, BQSR-or-not, variant calling or quantification), the cohort/joint step (joint genotyping or differential-expression model), the reference build and its matching accessory files, and the validation truth set — captured as an analysis plan. Reach for this when the user asks "design the WGS germline workflow", "what steps does this RNA-seq analysis need?", or "how do we structure the per-sample and cohort steps?". Used by `genomics-pipeline-engineer` and `bioinformatics-workflow-architect`.
---

# Skill: design-genomics-analysis-workflow

> **Invoked by:** `genomics-pipeline-engineer` (primary, to plan the build) and `bioinformatics-workflow-architect` (to shape the step graph before the engine is fixed).
>
> **When to invoke:** "Design the workflow for <assay>"; "what steps does this analysis need?"; "how do we structure per-sample vs cohort?"; any move from a scientific question to its concrete step graph.
>
> **Output:** the per-sample step graph + the cohort/joint step + the reference build & accessory files + the validation truth set, captured in the analysis plan spec.

## Procedure

1. **Name the question, the assay, and the sample design.** What biological question (variant discovery, differential expression, cell-type atlas)? Which assay (WGS / WES / somatic / RNA-seq / single-cell / long-read)? How many samples, what grouping (case/control, cohort, time-course)? The grouping decides whether there's a **cohort/joint** step.
2. **Fix the reference build + accessory files.** Name the build (GRCh38 analysis set vs T2T-CHM13) and pull its **matching** set: the FASTA + index + `.dict`, the known-sites/dbSNP for BQSR, the interval/capture BED, and the build-matched annotation (GTF/VEP cache). Record checksums — this is the coordinate contract.
3. **Lay out the per-sample step graph** (see [`../../knowledge/genomics-workflow-patterns-2026.md`](../../knowledge/genomics-workflow-patterns-2026.md)):
   - **DNA germline:** QC (FastQC/MultiQC) → trim → **BWA-MEM2** align → MarkDuplicates → BQSR? → **GATK HaplotypeCaller** (gVCF) or **DeepVariant**.
   - **RNA-seq:** QC → trim → **STAR** (align + count) or **Salmon** (quantify) → per-sample matrix.
   - **Single-cell:** QC → **Cell Ranger / STARsolo** → per-sample count matrix.
   Scatter over genomic intervals where the step allows.
4. **Add the cohort/joint step.** Germline → **joint genotyping** (GenomicsDBImport → GenotypeGVCFs) across the cohort, then filter (VQSR/hard). RNA-seq → the **DESeq2 / edgeR** differential-expression model on the count matrix. Single-cell → the **Scanpy / Seurat** integration + clustering. This is where cohort statistical power lives.
5. **Define QC gates + the validation truth set.** Set the QC signatures to gate on (mapping rate, dup rate, mito %, saturation for the assay), and pick the **GIAB sample + hap.py** concordance target for variant calling (or spike-in/marker sanity checks for RNA/single-cell).
6. **Name resources + block-vs-warn per step.** Which steps scatter, rough per-step CPU/RAM, and which QC failures **halt** the run vs merely **flag** (a failed FastQC on one sample shouldn't necessarily kill a 300-sample run).
7. **Capture it** in [`../../templates/analysis-plan-spec.md`](../../templates/analysis-plan-spec.md) so the step graph, reference, accessory files, QC gates, truth set, and owner live in one reviewable page — the contract the pipeline-engineer builds to.

## Worked example

> User: "Design the workflow for a 24-sample bulk RNA-seq case/control differential-expression study."

- **Question/assay/design:** differential expression, bulk RNA-seq, 24 samples in two groups (12 case / 12 control) → there **is** a cohort step (the DE model).
- **Reference:** GRCh38 primary assembly + a build-matched GTF for quantification; VEP not needed for DE.
- **Per-sample graph (quantification route, chosen for speed):** FastQC/MultiQC → fastp trim → **Salmon** selective-alignment quant against the transcriptome index → per-sample transcript quant.
- **Cohort step:** tximport → **DESeq2** (or edgeR) with the case/control design formula → differential-expression results + shrinkage + MA/volcano.
- **QC gates:** mapping/quant rate, rRNA %, library-complexity, and a PCA/clustering sanity check that samples group by condition, not by batch (flag a batch-effect confound before interpreting DE).
- **Validation:** no VCF truth set for RNA-seq → validate with ERCC spike-ins if present + known-marker sanity + the QC signatures; regression-check DESeq2 outputs against a prior run when the pipeline changes.
- **Resources/block-vs-warn:** Salmon steps scatter per sample (light CPU); a single-sample QC failure **flags** (drop or re-sequence that sample) rather than halting the study.
- **Captured** in the analysis plan spec, ready to implement.

## Guardrails

- Every step traces to the scientific question; a step with no analytical purpose is bloat.
- Fix the **reference build + matching accessory files** before laying out steps — the coordinate contract comes first.
- Separate **per-sample** from **cohort/joint** deliberately — joint genotyping / the DE model is where cohort power lives, and it's a different step.
- Pick the **validation truth set (GIAB/hap.py)** or the assay's QC signatures at design time, not after building.
- QC gates are **block-vs-warn per step** — don't let one bad sample halt a cohort, and don't let a batch confound through unflagged.
- BQSR-or-not, alignment-vs-quantification are deliberate choices — decide, don't cargo-cult a copied workflow.
- See the patterns reference for the canonical step orders and file-format contracts: [`../../knowledge/genomics-workflow-patterns-2026.md`](../../knowledge/genomics-workflow-patterns-2026.md).
