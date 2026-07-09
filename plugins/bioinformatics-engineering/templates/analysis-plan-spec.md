# Genomics analysis plan — <analysis-name>

> The one-page plan captured **before** implementing a pipeline. Pairs with
> [`pipeline-validation-report.md`](pipeline-validation-report.md) (how you prove it works).

**Owner:** <name / group> · **Date:** <YYYY-MM-DD> · **Engine:** <Nextflow/nf-core · Snakemake · WDL+Cromwell/miniwdl · CWL> · **Status:** draft / approved / built

## Question & sample design
- **Scientific question:** <variant discovery / differential expression / cell-type atlas / …>
- **Assay:** <WGS · WES · somatic · RNA-seq · single-cell · long-read>
- **Sample design:** <N samples · grouping (case/control · cohort · time-course) — decides whether there's a cohort/joint step>
- **Downstream consumers:** <stats / ML / clinical / report — who relies on the outputs>

## Reference (the coordinate contract)
- **Build:** <GRCh38 analysis set (ALT/decoy) · T2T-CHM13 — + WHY>
- **Accessory files (matching the build):** <FASTA + .fai + .dict · known-sites/dbSNP · interval/capture BED · annotation GTF / VEP cache>
- **Checksums recorded:** <yes/no — reference + accessory-file digests>
- **Build hazard note:** <never mix coordinates across builds; liftover is lossy>

## Per-sample step graph
| Step | Tool (pinned) | Scatter? | Resource (CPU/RAM/time) | QC / notes |
|---|---|---|---|---|
| QC | FastQC -> MultiQC | per-sample | <> | mapping rate, dup rate |
| Trim | fastp / Trimmomatic | per-sample | <> | skip if clean |
| Align | BWA-MEM2 / minimap2 / STAR / Salmon | per-sample | <> | DNA short / long / RNA |
| Dedup | MarkDuplicates | per-sample | <> | (DNA) |
| BQSR? | GATK BQSR | per-interval | <> | deliberate — decide, don't cargo-cult |
| Call / quantify | GATK HaplotypeCaller / DeepVariant / featureCounts | per-interval | <> | gVCF / counts |

## Cohort / joint step
- **Germline:** <joint genotyping — GenomicsDBImport -> GenotypeGVCFs -> filter (VQSR / hard)>
- **RNA-seq:** <DESeq2 / edgeR differential-expression model + design formula>
- **Single-cell:** <Scanpy / Seurat integration + clustering + annotation>
- **Why here:** <cohort statistical power lives in this step>

## QC gates (block vs flag)
- **Halt the run if:** <the QC failures that must stop the whole run>
- **Flag / drop the sample if:** <per-sample QC failures that shouldn't halt a cohort>
- **Batch/confound check:** <PCA/clustering by condition-not-batch, before interpreting results>

## Validation truth set
- **Variant calling:** <GIAB sample (e.g. HG002) + GA4GH hap.py concordance target — precision/recall/F1 by SNV/indel in confident regions>
- **RNA / single-cell:** <ERCC spike-ins · known-marker sanity · QC-signature check · regression vs prior run>

## Reproducibility approach
- **Containers:** <per-process Docker -> Apptainer/Singularity on HPC>
- **Env / lockfile:** <Conda/Bioconda + conda-lock · committed lockfile>
- **Pinning:** <every tool at an exact version — no `latest`>
- **Provenance:** <engine run report/trace · seeds · reference checksums · params file>

## Compute strategy
- **Where:** <HPC Slurm · cloud AWS Batch / Google Batch>
- **Spot placement:** <which fault-tolerant steps run on spot with retries; which stay on-demand>
- **Cost shape:** <rough runtime + $ estimate>

## Seams (not this team)
- **Model training / MLOps on outputs:** ml-engineering
- **Trial operations / regulatory:** clinical-trials
- **Warehouse / BI:** data-platform
- **Scheduling / DAG / backfill execution:** data-orchestration
- **Kubernetes / cloud account:** cloud-native-kubernetes / aws-cloud

## Open questions / risks
- <list>

**Sign-off:** <reviewer> · <date>
