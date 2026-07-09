---
name: choose-bioinformatics-pipeline-and-stack
description: Pick the right genomics workflow engine, reference build, tool chain, compute strategy, and reproducibility approach for a described analysis by traversing the bioinformatics pipeline decision tree (assay/question → curated community pipeline exists? → portability/team fluency → HPC vs cloud → reference build), then return the recommended engine (Nextflow/nf-core / Snakemake / WDL+Cromwell / CWL), the reference (GRCh38 vs T2T-CHM13) with the build hazards, the aligner/variant-caller chain, the compute plan (Slurm vs cloud Batch/spot + cost shape), the reproducibility approach, the validation truth set, and the conditions that would flip the choice. Reach for this when the user asks "Nextflow vs Snakemake vs WDL?", "GRCh38 or T2T-CHM13?", "HPC or cloud for this pipeline?", or "how do we make this reproducible?". Used by `bioinformatics-workflow-architect` (primary).
---

# Skill: choose-bioinformatics-pipeline-and-stack

> **Invoked by:** `bioinformatics-workflow-architect` (primary). Also consulted by `genomics-pipeline-engineer` when a build reveals the chosen engine/reference can't express a required step.
>
> **When to invoke:** "Nextflow/nf-core vs Snakemake vs WDL vs CWL?"; "GRCh38 or T2T-CHM13?"; "HPC Slurm or cloud Batch for this?"; "how do we make this reproducible?"; any "what should we build this genomics analysis on?" question.
>
> **Output:** the recommended engine + reference build + tool chain + compute strategy + reproducibility approach + validation truth set + the 1-2 flip conditions that would change the answer.

## Procedure

1. **Restate the situation in the tree's terms.** Capture: the **scientific question** (variant discovery, differential expression, cell-type atlas), the **assay** (WGS / WES / somatic / RNA-seq / single-cell / long-read), the **sample scale**, the **team's fluency** (Nextflow / Python / WDL), and the **compute + budget** constraints (owned HPC vs cloud, cost sensitivity).
2. **Check for a curated community pipeline first.** If **nf-core** (sarek, rnaseq, scrnaseq) or an equivalent curated WDL/Snakemake workflow already covers the assay, adopting + configuring it usually beats hand-rolling — you inherit its tests, containers, and community review. Only go bespoke for what the community doesn't cover.
3. **Traverse the decision tree** in [`../../knowledge/bioinformatics-pipeline-decision-tree.md`](../../knowledge/bioinformatics-pipeline-decision-tree.md) against those inputs:
   - curated pipeline + Nextflow-fluent (or willing) → **Nextflow / nf-core**,
   - cloud/Terra-centric, want Broad GATK WDLs → **WDL + Cromwell / miniwdl**,
   - Python-native research lab, local rule reasoning → **Snakemake**,
   - vendor-neutral portability / a shared cross-institution spec → **CWL**,
   - scale + dataflow + resume in any language, no curated pipeline → **Nextflow**.
4. **Choose the reference build deliberately.** **GRCh38** analysis set (ALT/decoy) with its **matching** known-sites/interval files is the default; **T2T-CHM13** when previously-unmappable regions matter and the downstream tools support it. **Name the coordinate-contract hazard** — never mix builds/coordinates, and treat liftover as lossy.
5. **Match the tool chain to the assay.** DNA short read → **BWA-MEM2**; long read → **minimap2**; RNA-seq → **STAR** or **Salmon**; single-cell → **Cell Ranger / STARsolo**; variant calling → **GATK best practices** or **DeepVariant**; then dedup, BQSR-or-not, joint genotyping.
6. **Choose compute + cost shape.** HPC Slurm (owned, queue limits, Apptainer) vs cloud Batch (elastic, spot on the fault-tolerant steps). Name where spot is safe and give a rough cost/runtime shape — don't hand-wave "the cloud."
7. **Lock the reproducibility approach and pick the truth set.** Containers (Docker → Apptainer) + Conda/Bioconda + pinned versions + provenance + FAIR, and the **GIAB sample + hap.py** concordance target. **State the flip conditions** — the 1-2 facts that, if different, change the engine/reference call.

## Worked example

> User: "We have 300 WES samples, a germline rare-variant question, a Python-heavy team, and an owned Slurm cluster. Nextflow, Snakemake, or WDL? GRCh38 or T2T?"

- **Curated pipeline exists:** nf-core/**sarek** covers WES germline end-to-end. That's a strong pull toward **Nextflow** even for a Python team — you inherit sarek's tests, containers, and GATK-best-practices step order rather than re-deriving them in Snakemake.
- **Engine:** **Nextflow / nf-core sarek**, configured for WES (capture-kit interval BED). If the team refuses Groovy and the analysis were more bespoke, Snakemake would be the fallback — but not here, where a curated pipeline exists.
- **Reference:** **GRCh38** analysis set + the matching dbSNP/known-sites + the capture-kit interval BED. T2T-CHM13 isn't justified — the rare-variant question doesn't hinge on the newly-mappable regions, and annotation support is simpler on GRCh38.
- **Tool chain:** FastQC/MultiQC → fastp → **BWA-MEM2** → MarkDuplicates → BQSR → **GATK HaplotypeCaller** (gVCF, scattered over the capture intervals) → **joint genotyping** across the 300-sample cohort (this is where the rare-variant power comes from) → VQSR/hard-filter → VEP.
- **Compute:** the owned **Slurm** cluster, **Apptainer** images converted from sarek's Docker containers, scatter over capture intervals. No cloud spend needed at this scale.
- **Reproducibility:** sarek's pinned containers + a committed params file + Nextflow `-with-trace/-with-report` provenance; reference build + accessory-file checksums recorded.
- **Validation:** run sarek on a **GIAB** WES sample and **hap.py** it → precision/recall/F1 by SNV/indel in the confident regions before trusting the cohort calls.
- **Flip condition:** if they lose the Slurm cluster or the cohort grows past what the queue handles, revisit for **cloud Batch + spot**; if the question shifted to hard-to-map regions, revisit **T2T-CHM13**.

## Guardrails

- Never name an engine before traversing the tree — question + assay before brand.
- Prefer a **curated community pipeline (nf-core)** before hand-rolling; you inherit tests, containers, and review.
- The reference build is a **coordinate contract** — name the build + its matching accessory files, and never mix coordinates.
- Choose the **validation truth set (GIAB/hap.py)** up front, not after the pipeline is built.
- Spot instances are safe on fault-tolerant steps, a footgun on long single-shot ones — say which.
- Clinical-trial operations/regulatory are **not** pipeline choice — route to `clinical-trials`; generic model training → `ml-engineering`.
- Volatile claims (tool versions, accessory files, cloud pricing) carry a **retrieval date** and are re-verified before a commitment. See [`../../knowledge/genomics-workflow-patterns-2026.md`](../../knowledge/genomics-workflow-patterns-2026.md).
