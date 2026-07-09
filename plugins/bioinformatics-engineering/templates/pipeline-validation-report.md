# Pipeline validation report — <pipeline / analysis>

> How you PROVE a genomics pipeline is reproducible and accurate. Reached from an
> implemented pipeline built against
> [`analysis-plan-spec.md`](analysis-plan-spec.md). The rule: **a concordance
> number against a truth set, or it didn't happen** — never "looks fine."

**Report ID:** <YYYY-MM-DD-nn> · **Pipeline:** <name + version/commit> · **Engine:** <Nextflow x.y / Snakemake / WDL> · **Run by:** <name> · **Date:** <YYYY-MM-DD>

## 1. What was run
- **Assay + question:** <WGS/WES/RNA-seq/single-cell · the analytical question>
- **Reference build:** <GRCh38 analysis set · T2T-CHM13 — + accessory files>
- **Sample(s):** <real cohort and/or the GIAB benchmark sample (e.g. HG002)>
- **Engine + workflow version:** <engine version · pipeline commit SHA / nf-core release>

## 2. Reproducibility manifest
- **Containers (pinned digests):** <per-process image tags / digests>
- **Env / lockfile:** <Conda/Bioconda lockfile committed? path>
- **Tool versions (pinned):** <aligner · caller · GATK · … each at an exact version>
- **Reference + accessory checksums:** <FASTA / dbSNP / interval-BED digests>
- **Provenance captured:** <engine trace/report/timeline · seeds · params file — links>
- **Re-run determinism:** <does a re-run reproduce the prior outputs? yes/no + evidence>

## 3. Scaling & cost result
- **Parallelism:** <scatter/gather layout — per-sample + per-interval>
- **Resources (right-sized):** <per-step CPU/RAM from profiling>
- **Compute placement:** <HPC Slurm · cloud Batch — which steps on spot vs on-demand>
- **Runtime before/after:** <baseline vs optimized wall-clock>
- **Cost before/after:** <baseline vs optimized $ (spot savings)>

## 4. Accuracy validation (variant calling — GIAB / hap.py)
- **Truth set:** <GIAB sample + truth VCF version + confident-region BED>
- **Comparison tool:** <GA4GH hap.py version — haplotype-aware, confident regions only>

| Variant type | Precision | Recall | F1 | Target met? |
|---|---|---|---|---|
| SNV | <> | <> | <> | <yes/no> |
| INDEL | <> | <> | <> | <yes/no> |

- **Regions:** <confident regions only — comparison outside them is meaningless>
- **Notes:** <indel metrics are the harder, more diagnostic ones — call out weakness>

## 5. Accuracy validation (RNA-seq / single-cell — no VCF truth set)
- **QC signatures:** <mapping/quant rate · rRNA/mito % · saturation · library complexity>
- **Spike-ins / controls:** <ERCC · known markers — sanity checks>
- **Batch/confound check:** <PCA/clustering by condition, not batch>
- **Regression vs prior run:** <did outputs match the last-good run within tolerance?>

## 6. Regression gate
- **Gate outcome:** <PASS / FAIL — did concordance/QC meet the target before this pipeline is trusted?>
- **What changed since last-good:** <tool-version bump / parameter change — and its effect on the numbers>
- **Blocking issues:** <anything that must be fixed before production use>

## 7. Sign-off & seams
- **Reproducible + accurate for intended use:** <yes/no — one-line verdict>
- **Seams:** <downstream stats/ML -> ml-engineering · trial/regulatory -> clinical-trials · warehouse -> data-platform · scheduling -> data-orchestration>

**Signed off:** <reviewer> · <date>
