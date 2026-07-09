# Knowledge — Genomics workflow patterns (2026)

> **Last reviewed:** 2026-07-09 · **Confidence:** High on the durable concepts (the file-format contracts, the germline best-practices step order, test-vs-monitor of reproducibility, benchmark-against-truth-set, scatter/gather scaling); **Medium on the dated tooling map — tool versions, reference builds, and cloud pricing are volatile and carry retrieval dates below.**
> The reference the `genomics-pipeline-engineer` reads when building and operating a pipeline: the file-format contracts, the core step sequences (WGS/WES germline, RNA-seq, single-cell), reproducibility patterns, scaling/cost patterns, validation against truth sets, and a 2026 tooling snapshot.

The team's discipline: **implement one process per step, pin + containerize every tool, scale with scatter/gather, and prove accuracy against a GIAB/hap.py truth set before claiming it.**

---

## File-format contracts (the coordinate + payload plumbing)

| Format | Carries | Watch out for |
|---|---|---|
| **FASTA** | Reference sequence (the genome/transcriptome) | Must be indexed (`.fai`, plus a `.dict`); the build here is the coordinate contract for everything downstream |
| **FASTQ** | Raw reads + per-base quality | Phred encoding, paired-end R1/R2 pairing, adapter contamination |
| **SAM / BAM / CRAM** | Aligned reads | **CRAM is reference-anchored** — you need the exact reference to read it; BAM is self-contained but larger; keep the index (`.bai`/`.crai`) |
| **VCF / gVCF** | Variants (gVCF = per-site records incl. non-variant blocks, for joint genotyping) | Must be bgzipped + tabix-indexed; the contig list must match the reference build |
| **BED** | Genomic intervals (0-based, half-open) | Off-by-one vs 1-based formats; capture-kit / confident-region files live here |
| **GFF / GTF** | Gene/feature annotation | Build-specific; a GTF for the wrong build silently mis-annotates |

**The cross-cutting rule:** the **reference build is a coordinate contract**. Every BAM/CRAM, VCF, BED, and GTF is only meaningful against the *same* build + its matching accessory files. Mixing builds is the #1 silent corruption.

---

## Core step sequence — WGS/WES germline (GATK best-practices shape)

1. **QC the reads** — FastQC per sample, aggregated with **MultiQC**. Gate on obvious failures before spending compute.
2. **Trim/adapter-remove** (when needed) — fastp / Trimmomatic; skip if the data is already clean.
3. **Align** — **BWA-MEM2** for DNA short reads (or **minimap2** for long reads); output sorted BAM/CRAM.
4. **Mark duplicates** — Picard/GATK MarkDuplicates (PCR/optical duplicates).
5. **BQSR (or not)** — base-quality-score recalibration with the **matching** known-sites; increasingly skipped for some modern callers — decide deliberately, don't cargo-cult.
6. **Call variants (per sample)** — **GATK HaplotypeCaller** in gVCF mode, or **DeepVariant** (CNN-based, strong on some assays). Scatter over intervals.
7. **Joint genotyping (cohort)** — GenomicsDBImport → GenotypeGVCFs across the cohort; gather the scattered intervals. This is where a cohort's rare variants gain power.
8. **Filter** — VQSR or hard filters / DeepVariant's own filtering.
9. **Annotate** — VEP / SnpEff (build-matched), then hand off downstream.

> RNA-seq and single-cell diverge after QC — see below.

---

## Core step sequence — RNA-seq & single-cell

- **Bulk RNA-seq (alignment route):** QC → trim → **STAR** (spliced alignment) → feature counting (featureCounts / HTSeq) → **DESeq2 / edgeR** for differential expression.
- **Bulk RNA-seq (quantification route):** QC → **Salmon** (selective-alignment/pseudo-alignment, fast, transcript-level) → tximport → **DESeq2 / edgeR**. Prefer this when transcript-level quant is enough and speed matters.
- **Single-cell (10x):** **Cell Ranger** (or STARsolo / Alevin-fry) for the count matrix → **Scanpy** (Python) or **Seurat** (R) for QC (mito %, doublets), normalization, clustering, and annotation.
- **QC signatures to sanity-check:** RNA-seq — mapping rate, rRNA/mito %, library complexity, gene-body coverage. Single-cell — reads/cell, genes/cell, mito %, saturation. A pipeline with green steps but bad QC signatures is a bad result.

---

## Reproducibility patterns (designed in, never bolted on)

