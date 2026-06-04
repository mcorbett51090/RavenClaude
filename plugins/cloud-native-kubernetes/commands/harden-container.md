---
description: "Produce a small, non-root, distroless, digest-pinned container with dropped caps and read-only root FS."
argument-hint: "[image/Dockerfile + how it runs]"
---

You are running `/cloud-native-kubernetes:harden-container`. Use `container-build-engineer` + the `container-hardening-k8s` skill.

## Steps
1. Multi-stage build into a distroless/minimal runtime; non-root UID; digest-pinned base.
2. Drop capabilities; read-only root FS.
3. Route SBOM/provenance to devops-cicd, residual CVEs to security-engineering.
4. Emit the Dockerfile + securityContext + Structured Output block.
