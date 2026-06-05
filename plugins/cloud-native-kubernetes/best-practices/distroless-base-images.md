# Use distroless or minimal base images to reduce CVE surface

**Status:** Pattern
**Domain:** Kubernetes / container build
**Applies to:** `cloud-native-kubernetes`

---

## Why this exists

A standard OS-based image (`ubuntu:22.04`, `debian:bookworm`) ships with hundreds of packages — a shell, package manager, libc, coreutils — that the application never uses. Each package is a potential CVE. A distroless image contains only the application runtime and its direct dependencies: no shell, no package manager, no cron, no unnecessary kernel interfaces. This dramatically reduces the CVE scan noise and eliminates entire attack vectors (shell injection, `apt` exploitation). The house opinion states: "distroless/non-root, no shell — quiets CVE scans."

## How to apply

Multi-stage build pattern: build in a rich image, copy the binary into a distroless final stage:

```dockerfile
# Stage 1: build (full OS toolchain)
FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -trimpath -o /app/server ./cmd/server

# Stage 2: minimal runtime (distroless nonroot)
FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=builder /app/server /server
USER nonroot:nonroot
EXPOSE 8080
ENTRYPOINT ["/server"]
```

For Python workloads:
```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --target /app/deps -r requirements.txt
COPY . .

FROM gcr.io/distroless/python3-debian12:nonroot
COPY --from=builder /app/deps /app/deps
COPY --from=builder /app/src /app/src
ENV PYTHONPATH=/app/deps
USER nonroot:nonroot
ENTRYPOINT ["python3", "/app/src/main.py"]
```

**Distroless image selection:**

| Runtime | Image |
|---|---|
| Go static binary | `gcr.io/distroless/static-debian12:nonroot` |
| Go with glibc | `gcr.io/distroless/base-debian12:nonroot` |
| Python | `gcr.io/distroless/python3-debian12:nonroot` |
| Java | `gcr.io/distroless/java21-debian12:nonroot` |
| Node.js | `gcr.io/distroless/nodejs20-debian12:nonroot` |

**Do:**
- Use the `:nonroot` tag variant — the image runs as a non-root user by default.
- Pin to a specific Debian release (e.g., `debian12`) rather than `latest`.
- Use `gcr.io/distroless/static` for Go binaries compiled with `CGO_ENABLED=0` — static binaries need nothing except the OS syscall layer.
- Scan with Trivy or Grype after switching to distroless — confirm CVE count drops.

**Don't:**
- Use distroless for debugging with `kubectl exec` — there is no shell to exec into. Use an ephemeral debug container (`kubectl debug -it`) with a separate debug image when needed.
- Use distroless if the application requires a shell at startup (init scripts, entrypoint shell) — fix the entrypoint to be a binary.
- Use `ubuntu:latest` as a "baseline" for production images — trim to `slim` at a minimum, distroless where possible.

## Edge cases / when the rule does NOT apply

- **Tooling containers** (init containers running migration scripts): these may legitimately need a shell and a package manager — use `alpine` or `debian:slim` and keep them separate from the application container.
- **Applications requiring `libc` plugins** not packaged in distroless: evaluate `base-debian12` which includes libc but not the full OS; fall back to `alpine` before `ubuntu`.

## See also

- [`../agents/container-build-engineer.md`](../agents/container-build-engineer.md) — owns container image craft and CVE surface reduction.
- [`./pin-everything.md`](./pin-everything.md) — pin the base image digest as well as the tag.

## Provenance

Codifies the `container-build-engineer` remit from `CLAUDE.md` §1: "distroless/non-root, image size and CVE surface reduction" and the capability map entry: "Distroless / minimal base images — mature, non-root, no shell; quiets CVE scans." Standard container hardening pattern from the CNCF and Google's distroless documentation.

---

_Last reviewed: 2026-06-05 by `claude`_
