---
description: "Make the build artifact trustworthy: reproducible, minimal, non-root, with an SBOM and SLSA provenance."
argument-hint: "[build/Dockerfile description]"
---

You are running `/devops-cicd:harden-artifact`. Use `build-and-artifact-engineer` + the `supply-chain-integrity` skill.

## Steps
1. Pin base images by digest; remove build-time nondeterminism.
2. Convert to multi-stage, minimal/distroless, non-root (pattern in `templates/dockerfile-hardened.md`).
3. Add build-time SBOM (CycloneDX/SPDX) + SLSA provenance + signing.
4. Add scan-on-push and a registry retention policy.
5. Route any CVE/finding verdict to security-engineering -> security-reviewer.
6. Emit the hardened build + the Structured Output block.