- **Pin every tool to an exact version** — no `latest`, no floating Conda solves at runtime. Commit a **lockfile**.
- **One container per process** — Docker in dev; convert to **Apptainer/Singularity** (rootless) for HPC. The container *is* the environment; the host node is not.
- **Conda/Bioconda when a container is overkill** — but lock it (`conda-lock` / explicit spec) so the solve is deterministic.
- **Capture provenance** — the engine's run report/trace (Nextflow `-with-trace`/`-with-report`, Snakemake report), random seeds, the reference build + accessory-file **checksums**, and the params file. A result you can't re-derive is an anecdote.
- **FAIR the outputs** — Findable, Accessible, Interoperable, Reusable: stable identifiers, standard formats, and the metadata to interpret them.

Reproducibility is the genomics analogue of test-vs-monitor: **the pinned environment is your known-good, the provenance trace is how you prove a rerun matches it.**

---

## Scaling & cost patterns

- **Scatter/gather is the primary lever.** Scatter per-sample *and* per genomic interval for alignment/calling; gather at joint-genotyping. This is what turns a week into a night.
- **Right-size from real profiling, not guesses.** Over-requesting RAM burns budget and queue priority; under-requesting kills the job at hour nine. Profile a representative sample, then set per-step resource labels.
- **Spot/preemptible for the fault-tolerant steps.** Short, checkpointable, retryable steps (alignment shards, per-interval calling) run cheaply on spot with retries; keep **long single-shot** steps (a big joint-genotype gather) on-demand. Spot reclaim mid-step must cost a retry, not the run.
- **Mind storage + egress.** Genomics data is huge; CRAM over BAM, delete intermediates, keep data close to compute. Cloud **egress** is a silent line-item.
- **Resume/caching.** Use the engine's resume (`-resume`) so a failed run restarts from the last good step, not from FASTQ.

---

## Validation against a truth set (the currency of trust)

- **Benchmark variant calls against GIAB.** The **Genome in a Bottle** samples (e.g. HG001–HG007) ship a **truth VCF + confident-region BED**. Run your pipeline on the sample and compare.
- **Use GA4GH `hap.py`** for concordance: it does haplotype-aware comparison and reports **precision / recall / F1 by variant type (SNV vs indel)** *within the confident regions only* (comparing outside them is meaningless).
- **Read the numbers by type.** Indel recall/precision is the harder, more diagnostic metric; a pipeline can look great on SNVs and be weak on indels.
- **Regression-gate on it.** A truth-set concordance run is how you catch that a tool-version bump or a parameter change silently degraded calls — the genomics equivalent of a monitor.
- **RNA-seq/single-cell** lack a single VCF truth set — validate with the expected QC signatures, spike-ins/ERCC where available, and known-marker sanity checks.

---

## 2026 tooling map (dated — volatile, re-verify before quoting)

- **Workflow engines:** Nextflow + **nf-core** (sarek/rnaseq/scrnaseq curated pipelines), Snakemake, WDL + Cromwell/miniwdl, CWL. _(Retrieved 2026-07-09.)_
- **QC / trim:** FastQC, **MultiQC** (aggregation), fastp / Trimmomatic. _(Retrieved 2026-07-09.)_
- **Alignment:** **BWA-MEM2** (DNA short read), **minimap2** (long read / spliced), **STAR** (RNA-seq), **Salmon** (RNA-seq quantification), Cell Ranger / STARsolo / Alevin-fry (single-cell). _(Retrieved 2026-07-09.)_
- **Variant calling:** **GATK** best practices (HaplotypeCaller, GenomicsDBImport, GenotypeGVCFs, VQSR), **DeepVariant** (CNN). _(Retrieved 2026-07-09.)_
- **Downstream stats:** **DESeq2 / edgeR** (differential expression), **Scanpy / Seurat** (single-cell). _(Retrieved 2026-07-09.)_
- **Annotation:** VEP, SnpEff (build-matched). _(Retrieved 2026-07-09.)_
- **Validation:** **GIAB** truth sets, **GA4GH hap.py** concordance. _(Retrieved 2026-07-09.)_
- **Containers:** Docker (dev), **Apptainer/Singularity** (HPC), Bioconda/Conda (`conda-lock`). _(Retrieved 2026-07-09.)_
- **References:** GRCh38 analysis set (ALT/decoy), **T2T-CHM13** (coordinate/annotation caveats). Tool versions, accessory files, and pricing **vary and change** — treat as a 2026-07 snapshot and re-verify with `ravenclaude-core/deep-researcher` before a client commitment.

---

## Provenance

- Durable concepts (file-format contracts + coordinate-contract hazard, the GATK best-practices germline step order, RNA-seq alignment-vs-quant routes, reproducibility via pinned containers + provenance, scatter/gather scaling, GIAB/hap.py truth-set validation) are consensus practice across the genomics community, reviewed 2026-07-09 — **High confidence**.
- The tooling map is a **2026-07 snapshot**; tool versions, reference builds, and cloud pricing are volatile and carry the retrieval dates above — re-verify before pinning in a deliverable.
