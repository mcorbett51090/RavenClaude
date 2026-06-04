---
name: supply-chain-integrity
description: "Produce trustworthy artifacts: reproducible/deterministic builds, minimal non-root container images, SemVer + immutable digests, build-time SBOM (CycloneDX/SPDX), and SLSA provenance + signing for verifiable supply-chain integrity."
---

# Supply-Chain Integrity (build side)

**Purpose:** make the artifact verifiable end-to-end.

## Reproducible builds
Pin base images by **digest**, lock dependencies, remove build-time nondeterminism (timestamps, network). Same inputs -> same bytes.

## Minimal image
Multi-stage, distroless/minimal base, **non-root**, no toolchain in the runtime layer.

## SBOM & provenance
- Generate an **SBOM** at build (CycloneDX/SPDX) and attach it — you can't patch a CVE in a dep you can't enumerate.
- Attest **SLSA provenance** and sign. `security-engineering` judges the findings; you produce the evidence.

## Versioning
SemVer + immutable **digest**. `latest` is a human pointer, not a contract.
