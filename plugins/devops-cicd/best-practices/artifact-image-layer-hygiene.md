# Keep container images small, layered cleanly, and non-root

**Status:** Absolute rule
**Domain:** Build / artifact engineering
**Applies to:** `devops-cicd`

---

## Why this exists

A bloated container image with build tools, package manager caches, and a root user is a CVE surface that takes longer to pull, scan, and start. Every unnecessary layer is a potential vulnerability, a wider blast radius if a container is compromised, and a slower cold-start for autoscaling. Small, clean, non-root images are cheaper to operate and harder to exploit.

## How to apply

Use multi-stage builds to produce a runtime image that contains only the compiled artifact and its runtime dependencies, not the build toolchain. Base the final stage on a minimal image (distroless, Alpine, or a slim variant). Run the process as a non-root user.

```dockerfile
# Multi-stage: builder stage has the toolchain, runtime stage has only the output
FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -trimpath -ldflags="-s -w" -o /app/server ./cmd/server

# Runtime stage: no Go toolchain, no build cache
FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=builder /app/server /server
USER nonroot:nonroot
EXPOSE 8080
ENTRYPOINT ["/server"]
```

**Do:**
- Use multi-stage builds: the final stage copies only the compiled binary / runtime artifacts.
- Pick the thinnest base that meets your runtime needs: distroless > Alpine > slim > full.
- Run as a non-root user (`USER nonroot` or `USER 65534`).
- Order `COPY` and `RUN` layers so dependencies (rarely-changing) precede source code (frequently-changing) — maximizes layer cache hits.
- Use `.dockerignore` to exclude `.git`, `node_modules`, test fixtures, and local config from the build context.

**Don't:**
- Install development or debug tools in the runtime stage (`curl`, `vim`, `wget`).
- Leave package manager caches in a layer (`apt-get install` without `rm -rf /var/lib/apt/lists/*`).
- Run the application as root inside the container.
- Use `latest` as the base image tag in a production Dockerfile.

## Edge cases / when the rule does NOT apply

Ephemeral CI builder images (not shipped to production) can keep build tools and run as root. Debug sidecars for incident investigation are intentionally tool-rich; constrain their use to break-glass scenarios, not normal operation.

## See also

- [`../agents/build-and-artifact-engineer.md`](../agents/build-and-artifact-engineer.md) — owns container image hygiene and layer optimization.
- [`./artifact-sign-every-release.md`](./artifact-sign-every-release.md) — a clean, minimal image is worth signing; a bloated one is harder to attest.

## Provenance

Codifies Docker multi-stage build best practices (docs.docker.com), Google's distroless project guidance, and CIS Docker Benchmark recommendations for non-root runtime processes.

---

_Last reviewed: 2026-06-05 by `claude`_
