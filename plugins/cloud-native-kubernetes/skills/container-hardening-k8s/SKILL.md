---
name: container-hardening-k8s
description: "Build a small, safe container for Kubernetes: multi-stage with a distroless/minimal base, non-root UID, digest-pinned base, dropped Linux capabilities, and a read-only root filesystem."
---

# Container Hardening (k8s)

## Build
Multi-stage: build in one stage, copy the artifact into a **distroless/minimal** runtime. No compiler/shell in runtime.

## Run safely
- **non-root** UID
- **drop** all Linux capabilities (add back only what's needed)
- **read-only** root filesystem
- base pinned by **digest**

## Why
Every package is a CVE + attack surface. Distroless quiets most scans by construction. Read-only FS + dropped caps shrink blast radius cheaply. Route the residual CVE verdict to `security-engineering`.
