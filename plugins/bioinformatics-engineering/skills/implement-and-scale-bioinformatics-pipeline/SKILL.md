---
name: implement-and-scale-bioinformatics-pipeline
description: Implement a designed genomics workflow in the chosen engine, containerize and pin every tool for reproducibility, scale it with scatter/gather on HPC Slurm or cloud Batch (spot on the fault-tolerant steps), and validate it against a GIAB/GA4GH hap.py truth set — then produce a pipeline-validation report. Reach for this when the user asks "build this pipeline in Nextflow/Snakemake/WDL", "containerize and pin it for reproducibility", "scale/cost-optimize this on Slurm or cloud", or "benchmark our variant calls against GIAB". Used by `genomics-pipeline-engineer` (primary).
---

# Skill: implement-and-scale-bioinformatics-pipeline

> **Invoked by:** `genomics-pipeline-engineer` (primary). Also consulted by `bioinformatics-workflow-architect` to confirm the chosen engine/compute can actually run the workflow before finalizing the architecture.
>
> **When to invoke:** "Build the pipeline in <engine>"; "containerize + pin it"; "scale / cost-optimize on Slurm or cloud"; "benchmark against GIAB/hap.py"; any move from a designed workflow to a running, reproducible, validated pipeline.
>
> **Output:** the implemented workflow (per-step processes, containers, resource labels, params/config), the reproducibility manifest (pinned versions + lockfile + provenance), the scaling/cost plan, and a truth-set concordance report captured in the validation-report template.

## Procedure

1. **Start from the analysis plan.** Take the step graph, reference build, accessory files, and truth set from [`design-genomics-analysis-workflow`](../design-genomics-analysis-workflow/SKILL.md) / [`../../templates/analysis-plan-spec.md`](../../templates/analysis-plan-spec.md). Don't implement against a vague ask — an unspecified step graph produces an unmaintainable pipeline.
2. **Implement one process per step.** Each step (QC, trim, align, dedup, BQSR, call, joint-genotype / quantify) is a discrete process/rule with its own **pinned container**, a **resource label** (CPU/RAM/time), and typed inputs/outputs. Never a mega-script — the process graph is the unit of resume and reuse. Add a **MultiQC** roll-up at the end.
3. **Containerize + pin for reproducibility.** Per-process containers (Docker in dev → **Apptainer/Singularity** on HPC) or locked Conda/Bioconda envs; every tool at an **exact version**; commit the **lockfile** and a params file. Record the reference build + accessory-file **checksums**. Capture provenance (engine `-with-trace/-with-report` / Snakemake report, seeds).
4. **Scale with scatter/gather + right-sized resources.** Scatter per-sample and per genomic interval for alignment/calling; gather at joint-genotyping. Right-size resources from **profiling a representative sample**, not guesses. Use the engine's **resume** so a failure restarts from the last good step.
5. **Cost-optimize the compute placement.** On cloud, put the **short, fault-tolerant, checkpointed** steps on **spot/preemptible** with retries; keep **long single-shot** steps (a big joint-genotype gather) on-demand. Prefer CRAM over BAM, delete intermediates, keep data close to compute (watch egress). Record a **before/after runtime + cost**.
6. **Validate against the truth set.** For variant calling, run **GA4GH hap.py** against the **GIAB** truth VCF + confident-region BED and report **precision / recall / F1 by variant type (SNV/indel)** *in the confident regions*. For RNA/single-cell, check the expected QC signatures + spike-ins/markers. Regression-gate: a tool-version bump that degrades concordance must fail here, not in production.
7. **Capture it** in [`../../templates/pipeline-validation-report.md`](../../templates/pipeline-validation-report.md) — the engine/version, the pinned environment, the scaling/cost result, and the concordance numbers in one auditable page.

## Worked example

> User: "Build the WGS germline pipeline we designed in Nextflow, make it reproducible, run it on AWS Batch cheaply, and prove it works."

- **Implement:** DSL2 processes — `fastqc` → `multiqc`, `fastp`, `bwamem2_align`, `markduplicates`, `bqsr`, `haplotypecaller` (scattered over interval BED, gVCF), `genomicsdb_import` + `genotypegvcfs` (gather), `vqsr`, `vep`. Each with a pinned container and a `resourceLabel`.
- **Reproducibility:** each process pins its Biocontainer to an exact tag; a `nextflow.config` with a params file; `-with-report -with-trace -with-timeline` for provenance; reference (GRCh38 analysis set) + dbSNP checksums recorded; the container digests committed.
- **Scale on AWS Batch:** the AWS Batch executor; **scatter** HaplotypeCaller over ~can-be-many interval shards; the alignment shards + per-interval calling run on **spot** with `errorStrategy 'retry'` (reclaim = a cheap retry); the single-shot joint-genotype gather runs **on-demand**. CRAM output, intermediates cleaned. Before/after: record the spot-vs-on-demand cost delta.
- **Validate:** run the pipeline on **GIAB HG002**, then `hap.py calls.vcf.gz` against the HG002 truth VCF + confident BED → report SNV and **indel** precision/recall/F1 in the confident regions. Gate the pipeline on meeting the target before it's trusted for real samples.
- **Report:** all of it in the pipeline-validation report — engine version, pinned digests, scatter config, spot/cost result, and the hap.py concordance table.

## Guardrails

- Implement against a **captured analysis plan**, never a vague ask.
- **One process per step, one pinned container per process** — mega-scripts kill resume, reuse, and reproducibility.
- **Pin every version + commit a lockfile + record reference checksums** — a floating solve or a `latest` tag is a non-reproducible result.
- Scatter/gather + **right-size from profiling** is the primary scaling lever, not bigger nodes.
- **Spot only on fault-tolerant, retryable steps**; keep long single-shot steps on-demand.
- **Validate against GIAB/hap.py before claiming accuracy** — report precision/recall/F1 by variant type in the confident regions, never "looks fine."
- Never mix reference builds/coordinates — the build + its matching accessory files are one set.
- Volatile facts (tool versions, GIAB truth-set versions, cloud pricing) carry a **retrieval date**; re-verify before shipping. See [`../../knowledge/genomics-workflow-patterns-2026.md`](../../knowledge/genomics-workflow-patterns-2026.md).
